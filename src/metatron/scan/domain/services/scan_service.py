from metatron.scan.domain.services.scan_command import ScanCommand
from metatron.scan.domain.services.scan_result_projection import ScanResultProjection
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
from metatron.scan.domain.transaction_scripts.write_model_ts.write_model_params import (
    WriteModelParams,
)
from metatron.scan.domain.transaction_scripts.write_model_ts.write_model_transaction_script import (  # noqa: E501
    WriteModelTS,
)
from metatron.shared.domain.ports.config_port import ConfigPort


class ScanService:
    def __init__(
        self,
        config_port: ConfigPort,
        read_source_tree_ts: ReadSourceTreeTS,
        evaluate_rules_ts: EvaluateRulesTS,
        write_model_ts: WriteModelTS,
    ) -> None:
        self.config_port = config_port
        self.read_source_tree_ts = read_source_tree_ts
        self.evaluate_rules_ts = evaluate_rules_ts
        self.write_model_ts = write_model_ts

    def scan(self, command: ScanCommand) -> ScanResultProjection:
        config = self.config_port.load(command.start)
        tree = self.read_source_tree_ts.apply(ReadSourceTreeParams(config=config))
        model = self.evaluate_rules_ts.apply(EvaluateRulesParams(config=config, tree=tree))
        written = self.write_model_ts.apply(WriteModelParams(model=model, out_dir=config.out_dir))
        return ScanResultProjection(config=config, model=model, model_path=written)
