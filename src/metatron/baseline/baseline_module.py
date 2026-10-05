from metatron.baseline.application.actions.check_baseline.check_baseline_responder import (
    CheckBaselineResponder,
)
from metatron.baseline.application.actions.record_baseline.record_baseline_responder import (
    RecordBaselineResponder,
)
from metatron.baseline.domain.services.baseline_service import BaselineService
from metatron.baseline.registries.action_registry import action_registry
from metatron.baseline.registries.repository_registry import repository_registry
from metatron.baseline.registries.transaction_script_registry import transaction_script_registry
from metatron.shared.kernel.module import Module

baseline_module = Module(
    providers=[
        BaselineService,
        RecordBaselineResponder,
        CheckBaselineResponder,
        *transaction_script_registry,
        *repository_registry,
    ],
    actions=action_registry,
)
