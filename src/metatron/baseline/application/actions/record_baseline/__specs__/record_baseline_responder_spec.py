from pathlib import Path

import pytest

from metatron.baseline.application.actions.record_baseline.record_baseline_responder import (
    RecordBaselineResponder,
)
from metatron.baseline.domain.transaction_scripts.record_baseline_ts.recorded_baseline_projection import (  # noqa: E501
    RecordedBaselineProjection,
)

CWD = Path("/code/notes")


def recorded(**overrides):
    values = dict(
        project="notes",
        path=CWD / "arch.baseline.json",
        updated=False,
        count=3,
        kept=0,
        dropped=0,
        ungated=(),
    )
    return RecordedBaselineProjection(**{**values, **overrides})


@pytest.fixture
def target():
    return RecordBaselineResponder()


class GivenRecordBaselineResponder:
    class WhenAFirstBaselineIsWritten:
        def then_it_says_what_was_accepted_and_to_commit_it(self, target):
            # Act
            result = target.apply(recorded(), CWD)

            # Assert
            assert result.splitlines()[:3] == [
                "metatron baseline · notes",
                "  wrote arch.baseline.json",
                "  3 violations accepted",
            ]
            assert "Commit this file." in result

    class WhenAnUpdateKeptAndDroppedNotes:
        def then_it_says_how_many_of_each(self, target):
            # Act
            result = target.apply(recorded(updated=True, kept=1, dropped=2), CWD)

            # Assert
            assert "  updated arch.baseline.json" in result
            assert "  3 violations accepted, 1 note preserved" in result
            assert "  2 notes dropped — the violations they described no longer exist" in result

    class WhenSomeWarningsCannotGate:
        def then_it_names_them(self, target):
            # Act
            result = target.apply(recorded(ungated=("dag",)), CWD)

            # Assert
            assert "  not gated, aggregate findings: dag" in result
