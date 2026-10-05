from metatron.shared.domain.ports.config_port import ArchConfigProjection
from metatron.shared.domain.ports.model_port import SkipRuleProjection


class SkipRulesConverter:
    """Every skip the flow implies, minus the ones the architecture allows.

    Declaring the flow beats hand-listing rules: jumping one station is a
    warning, two or more is critical.
    """

    def apply(self, config: ArchConfigProjection) -> tuple[SkipRuleProjection, ...]:
        flow = config.flow
        return tuple(
            self._rule(flow, i, j)
            for i in range(len(flow))
            for j in range(i + 2, len(flow))
            if f"{flow[i]}>{flow[j]}" not in config.allowed_skips
        )

    def _rule(self, flow: tuple[str, ...], i: int, j: int) -> SkipRuleProjection:
        jump = j - i - 1
        source, target = self._label(flow[i]), self._label(flow[j])
        skipped = " and ".join(self._label(station) for station in flow[i + 1 : j])
        return SkipRuleProjection(
            id=f"{flow[i]}>{flow[j]}",
            source=flow[i],
            target=flow[j],
            severity="crit" if jump >= 2 else "warn",
            jump=jump,
            why=f"{source} reaches {target} directly, skipping {skipped}",
        )

    def _label(self, pattern: str) -> str:
        return pattern.replace("-", " ").title()
