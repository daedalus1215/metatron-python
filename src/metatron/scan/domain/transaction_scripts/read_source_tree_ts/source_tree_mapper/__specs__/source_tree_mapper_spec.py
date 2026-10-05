"""The mapper over its real converters: they are pure, so the pipeline is tested whole."""

from textwrap import dedent

import pytest

from metatron.scan.domain.transaction_scripts.read_source_tree_ts.source_text_projection import (
    SourceTextProjection,
)
from metatron.scan.domain.transaction_scripts.read_source_tree_ts.source_tree_mapper.coverage_converter import (  # noqa: E501
    CoverageConverter,
)
from metatron.scan.domain.transaction_scripts.read_source_tree_ts.source_tree_mapper.file_classification_converter import (  # noqa: E501
    FileClassificationConverter,
)
from metatron.scan.domain.transaction_scripts.read_source_tree_ts.source_tree_mapper.import_resolution_converter import (  # noqa: E501
    ImportResolutionConverter,
)
from metatron.scan.domain.transaction_scripts.read_source_tree_ts.source_tree_mapper.module_prefix_converter import (  # noqa: E501
    ModulePrefixConverter,
)
from metatron.scan.domain.transaction_scripts.read_source_tree_ts.source_tree_mapper.python_source_converter import (  # noqa: E501
    PythonSourceConverter,
)
from metatron.scan.domain.transaction_scripts.read_source_tree_ts.source_tree_mapper.source_location_converter import (  # noqa: E501
    SourceLocationConverter,
)
from metatron.scan.domain.transaction_scripts.read_source_tree_ts.source_tree_mapper.source_tree_mapper import (  # noqa: E501
    SourceTreeMapper,
)
from metatron.scan.test_utils import create_mock_arch_config
from metatron.shared.domain.ports.model_port import DiagnosticProjection, ImportEdgeProjection

LOCAL = frozenset({"app"})
SOURCES = {
    "__init__.py": "",
    "notes/__init__.py": "",
    "notes/application/create_note_action.py": """\
        from app.notes.domain.note_service import NoteService
        from app.notes.domain import note_service
        from fastapi import APIRouter
    """,
    "notes/domain/__init__.py": "",
    "notes/domain/note_service.py": """\
        from typing import TYPE_CHECKING
        from .create_note_transaction_script import CreateNoteTS

        if TYPE_CHECKING:
            from app.shared.users_port import UsersPort

        def late():
            from ..infrastructure.note_repository import NoteRepository
    """,
    "notes/domain/create_note_transaction_script.py": "from app.missing import nothing\n",
    "notes/infrastructure/note_repository.py": "import sqlalchemy\nimport sqlalchemy.orm\n",
    "shared/users_port.py": "class UsersPort: ...\n",
    "shared/broken.py": "def broken(:\n",
}


def sources():
    return tuple(
        SourceTextProjection(path=path, text=dedent(text)) for path, text in sorted(SOURCES.items())
    )


@pytest.fixture
def target():
    return SourceTreeMapper(
        PythonSourceConverter(),
        ModulePrefixConverter(),
        ImportResolutionConverter(),
        FileClassificationConverter(),
        SourceLocationConverter(),
        CoverageConverter(),
    )


class GivenSourceTreeMapper:
    class WhenMappingATreeWithEveryImportShape:
        def then_each_local_import_is_one_edge_with_its_first_line(self, target):
            # Act
            result = target.apply(sources(), create_mock_arch_config(), LOCAL)

            # Assert
            assert result.edges == (
                ImportEdgeProjection(
                    "notes/application/create_note_action.py", "notes/domain/note_service.py", 1
                ),
                ImportEdgeProjection(
                    "notes/domain/note_service.py",
                    "notes/domain/create_note_transaction_script.py",
                    2,
                ),
                ImportEdgeProjection("notes/domain/note_service.py", "shared/users_port.py", 5),
                ImportEdgeProjection(
                    "notes/domain/note_service.py", "notes/infrastructure/note_repository.py", 8
                ),
            )

        def then_externals_are_counted_by_their_head(self, target):
            # Act
            result = target.apply(sources(), create_mock_arch_config(), LOCAL)

            # Assert
            assert result.externals == {"fastapi": 1, "sqlalchemy": 2, "typing": 1}

        def then_what_it_could_not_read_is_a_diagnostic(self, target):
            # Act
            result = target.apply(sources(), create_mock_arch_config(), LOCAL)

            # Assert
            assert [(d.kind, d.file, d.line) for d in result.diagnostics] == [
                ("import-unresolved", "notes/domain/create_note_transaction_script.py", 1),
                ("parse-failed", "shared/broken.py", 1),
            ]
            assert result.diagnostics[0] == DiagnosticProjection(
                kind="import-unresolved",
                file="notes/domain/create_note_transaction_script.py",
                line=1,
                detail="'from app.missing import nothing' names no file in the scanned tree",
            )

        def then_every_file_is_classified_and_located(self, target):
            # Act
            result = target.apply(sources(), create_mock_arch_config(), LOCAL)

            # Assert
            service = next(f for f in result.files if f.path == "notes/domain/note_service.py")
            assert (service.module, service.folder, service.pattern, service.loc) == (
                "notes",
                "notes/domain",
                "service",
                8,
            )
            assert result.coverage.unclassified == ("shared/broken.py",)
