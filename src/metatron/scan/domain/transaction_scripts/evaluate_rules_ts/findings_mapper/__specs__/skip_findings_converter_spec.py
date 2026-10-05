import pytest

from metatron.scan.domain.transaction_scripts.evaluate_rules_ts.findings_mapper.skip_findings_converter import (  # noqa: E501
    SkipFindingsConverter,
)
from metatron.scan.domain.transaction_scripts.evaluate_rules_ts.skip_rules_converter import (
    SkipRulesConverter,
)
from metatron.scan.test_utils import create_mock_arch_config, create_mock_source_tree
from metatron.shared.domain.ports.model_port import InstanceProjection

CONFIG = create_mock_arch_config(allowed_skips=("service>repository",))
SKIP_RULES = SkipRulesConverter().apply(CONFIG)
FILES = {
    "notes/create_note_action.py": "action",
    "notes/notes_router.py": "router",
    "notes/note_service.py": "service",
    "notes/create_note_transaction_script.py": "transaction-script",
    "notes/note_repository.py": "repository",
}


@pytest.fixture
def target():
    return SkipFindingsConverter()


class GivenSkipFindingsConverter:
    class WhenAnActionReachesARepository:
        def then_it_is_a_critical_action_to_repository_finding(self, target):
            # Arrange
            tree = create_mock_source_tree(
                FILES, [("notes/create_note_action.py", "notes/note_repository.py")]
            )

            # Act
            result = target.apply(CONFIG, tree, SKIP_RULES)

            # Assert
            assert [f.id for f in result] == ["action>repository"]
            assert result[0].instances == (
                InstanceProjection("notes/create_note_action.py", "notes/note_repository.py"),
            )

    class WhenARouterReachesATransactionScript:
        def then_the_alias_counts_as_the_action_station(self, target):
            # Arrange
            tree = create_mock_source_tree(
                FILES,
                [("notes/notes_router.py", "notes/create_note_transaction_script.py")],
            )

            # Act
            result = target.apply(CONFIG, tree, SKIP_RULES)

            # Assert
            assert [f.id for f in result] == ["action>transaction-script"]

    class WhenEveryImportFollowsTheFlowOrAnAllowedSkip:
        def then_there_are_no_findings(self, target):
            # Arrange
            tree = create_mock_source_tree(
                FILES,
                [
                    ("notes/create_note_action.py", "notes/note_service.py"),
                    ("notes/note_service.py", "notes/create_note_transaction_script.py"),
                    ("notes/note_service.py", "notes/note_repository.py"),
                    ("notes/create_note_transaction_script.py", "notes/note_repository.py"),
                ],
            )

            # Act
            result = target.apply(CONFIG, tree, SKIP_RULES)

            # Assert
            assert result == ()
