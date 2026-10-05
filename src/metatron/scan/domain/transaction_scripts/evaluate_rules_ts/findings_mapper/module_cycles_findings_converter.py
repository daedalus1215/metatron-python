from metatron.scan.domain.transaction_scripts.evaluate_rules_ts.findings_mapper.cross_context_constants import (  # noqa: E501
    ROOT_MODULE,
    SET_ASIDE_PATTERNS,
)
from metatron.scan.domain.utils.graph_utils import cycles
from metatron.shared.domain.ports.config_port import ArchConfigProjection
from metatron.shared.domain.ports.model_port import FindingProjection, SourceTreeProjection


class ModuleCyclesFindingsConverter:
    """`dag`: whether the bounded contexts depend on each other in a loop.

    An aggregate observation, not a violation: the loop is made of imports
    other findings already name one by one, so it is printed and never gated.
    An import landing on a port is the sanctioned way across and is left out.
    """

    def apply(
        self, config: ArchConfigProjection, tree: SourceTreeProjection
    ) -> tuple[FindingProjection, ...]:
        set_aside = {*config.infra_modules, ROOT_MODULE}
        between = {
            (source.module, target.module)
            for source, target in (
                (tree.by_path[edge.source], tree.by_path[edge.target]) for edge in tree.edges
            )
            if source.module != target.module
            and not {source.module, target.module} & set_aside
            and source.pattern not in SET_ASIDE_PATTERNS
            and target.pattern not in {*SET_ASIDE_PATTERNS, "port"}
        }
        loops = cycles(sorted(between))
        return (
            FindingProjection(
                id="dag",
                tone="warn" if loops else "good",
                title="Bounded contexts depend on each other in a loop"
                if loops
                else "Bounded contexts form a DAG",
                detail="Imports landing on a port, the wiring and the tests are left out.",
                items=tuple(" <-> ".join(loop) for loop in loops),
                gate=False,
            ),
        )
