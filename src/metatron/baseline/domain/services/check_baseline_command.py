from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class CheckBaselineCommand:
    start: Path
    rules: tuple[str, ...]
    allow_new: int
