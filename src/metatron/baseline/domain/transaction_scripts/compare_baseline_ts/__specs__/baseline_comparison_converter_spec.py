import pytest

from metatron.baseline.domain.transaction_scripts.compare_baseline_ts.baseline_comparison_converter import (  # noqa: E501
    BaselineComparisonConverter,
)
from metatron.baseline.test_utils import (
    create_mock_baseline,
    create_mock_entry,
    create_mock_model,
    create_mock_violation,
)


@pytest.fixture
def target():
    return BaselineComparisonConverter()


class GivenBaselineComparisonConverter:
    class WhenNothingChanged:
        def then_everything_is_known_and_it_passes(self, target):
            # Arrange
            model = create_mock_model(create_mock_violation("aaa"))
            baseline = create_mock_baseline(create_mock_entry("aaa"))

            # Act
            result = target.apply(model, baseline, (), 0)

            # Assert
            assert (result.total, result.unchanged, result.added, result.fixed) == (1, 1, (), ())
            assert not result.failed

    class WhenOneViolationIsSwappedForAnother:
        def then_the_new_one_fails_and_the_old_one_is_fixed(self, target):
            # Arrange
            model = create_mock_model(create_mock_violation("bbb"))
            baseline = create_mock_baseline(create_mock_entry("aaa"))

            # Act
            result = target.apply(model, baseline, (), 0)

            # Assert
            assert [v.fingerprint for v in result.added] == ["bbb"]
            assert [e.fingerprint for e in result.fixed] == ["aaa"]
            assert result.failed

    class WhenTheGateIsNarrowedToOneRule:
        def then_a_new_violation_of_another_rule_is_reported_but_passes(self, target):
            # Arrange
            model = create_mock_model(create_mock_violation("ccc", "circular"))

            # Act
            result = target.apply(model, create_mock_baseline(), ("no-upward",), 0)

            # Assert
            assert result.added == ()
            assert [v.rule for v in result.added_out_of_scope] == ["circular"]
            assert not result.failed

    class WhenSomeNewViolationsAreAllowed:
        def then_it_fails_only_beyond_the_allowance(self, target):
            # Arrange
            model = create_mock_model(create_mock_violation("ddd"), create_mock_violation("eee"))

            # Act
            within = target.apply(model, create_mock_baseline(), (), 2)
            beyond = target.apply(model, create_mock_baseline(), (), 1)

            # Assert
            assert not within.failed
            assert beyond.failed
