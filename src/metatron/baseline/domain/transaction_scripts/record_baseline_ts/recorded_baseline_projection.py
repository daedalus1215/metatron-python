from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class RecordedBaselineProjection:
    project: str
    path: Path
    updated: bool
    count: int
    kept: int
    dropped: int
    ungated: tuple[str, ...]
