import os
from pathlib import Path

from metatron.baseline.domain.transaction_scripts.record_baseline_ts.recorded_baseline_projection import (  # noqa: E501
    RecordedBaselineProjection,
)
from metatron.shared.utils.text_utils import count


class RecordBaselineResponder:
    def apply(self, recorded: RecordedBaselineProjection, cwd: Path) -> str:
        relative = os.path.relpath(recorded.path, cwd)
        shown = str(recorded.path) if relative.startswith("..") else relative
        accepted = f"  {count(recorded.count, 'violation')} accepted" + (
            f", {count(recorded.kept, 'note')} preserved" if recorded.kept else ""
        )
        lines = [
            f"metatron baseline · {recorded.project}",
            f"  {'updated' if recorded.updated else 'wrote'} {shown}",
            accepted,
        ]
        if recorded.dropped:
            gone = "the violation it described no longer exists"
            if recorded.dropped > 1:
                gone = "the violations they described no longer exist"
            lines.append(f"  {count(recorded.dropped, 'note')} dropped — {gone}")
        if recorded.ungated:
            lines.append(f"  not gated, aggregate findings: {', '.join(recorded.ungated)}")
        lines += [
            "",
            "  Commit this file. `metatron-py check` fails when a violation appears"
            " that is not in it.",
        ]
        return "\n".join(lines)
