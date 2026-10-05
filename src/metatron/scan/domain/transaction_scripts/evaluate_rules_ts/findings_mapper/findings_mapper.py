from metatron.scan.domain.transaction_scripts.evaluate_rules_ts.findings_mapper.absent_patterns_findings_converter import (  # noqa: E501
    AbsentPatternsFindingsConverter,
)
from metatron.scan.domain.transaction_scripts.evaluate_rules_ts.findings_mapper.circular_findings_converter import (  # noqa: E501
    CircularFindingsConverter,
)
from metatron.scan.domain.transaction_scripts.evaluate_rules_ts.findings_mapper.cross_domain_findings_converter import (  # noqa: E501
    CrossDomainFindingsConverter,
)
from metatron.scan.domain.transaction_scripts.evaluate_rules_ts.findings_mapper.forbidden_findings_converter import (  # noqa: E501
    ForbiddenFindingsConverter,
)
from metatron.scan.domain.transaction_scripts.evaluate_rules_ts.findings_mapper.layer_findings_converter import (  # noqa: E501
    LayerFindingsConverter,
)
from metatron.scan.domain.transaction_scripts.evaluate_rules_ts.findings_mapper.module_cycles_findings_converter import (  # noqa: E501
    ModuleCyclesFindingsConverter,
)
from metatron.scan.domain.transaction_scripts.evaluate_rules_ts.findings_mapper.naming_findings_converter import (  # noqa: E501
    NamingFindingsConverter,
)
from metatron.scan.domain.transaction_scripts.evaluate_rules_ts.findings_mapper.same_level_findings_converter import (  # noqa: E501
    SameLevelFindingsConverter,
)
from metatron.scan.domain.transaction_scripts.evaluate_rules_ts.findings_mapper.skip_findings_converter import (  # noqa: E501
    SkipFindingsConverter,
)
from metatron.shared.domain.ports.config_port import ArchConfigProjection
from metatron.shared.domain.ports.model_port import (
    FindingProjection,
    SkipRuleProjection,
    SourceTreeProjection,
)


class FindingsMapper:
    """Every rule run over the tree, in the order the findings are reported."""

    def __init__(
        self,
        cross_domain_findings_converter: CrossDomainFindingsConverter,
        module_cycles_findings_converter: ModuleCyclesFindingsConverter,
        same_level_findings_converter: SameLevelFindingsConverter,
        forbidden_findings_converter: ForbiddenFindingsConverter,
        layer_findings_converter: LayerFindingsConverter,
        skip_findings_converter: SkipFindingsConverter,
        naming_findings_converter: NamingFindingsConverter,
        circular_findings_converter: CircularFindingsConverter,
        absent_patterns_findings_converter: AbsentPatternsFindingsConverter,
    ) -> None:
        self.cross_domain_findings_converter = cross_domain_findings_converter
        self.module_cycles_findings_converter = module_cycles_findings_converter
        self.same_level_findings_converter = same_level_findings_converter
        self.forbidden_findings_converter = forbidden_findings_converter
        self.layer_findings_converter = layer_findings_converter
        self.skip_findings_converter = skip_findings_converter
        self.naming_findings_converter = naming_findings_converter
        self.circular_findings_converter = circular_findings_converter
        self.absent_patterns_findings_converter = absent_patterns_findings_converter

    def apply(
        self,
        config: ArchConfigProjection,
        tree: SourceTreeProjection,
        skip_rules: tuple[SkipRuleProjection, ...],
    ) -> tuple[FindingProjection, ...]:
        return (
            *self.cross_domain_findings_converter.apply(config, tree),
            *self.module_cycles_findings_converter.apply(config, tree),
            *self.same_level_findings_converter.apply(config, tree),
            *self.forbidden_findings_converter.apply(config, tree),
            *self.layer_findings_converter.apply(config, tree),
            *self.skip_findings_converter.apply(config, tree, skip_rules),
            *self.naming_findings_converter.apply(config, tree),
            *self.circular_findings_converter.apply(tree),
            *self.absent_patterns_findings_converter.apply(config, tree),
        )
