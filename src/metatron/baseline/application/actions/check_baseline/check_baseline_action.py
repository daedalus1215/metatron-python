import argparse

from metatron.baseline.application.actions.check_baseline.check_baseline_request_dto import (
    CheckBaselineRequestDTO,
)
from metatron.baseline.application.actions.check_baseline.check_baseline_responder import (
    CheckBaselineResponder,
)
from metatron.baseline.domain.services.baseline_service import BaselineService
from metatron.baseline.domain.services.check_baseline_command import CheckBaselineCommand


class CheckBaselineAction:
    """`metatron-py check`: exit 0 clean, 1 on a new violation, 2 on a tool or config error."""

    name = "check"
    help = "fail if a violation appeared that arch.baseline.json does not accept"

    def __init__(
        self, baseline_service: BaselineService, check_baseline_responder: CheckBaselineResponder
    ) -> None:
        self.baseline_service = baseline_service
        self.check_baseline_responder = check_baseline_responder

    def configure(self, parser: argparse.ArgumentParser) -> None:
        CheckBaselineRequestDTO.add_arguments(parser)

    def apply(self, arguments: argparse.Namespace) -> int:
        request = CheckBaselineRequestDTO.from_namespace(arguments)
        check = self.baseline_service.check(
            CheckBaselineCommand(
                start=request.path, rules=request.rules, allow_new=request.allow_new
            )
        )
        print(self.check_baseline_responder.apply(check, request.show_fixed, request.as_json))
        return 1 if check.failed else 0
