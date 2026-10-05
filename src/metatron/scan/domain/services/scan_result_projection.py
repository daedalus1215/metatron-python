from dataclasses import dataclass
from pathlib import Path

from metatron.shared.domain.ports.config_port import ArchConfigProjection
from metatron.shared.domain.ports.model_port import ArchModelProjection


@dataclass(frozen=True)
class ScanResultProjection:
    config: ArchConfigProjection
    model: ArchModelProjection
    model_path: Path
