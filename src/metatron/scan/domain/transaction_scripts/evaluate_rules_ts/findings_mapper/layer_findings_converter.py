from metatron.scan.domain.utils.text_utils import count
from metatron.shared.domain.ports.config_port import ArchConfigProjection, LayerRuleProjection
from metatron.shared.domain.ports.model_port import (
    FindingProjection,
    InstanceProjection,
    SourceTreeProjection,
)


class LayerFindingsConverter:
    """One finding per `layers` rule: a file under its `from` directory importing one under `to`.

    A file is under a directory when any segment of its path names it, so
    `notes/domain/services/x.py` is in `domain` wherever the context sits.
    """

    def apply(
        self, config: ArchConfigProjection, tree: SourceTreeProjection
    ) -> tuple[FindingProjection, ...]:
        return tuple(self._finding(rule, tree) for rule in config.layers)

    def _finding(self, rule: LayerRuleProjection, tree: SourceTreeProjection) -> FindingProjection:
        hits = [
            edge
            for edge in tree.edges
            if self._under(edge.source, rule.source) and self._under(edge.target, rule.target)
        ]
        if not hits:
            return FindingProjection(
                id=rule.id,
                tone="good",
                title=f"No {rule.source}/ file imports from {rule.target}/",
                detail=rule.why,
            )
        return FindingProjection(
            id=rule.id,
            tone="warn",
            title=f"{count(len(hits), 'import')} where {rule.why}",
            detail=f"Dependencies point inward: {rule.source}/ must not import {rule.target}/.",
            items=tuple(f"{edge.source}  ->  {edge.target}" for edge in hits),
            instances=tuple(InstanceProjection(edge.source, edge.target) for edge in hits),
        )

    def _under(self, path: str, directory: str) -> bool:
        return directory in path.split("/")[:-1]
