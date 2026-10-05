from metatron.baseline.application.actions.check_baseline.check_baseline_action import (
    CheckBaselineAction,
)
from metatron.baseline.application.actions.record_baseline.record_baseline_action import (
    RecordBaselineAction,
)

action_registry = [
    RecordBaselineAction,
    CheckBaselineAction,
]
