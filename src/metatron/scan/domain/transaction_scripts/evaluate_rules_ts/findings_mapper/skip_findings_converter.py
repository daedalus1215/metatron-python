from collections import defaultdict

from metatron.shared.domain.ports.config_port import ArchConfigProjection
from metatron.shared.domain.ports.model_port import (
    FindingProjection,
    ImportEdgeProjection,
    InstanceProjection,
    SkipRuleProjection,
    SourceTreeProjection,
)


class SkipFindingsConverter:
    """One finding per skip rule an import breaks, read through the flow aliases.

    A router is the action station, so a router importing a repository breaks
    `action>repository` exactly as an action would.
    """

    def apply(
        self,
        config: ArchConfigProjection,
        tree: SourceTreeProjection,
        skip_rules: tuple[SkipRuleProjection, ...],
    ) -> tuple[FindingProjection, ...]:
        stations = {pattern: i for i, pattern in enumerate(config.flow)} | {
            alias: config.flow.index(station)
            for station, aliases in config.flow_aliases.items()
            if station in config.flow
            for alias in aliases
        }
        rules = {(stations[r.source], stations[r.target]): r for r in skip_rules}
        hits: dict[str, list[ImportEdgeProjection]] = defaultdict(list)
        for edge in tree.edges:
            source, target = tree.by_path[edge.source], tree.by_path[edge.target]
            rule = rules.get((stations.get(source.pattern, -1), stations.get(target.pattern, -1)))
            if rule:
                hits[rule.id].append(edge)
        return tuple(
            FindingProjection(
                id=rule.id,
                tone="warn",
                title=rule.why,
                detail=f"Intended flow is {' -> '.join(config.flow)}.",
                items=tuple(f"{e.source}  ->  {e.target}" for e in hits[rule.id]),
                instances=tuple(InstanceProjection(e.source, e.target) for e in hits[rule.id]),
            )
            for rule in skip_rules
            if hits[rule.id]
        )
