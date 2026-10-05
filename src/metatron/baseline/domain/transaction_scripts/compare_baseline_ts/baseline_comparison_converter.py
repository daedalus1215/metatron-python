from metatron.baseline.domain.entities.baseline_entity import BaselineEntity
from metatron.baseline.domain.transaction_scripts.compare_baseline_ts.baseline_check_projection import (  # noqa: E501
    BaselineCheckProjection,
)
from metatron.shared.domain.ports.model_port import ArchModelProjection


class BaselineComparisonConverter:
    """Which violations are new, which are known, and which the baseline still lists but are gone.

    Compared by fingerprint, so a swap (one fixed, one added) is still a new
    violation. `rules`, when given, narrows the gate: a new violation of another
    rule is reported but does not fail.
    """

    def apply(
        self,
        model: ArchModelProjection,
        baseline: BaselineEntity,
        rules: tuple[str, ...],
        allow_new: int,
    ) -> BaselineCheckProjection:
        current = {violation.fingerprint for violation in model.violations}
        added = [v for v in model.violations if v.fingerprint not in baseline.entries]
        in_scope = [v for v in added if not rules or v.rule in rules]
        return BaselineCheckProjection(
            project=model.project,
            total=len(model.violations),
            unchanged=len(model.violations) - len(added),
            added=tuple(in_scope),
            added_out_of_scope=tuple(v for v in added if v not in in_scope),
            fixed=tuple(
                entry
                for fingerprint, entry in baseline.entries.items()
                if fingerprint not in current
            ),
            rules=rules,
            allow_new=allow_new,
        )
