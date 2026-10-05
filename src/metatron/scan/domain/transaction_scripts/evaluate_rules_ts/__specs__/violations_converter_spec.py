import hashlib

import pytest

from metatron.scan.domain.transaction_scripts.evaluate_rules_ts.violations_converter import (
    ViolationsConverter,
)
from metatron.shared.domain.ports.model_port import (
    FindingProjection,
    InstanceProjection,
    SkipRuleProjection,
    ViolationProjection,
)

SKIP = SkipRuleProjection("action>repository", "action", "repository", "crit", 2, "skips")
A_TO_R = InstanceProjection("notes/a_action.py", "notes/r_repository.py")


def finding(id, *instances, tone="warn", gate=True):
    return FindingProjection(id=id, tone=tone, title="", instances=instances, gate=gate)


@pytest.fixture
def target():
    return ViolationsConverter()


class GivenViolationsConverter:
    class WhenAWarningHasInstances:
        def then_each_is_a_violation_fingerprinted_like_metatron_nestjs(self, target):
            # Act
            result = target.apply((finding("action>repository", A_TO_R),), (SKIP,))

            # Assert
            expected = hashlib.sha1(
                b"action>repository|notes/a_action.py|notes/r_repository.py"
            ).hexdigest()[:12]
            assert result == (
                ViolationProjection(
                    fingerprint=expected,
                    rule="action>repository",
                    source="notes/a_action.py",
                    target="notes/r_repository.py",
                    severity="crit",
                ),
            )

    class WhenTheSameEdgeBreaksTwoRules:
        def then_it_is_two_violations_sorted_by_rule(self, target):
            # Act
            result = target.apply(
                (finding("no-upward", A_TO_R), finding("action>repository", A_TO_R)), (SKIP,)
            )

            # Assert
            assert [(v.rule, v.severity) for v in result] == [
                ("action>repository", "crit"),
                ("no-upward", "warn"),
            ]

    class WhenAnInstanceRepeats:
        def then_it_is_one_violation(self, target):
            # Act
            result = target.apply((finding("circular", A_TO_R, A_TO_R),), ())

            # Assert
            assert len(result) == 1

    class WhenAFindingIsUngatedOrNotAWarning:
        def then_it_never_becomes_a_violation(self, target):
            # Act
            result = target.apply(
                (
                    finding("dag", A_TO_R, gate=False),
                    finding("cross-domain", A_TO_R, tone="good"),
                    finding("absent-patterns", A_TO_R, tone="note"),
                ),
                (),
            )

            # Assert
            assert result == ()
