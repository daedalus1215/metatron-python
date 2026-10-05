from dataclasses import dataclass

from metatron.shared.domain.ports.config_port import ArchConfigProjection


@dataclass(frozen=True)
class ReadSourceTreeParams:
    config: ArchConfigProjection
