from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class ConfigTableProjection:
    """A metatron table as written on disk, and the file it was read from."""

    file: Path
    table: dict[str, Any]
