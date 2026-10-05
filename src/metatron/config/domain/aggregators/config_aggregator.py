from pathlib import Path

from metatron.config.domain.transaction_scripts.load_config_ts.load_config_params import (
    LoadConfigParams,
)
from metatron.config.domain.transaction_scripts.load_config_ts.load_config_transaction_script import (  # noqa: E501
    LoadConfigTS,
)
from metatron.shared.domain.ports.config_port import ArchConfigProjection


class ConfigAggregator:
    """ConfigPort, as other contexts consume it."""

    def __init__(self, load_config_ts: LoadConfigTS) -> None:
        self.load_config_ts = load_config_ts

    def load(self, start: Path) -> ArchConfigProjection:
        return self.load_config_ts.apply(LoadConfigParams(start=start))
