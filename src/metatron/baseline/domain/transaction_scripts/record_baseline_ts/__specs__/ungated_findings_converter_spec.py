import pytest

from metatron.baseline.domain.transaction_scripts.record_baseline_ts.ungated_findings_converter import (  # noqa: E501
    UngatedFindingsConverter,
)
from metatron.baseline.test_utils import create_mock_model
from metatron.shared.domain.ports.model_port import FindingProjection, InstanceProjection

INSTANCE = (InstanceProjection("a", "b"),)


@pytest.fixture
def target():
    return UngatedFindingsConverter()


class GivenUngatedFindingsConverter:
    class WhenSomeWarningsCannotGate:
        def then_only_those_are_listed(self, target):
            # Arrange
            model = create_mock_model(
                findings=(
                    FindingProjection("dag", "warn", "loop", gate=False),
                    FindingProjection("orphans", "warn", "no instances"),
                    FindingProjection("circular", "warn", "gated", instances=INSTANCE),
                    FindingProjection("cross-domain", "good", "holds"),
                )
            )

            # Act
            result = target.apply(model)

            # Assert
            assert result == ("dag", "orphans")
