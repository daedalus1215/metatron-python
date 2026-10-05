from dataclasses import dataclass

from metatron.shared.domain.ports.config_port import ArchConfigProjection
from metatron.shared.domain.ports.model_port import SourceTreeProjection


@dataclass(frozen=True)
class EvaluateRulesParams:
    config: ArchConfigProjection
    tree: SourceTreeProjection
