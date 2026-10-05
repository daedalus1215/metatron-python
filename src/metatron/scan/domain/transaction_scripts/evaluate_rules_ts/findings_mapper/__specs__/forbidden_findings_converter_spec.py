import pytest

from metatron.scan.domain.transaction_scripts.evaluate_rules_ts.findings_mapper.forbidden_findings_converter import (  # noqa: E501
    ForbiddenFindingsConverter,
)
from metatron.scan.test_utils import create_mock_arch_config, create_mock_source_tree
from metatron.shared.domain.ports.config_port import ForbiddenProjection
from metatron.shared.domain.ports.model_port import InstanceProjection

CONFIG = create_mock_arch_config(
    forbidden=(
        ForbiddenProjection("transaction-script", "service", "a TS calls upward into a Service"),
        ForbiddenProjection("converter", "repository", "a Converter is pure"),
    )
)
FILES = {
    "notes/note_service.py": "service",
    "notes/create_note_transaction_script.py": "transaction-script",
    "notes/note_converter.py": "converter",
    "notes/note_repository.py": "repository",
}


@pytest.fixture
def target():
    return ForbiddenFindingsConverter()


class GivenForbiddenFindingsConverter:
    class WhenATransactionScriptImportsAService:
        def then_it_is_one_upward_call_saying_why(self, target):
            # Arrange
            tree = create_mock_source_tree(
                FILES, [("notes/create_note_transaction_script.py", "notes/note_service.py")]
            )

            # Act
            result = target.apply(CONFIG, tree)

            # Assert
            assert len(result) == 1
            assert (result[0].id, result[0].tone, result[0].title) == (
                "no-upward",
                "warn",
                "1 upward call",
            )
            assert result[0].items == (
                "a TS calls upward into a Service: "
                "notes/create_note_transaction_script.py -> notes/note_service.py",
            )
            assert result[0].instances == (
                InstanceProjection(
                    "notes/create_note_transaction_script.py", "notes/note_service.py"
                ),
            )

    class WhenEveryImportGoesTheAllowedWay:
        def then_it_reports_the_rule_as_upheld(self, target):
            # Arrange
            tree = create_mock_source_tree(
                FILES, [("notes/note_service.py", "notes/create_note_transaction_script.py")]
            )

            # Act
            result = target.apply(CONFIG, tree)

            # Assert
            assert [(f.id, f.tone, f.detail) for f in result] == [
                ("no-upward", "good", "Checked 2 forbidden directions.")
            ]
