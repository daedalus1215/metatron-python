from metatron.scan.domain.transaction_scripts.evaluate_rules_ts.evaluate_rules_params import (
    EvaluateRulesParams,
)
from metatron.scan.domain.transaction_scripts.evaluate_rules_ts.evaluate_rules_transaction_script import (  # noqa: E501
    EvaluateRulesTS,
)
from metatron.scan.domain.transaction_scripts.read_source_tree_ts.read_source_tree_params import (
    ReadSourceTreeParams,
)
from metatron.scan.domain.transaction_scripts.read_source_tree_ts.read_source_tree_transaction_script import (  # noqa: E501
    ReadSourceTreeTS,
)
from metatron.shared.domain.ports.config_port import ArchConfigProjection
from metatron.shared.domain.ports.model_port import ArchModelProjection


class ScanAggregator:
    """ModelPort, as other contexts consume it: the model, built and not written."""

    def __init__(
        self, read_source_tree_ts: ReadSourceTreeTS, evaluate_rules_ts: EvaluateRulesTS
    ) -> None:
        self.read_source_tree_ts = read_source_tree_ts
        self.evaluate_rules_ts = evaluate_rules_ts

    def build(self, config: ArchConfigProjection) -> ArchModelProjection:
        tree = self.read_source_tree_ts.apply(ReadSourceTreeParams(config=config))
        return self.evaluate_rules_ts.apply(EvaluateRulesParams(config=config, tree=tree))
