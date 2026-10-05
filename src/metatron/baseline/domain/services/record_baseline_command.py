from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class RecordBaselineCommand:
    start: Path
    update: bool
