from metatron.baseline.domain.services.check_baseline_command import CheckBaselineCommand
from metatron.baseline.domain.services.record_baseline_command import RecordBaselineCommand
from metatron.baseline.domain.transaction_scripts.compare_baseline_ts.baseline_check_projection import (  # noqa: E501
    BaselineCheckProjection,
)
from metatron.baseline.domain.transaction_scripts.compare_baseline_ts.compare_baseline_params import (  # noqa: E501
    CompareBaselineParams,
)
from metatron.baseline.domain.transaction_scripts.compare_baseline_ts.compare_baseline_transaction_script import (  # noqa: E501
    CompareBaselineTS,
)
from metatron.baseline.domain.transaction_scripts.record_baseline_ts.record_baseline_params import (  # noqa: E501
    RecordBaselineParams,
)
from metatron.baseline.domain.transaction_scripts.record_baseline_ts.record_baseline_transaction_script import (  # noqa: E501
    RecordBaselineTS,
)
from metatron.baseline.domain.transaction_scripts.record_baseline_ts.recorded_baseline_projection import (  # noqa: E501
    RecordedBaselineProjection,
)
from metatron.shared.domain.ports.config_port import ConfigPort
from metatron.shared.domain.ports.model_port import ModelPort


class BaselineService:
    """The ratchet: record what is accepted, then hold the line against it.

    The config and the model come through ports; this context owns only the file.
    """

    def __init__(
        self,
        config_port: ConfigPort,
        model_port: ModelPort,
        record_baseline_ts: RecordBaselineTS,
        compare_baseline_ts: CompareBaselineTS,
    ) -> None:
        self.config_port = config_port
        self.model_port = model_port
        self.record_baseline_ts = record_baseline_ts
        self.compare_baseline_ts = compare_baseline_ts

    def record(self, command: RecordBaselineCommand) -> RecordedBaselineProjection:
        config = self.config_port.load(command.start)
        model = self.model_port.build(config)
        return self.record_baseline_ts.apply(
            RecordBaselineParams(model=model, directory=config.directory, update=command.update)
        )

    def check(self, command: CheckBaselineCommand) -> BaselineCheckProjection:
        config = self.config_port.load(command.start)
        model = self.model_port.build(config)
        return self.compare_baseline_ts.apply(
            CompareBaselineParams(
                model=model,
                directory=config.directory,
                rules=command.rules,
                allow_new=command.allow_new,
            )
        )
