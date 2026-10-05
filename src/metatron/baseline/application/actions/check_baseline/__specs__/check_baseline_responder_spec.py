import json

import pytest

from metatron.baseline.application.actions.check_baseline.check_baseline_responder import (
    CheckBaselineResponder,
)
from metatron.baseline.domain.transaction_scripts.compare_baseline_ts.baseline_check_projection import (  # noqa: E501
    BaselineCheckProjection,
)
from metatron.baseline.test_utils import create_mock_entry, create_mock_violation


def check(**overrides):
    values = dict(
        project="notes",
        total=3,
        unchanged=3,
        added=(),
        added_out_of_scope=(),
        fixed=(),
        rules=(),
        allow_new=0,
    )
    return BaselineCheckProjection(**{**values, **overrides})


@pytest.fixture
def target():
    return CheckBaselineResponder()


class GivenCheckBaselineResponder:
    class WhenNothingIsNew:
        def then_it_passes(self, target):
            # Act
            result = target.apply(check(), show_fixed=True, as_json=False)

            # Assert
            assert result.splitlines() == [
                "metatron check · notes",
                "",
                "  new violations        0",
                "",
                "  known, unchanged      3",
                "",
                "PASS — no new violations.",
            ]

    class WhenAViolationIsNew:
        def then_it_names_the_pair_and_fails(self, target):
            # Act
            result = target.apply(
                check(added=(create_mock_violation("aaa", "circular"),)),
                show_fixed=True,
                as_json=False,
            )

            # Assert
            assert (
                "    circular              notes/aaa_from.py\n"
                "                          -> notes/aaa_to.py"
            ) in result
            assert result.endswith(
                "FAIL — 1 new violation."
                " Fix it, or run `metatron-py baseline --update` to accept it."
            )

    class WhenSomeWereFixed:
        def then_it_passes_and_says_to_record_that(self, target):
            # Act
            result = target.apply(
                check(fixed=(create_mock_entry("bbb"),)), show_fixed=True, as_json=False
            )

            # Assert
            assert "  fixed since baseline  1" in result
            assert result.endswith("1 fixed; run `metatron-py baseline --update` to record that.")

        def then_no_fixed_hides_them(self, target):
            # Act
            result = target.apply(
                check(fixed=(create_mock_entry("bbb"),)), show_fixed=False, as_json=False
            )

            # Assert
            assert "fixed" not in result
            assert result.endswith("PASS — no new violations.")

    class WhenANewViolationIsOutsideTheGatedRules:
        def then_it_is_listed_as_reported_not_gated(self, target):
            # Act
            result = target.apply(
                check(added_out_of_scope=(create_mock_violation("ccc"),), rules=("circular",)),
                show_fixed=True,
                as_json=False,
            )

            # Assert
            assert "  new, outside --rule   1  (reported, not gated)" in result

    class WhenAskedForJson:
        def then_it_is_the_comparison_as_json(self, target):
            # Act
            result = json.loads(
                target.apply(
                    check(added=(create_mock_violation("aaa"),), allow_new=1),
                    show_fixed=True,
                    as_json=True,
                )
            )

            # Assert
            assert result["ok"] is True
            assert result["rules"] is None
            assert result["added"][0]["fingerprint"] == "aaa"
