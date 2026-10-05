from metatron.config.domain.aggregators.config_aggregator import ConfigAggregator
from metatron.config.registries.repository_registry import repository_registry
from metatron.config.registries.transaction_script_registry import transaction_script_registry
from metatron.shared.domain.ports.config_port import ConfigPort
from metatron.shared.kernel.module import Bind, Module

config_module = Module(
    providers=[
        Bind(ConfigPort, to=ConfigAggregator),
        *transaction_script_registry,
        *repository_registry,
    ],
)
