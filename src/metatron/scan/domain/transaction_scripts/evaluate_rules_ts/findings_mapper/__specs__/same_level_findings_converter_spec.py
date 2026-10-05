import pytest

from metatron.scan.domain.transaction_scripts.evaluate_rules_ts.findings_mapper.same_level_findings_converter import (  # noqa: E501
    SameLevelFindingsConverter,
)
from metatron.scan.test_utils import create_mock_arch_config, create_mock_source_tree
from metatron.shared.domain.ports.model_port import InstanceProjection

CONFIG = create_mock_arch_config()
TS = "notes/domain/transaction_scripts"
FILES = {
    f"{TS}/create_note_ts/create_note_transaction_script.py": "transaction-script",
    f"{TS}/delete_note_ts/delete_note_transaction_script.py": "transaction-script",
    "notes/domain/services/note_service.py": "service",
    "notes/domain/services/note_helper_service.py": "service",
    "notes/domain/note_action.py": "action",
    "notes/domain/other_action.py": "action",
}


@pytest.fixture
def target():
    return SameLevelFindingsConverter()


class GivenSameLevelFindingsConverter:
    class WhenATransactionScriptImportsOneInASiblingDirectory:
        def then_it_is_a_same_level_import(self, target):
            # Arrange
            edge = (
                f"{TS}/create_note_ts/create_note_transaction_script.py",
                f"{TS}/delete_note_ts/delete_note_transaction_script.py",
            )
            tree = create_mock_source_tree(FILES, [edge])

            # Act
            result = target.apply(CONFIG, tree)

            # Assert
            assert (result[0].id, result[0].tone, result[0].title) == (
                "no-same-level",
                "warn",
                "1 same-level import",
            )
            assert result[0].instances == (InstanceProjection(*edge),)

    class WhenTwoServicesInOneDirectoryImportEachOther:
        def then_it_is_a_helper_split_and_only_mentioned(self, target):
            # Arrange
            tree = create_mock_source_tree(
                FILES,
                [
                    (
                        "notes/domain/services/note_service.py",
                        "notes/domain/services/note_helper_service.py",
                    )
                ],
            )

            # Act
            result = target.apply(CONFIG, tree)

            # Assert
            assert result[0].tone == "good"
            assert result[0].instances == ()
            assert "1 same-pattern import inside one directory" in result[0].detail

    class WhenThePatternIsNotListed:
        def then_its_imports_are_not_checked(self, target):
            # Arrange
            tree = create_mock_source_tree(
                FILES, [("notes/domain/note_action.py", "notes/domain/other_action.py")]
            )

            # Act
            result = target.apply(CONFIG, tree)

            # Assert
            assert result[0].tone == "good"
            assert result[0].items == ()
