from metatron.scan.application.actions.scan.scan_responder import ScanResponder
from metatron.scan.domain.aggregators.scan_aggregator import ScanAggregator
from metatron.scan.domain.services.scan_service import ScanService
from metatron.scan.registries.action_registry import action_registry
from metatron.scan.registries.repository_registry import repository_registry
from metatron.scan.registries.transaction_script_registry import transaction_script_registry
from metatron.shared.domain.ports.model_port import ModelPort
from metatron.shared.kernel.module import Bind, Module

scan_module = Module(
    providers=[
        ScanService,
        ScanResponder,
        Bind(ModelPort, to=ScanAggregator),
        *transaction_script_registry,
        *repository_registry,
    ],
    actions=action_registry,
)
