from metatron.scan.domain.transaction_scripts.evaluate_rules_ts.findings_mapper.cross_context_constants import (  # noqa: E501
    ROOT_MODULE,
    SET_ASIDE_PATTERNS,
)
from metatron.shared.domain.ports.config_port import ArchConfigProjection
from metatron.shared.domain.ports.model_port import (
    FindingProjection,
    ImportEdgeProjection,
    InstanceProjection,
    SourceTreeProjection,
)
from metatron.shared.utils.text_utils import count


class CrossDomainFindingsConverter:
    """`cross-domain`: an import between bounded contexts that lands outside the gateways.

    Domains talk only through aggregators consumed via ports.
    """

    def apply(
        self, config: ArchConfigProjection, tree: SourceTreeProjection
    ) -> tuple[FindingProjection, ...]:
        crossings = [edge for edge in tree.edges if self._crosses(edge, config, tree)]
        hits = [
            edge
            for edge in crossings
            if tree.by_path[edge.target].pattern not in config.cross_domain_gateways
        ]
        gateways = ", ".join(config.cross_domain_gateways) or "(none configured)"
        detail = (
            f"{count(len(crossings), 'import')} cross a bounded context."
            f" Allowed landing points: {gateways}."
        )
        source = tree.by_path
        return (
            FindingProjection(
                id="cross-domain",
                tone="warn" if hits else "good",
                title=f"{count(len(hits), 'cross-domain import')} bypass the gateways"
                if hits
                else "Every cross-domain import goes through a gateway",
                detail=detail,
                items=tuple(
                    f"{source[e.source].module}/{source[e.source].pattern} -> {e.target}"
                    for e in (hits or crossings)
                ),
                instances=tuple(InstanceProjection(e.source, e.target) for e in hits),
            ),
        )

    def _crosses(
        self, edge: ImportEdgeProjection, config: ArchConfigProjection, tree: SourceTreeProjection
    ) -> bool:
        source, target = tree.by_path[edge.source], tree.by_path[edge.target]
        set_aside = {*config.infra_modules, ROOT_MODULE}
        return (
            source.module != target.module
            and source.module not in set_aside
            and target.module not in set_aside
            and source.pattern not in SET_ASIDE_PATTERNS
            and target.pattern not in SET_ASIDE_PATTERNS
        )
