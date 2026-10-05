from dataclasses import dataclass

from metatron.baseline.domain.entities.baseline_entity import BaselineEntryEntity
from metatron.shared.domain.ports.model_port import ViolationProjection


@dataclass(frozen=True)
class BaselineCheckProjection:
    """Today's violations against the accepted ones."""

    project: str
    total: int
    unchanged: int
    added: tuple[ViolationProjection, ...]
    added_out_of_scope: tuple[ViolationProjection, ...]
    fixed: tuple[BaselineEntryEntity, ...]
    rules: tuple[str, ...]
    allow_new: int

    @property
    def failed(self) -> bool:
        return len(self.added) > self.allow_new
