from dataclasses import dataclass
from pathlib import Path

from metatron.shared.domain.ports.model_port import ArchModelProjection


@dataclass(frozen=True)
class CompareBaselineParams:
    model: ArchModelProjection
    directory: Path
    rules: tuple[str, ...]
    allow_new: int
