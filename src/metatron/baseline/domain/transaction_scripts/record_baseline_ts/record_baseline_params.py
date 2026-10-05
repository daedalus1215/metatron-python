from dataclasses import dataclass
from pathlib import Path

from metatron.shared.domain.ports.model_port import ArchModelProjection


@dataclass(frozen=True)
class RecordBaselineParams:
    model: ArchModelProjection
    directory: Path
    update: bool
