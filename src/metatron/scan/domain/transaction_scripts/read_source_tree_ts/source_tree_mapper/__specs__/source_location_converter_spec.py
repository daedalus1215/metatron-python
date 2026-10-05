import pytest

from metatron.scan.domain.transaction_scripts.read_source_tree_ts.source_tree_mapper.source_location_converter import (  # noqa: E501
    SourceLocationConverter,
)
from metatron.scan.domain.transaction_scripts.read_source_tree_ts.source_tree_mapper.source_location_projection import (  # noqa: E501
    SourceLocationProjection,
)


@pytest.fixture
def target():
    return SourceLocationConverter()


class GivenSourceLocationConverter:
    @pytest.mark.parametrize(
        ("path", "module", "folder"),
        [
            ("main.py", "(root)", "(root)"),
            ("notes/notes_module.py", "notes", "notes/(root)"),
            ("notes/domain/note_entity.py", "notes", "notes/domain"),
            ("notes/domain/services/note_service.py", "notes", "notes/domain/services"),
            (
                "notes/domain/transaction_scripts/a_ts/a.py",
                "notes",
                "notes/domain/transaction_scripts",
            ),
        ],
    )
    def then_it_names_the_module_and_the_folder(self, target, path, module, folder):
        # Act
        result = target.apply(path)

        # Assert
        assert result == SourceLocationProjection(module=module, folder=folder)
