from metatron.scan.domain.transaction_scripts.evaluate_rules_ts.evaluate_rules_params import (
    EvaluateRulesParams,
)
from metatron.scan.domain.transaction_scripts.evaluate_rules_ts.findings_mapper.findings_mapper import (  # noqa: E501
    FindingsMapper,
)
from metatron.scan.domain.transaction_scripts.evaluate_rules_ts.skip_rules_converter import (
    SkipRulesConverter,
)
from metatron.scan.domain.transaction_scripts.evaluate_rules_ts.violations_converter import (
    ViolationsConverter,
)
from metatron.shared.domain.ports.model_port import ArchModelProjection


class EvaluateRulesTS:
    """The tree judged against the config's rules: the whole model."""

    def __init__(
        self,
        skip_rules_converter: SkipRulesConverter,
        findings_mapper: FindingsMapper,
        violations_converter: ViolationsConverter,
    ) -> None:
        self.skip_rules_converter = skip_rules_converter
        self.findings_mapper = findings_mapper
        self.violations_converter = violations_converter

    def apply(self, params: EvaluateRulesParams) -> ArchModelProjection:
        config, tree = params.config, params.tree
        skip_rules = self.skip_rules_converter.apply(config)
        findings = self.findings_mapper.apply(config, tree, skip_rules)
        return ArchModelProjection(
            project=config.name,
            root=config.root.relative_to(config.directory).as_posix()
            if config.root.is_relative_to(config.directory)
            else str(config.root),
            tiers=config.tiers,
            flow=config.flow,
            skip_rules=skip_rules,
            tree=tree,
            findings=findings,
            violations=self.violations_converter.apply(findings, skip_rules),
        )
