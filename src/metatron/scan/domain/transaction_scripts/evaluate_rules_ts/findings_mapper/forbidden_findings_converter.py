from metatron.scan.domain.utils.text_utils import count
from metatron.shared.domain.ports.config_port import ArchConfigProjection
from metatron.shared.domain.ports.model_port import (
    FindingProjection,
    InstanceProjection,
    SourceTreeProjection,
)


class ForbiddenFindingsConverter:
    """`no-upward`: every import in a direction `forbidden` rules out."""

    def apply(
        self, config: ArchConfigProjection, tree: SourceTreeProjection
    ) -> tuple[FindingProjection, ...]:
        hits = [
            (edge, rule)
            for edge in tree.edges
            for rule in config.forbidden
            if tree.by_path[edge.source].pattern == rule.source
            and tree.by_path[edge.target].pattern == rule.target
        ]
        checked = f"Checked {count(len(config.forbidden), 'forbidden direction')}."
        if not hits:
            return (
                FindingProjection(
                    id="no-upward", tone="good", title="No upward calls", detail=checked
                ),
            )
        return (
            FindingProjection(
                id="no-upward",
                tone="warn",
                title=count(len(hits), "upward call"),
                detail=checked,
                items=tuple(f"{rule.why}: {edge.source} -> {edge.target}" for edge, rule in hits),
                instances=tuple(InstanceProjection(edge.source, edge.target) for edge, _ in hits),
            ),
        )
