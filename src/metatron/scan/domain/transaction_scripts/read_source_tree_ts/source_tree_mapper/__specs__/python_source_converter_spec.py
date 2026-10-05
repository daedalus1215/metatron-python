from textwrap import dedent

import pytest

from metatron.scan.domain.transaction_scripts.read_source_tree_ts.source_text_projection import (
    SourceTextProjection,
)
from metatron.scan.domain.transaction_scripts.read_source_tree_ts.source_tree_mapper.parsed_source_projection import (  # noqa: E501
    ImportStatementProjection,
)
from metatron.scan.domain.transaction_scripts.read_source_tree_ts.source_tree_mapper.python_source_converter import (  # noqa: E501
    PythonSourceConverter,
)


def source(text):
    return SourceTextProjection(path="notes/domain/note_service.py", text=dedent(text))


@pytest.fixture
def target():
    return PythonSourceConverter()


class GivenPythonSourceConverter:
    class WhenAFileImportsInEveryShape:
        def then_each_imported_module_is_one_statement_in_line_order(self, target):
            # Arrange
            text = """\
                import os, app.notes.x as x
                from typing import TYPE_CHECKING
                from . import sibling
                from ..infrastructure.repositories import note_repository

                if TYPE_CHECKING:
                    from app.users.domain.ports import users_port

                def late():
                    from app.tags import tag_service
            """

            # Act
            result = target.apply(source(text))

            # Assert
            assert result.error is None
            assert result.imports == (
                ImportStatementProjection("os", (), 0, 1),
                ImportStatementProjection("app.notes.x", (), 0, 1),
                ImportStatementProjection("typing", ("TYPE_CHECKING",), 0, 2),
                ImportStatementProjection("", ("sibling",), 1, 3),
                ImportStatementProjection(
                    "infrastructure.repositories", ("note_repository",), 2, 4
                ),
                ImportStatementProjection("app.users.domain.ports", ("users_port",), 0, 7),
                ImportStatementProjection("app.tags", ("tag_service",), 0, 10),
            )

    class WhenAFileDoesNotParse:
        def then_it_returns_the_error_and_its_line_with_no_imports(self, target):
            # Arrange
            text = "import os\ndef broken(:\n"

            # Act
            result = target.apply(source(text))

            # Assert
            assert result.imports == ()
            assert result.error_line == 2
            assert result.error

    class WhenAFileHoldsANullByte:
        def then_it_is_reported_rather_than_raised(self, target):
            # Act
            result = target.apply(source("x = 1\x00\n"))

            # Assert
            assert result.imports == ()
            assert result.error


class GivenImportStatementProjection:
    class WhenWritingItBack:
        @pytest.mark.parametrize(
            ("statement", "written"),
            [
                (ImportStatementProjection("a.b", (), 0, 1), "import a.b"),
                (ImportStatementProjection("a", ("b", "c"), 0, 1), "from a import b, c"),
                (ImportStatementProjection("", ("b",), 2, 1), "from .. import b"),
                (ImportStatementProjection("x", ("b",), 1, 1), "from .x import b"),
            ],
        )
        def then_it_reads_as_it_was_written(self, statement, written):
            # Act & Assert
            assert statement.written == written
