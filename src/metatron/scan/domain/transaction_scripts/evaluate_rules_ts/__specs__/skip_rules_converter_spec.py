import pytest

from metatron.scan.domain.transaction_scripts.evaluate_rules_ts.skip_rules_converter import (
    SkipRulesConverter,
)
from metatron.scan.test_utils import create_mock_arch_config
from metatron.shared.domain.ports.model_port import SkipRuleProjection


@pytest.fixture
def target():
    return SkipRulesConverter()


class GivenSkipRulesConverter:
    class WhenTheFlowHasFourStations:
        def then_it_derives_every_skip_with_its_severity(self, target):
            # Act
            result = target.apply(create_mock_arch_config())

            # Assert
            assert [(r.id, r.severity, r.jump) for r in result] == [
                ("action>transaction-script", "warn", 1),
                ("action>repository", "crit", 2),
                ("service>repository", "warn", 1),
            ]

        def then_each_rule_says_what_it_skips(self, target):
            # Act
            result = target.apply(create_mock_arch_config())

            # Assert
            assert result[1] == SkipRuleProjection(
                id="action>repository",
                source="action",
                target="repository",
                severity="crit",
                jump=2,
                why="Action reaches Repository directly, skipping Service and Transaction Script",
            )

    class WhenASkipIsAllowed:
        def then_it_is_not_a_rule(self, target):
            # Act
            result = target.apply(create_mock_arch_config(allowed_skips=("service>repository",)))

            # Assert
            assert "service>repository" not in [r.id for r in result]

    class WhenTheFlowIsTooShortToSkip:
        def then_there_are_no_rules(self, target):
            # Act
            result = target.apply(create_mock_arch_config(flow=("action", "service")))

            # Assert
            assert result == ()
