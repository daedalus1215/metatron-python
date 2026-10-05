import argparse
from pathlib import Path

from metatron.baseline.application.actions.record_baseline.record_baseline_request_dto import (
    RecordBaselineRequestDTO,
)
from metatron.baseline.application.actions.record_baseline.record_baseline_responder import (
    RecordBaselineResponder,
)
from metatron.baseline.domain.services.baseline_service import BaselineService
from metatron.baseline.domain.services.record_baseline_command import RecordBaselineCommand


class RecordBaselineAction:
    """`metatron-py baseline`: accept today's violations, in a file meant to be committed."""

    name = "baseline"
    help = "record today's violations as accepted, in arch.baseline.json beside the config"

    def __init__(
        self, baseline_service: BaselineService, record_baseline_responder: RecordBaselineResponder
    ) -> None:
        self.baseline_service = baseline_service
        self.record_baseline_responder = record_baseline_responder

    def configure(self, parser: argparse.ArgumentParser) -> None:
        RecordBaselineRequestDTO.add_arguments(parser)

    def apply(self, arguments: argparse.Namespace) -> int:
        request = RecordBaselineRequestDTO.from_namespace(arguments)
        recorded = self.baseline_service.record(
            RecordBaselineCommand(start=request.path, update=request.update)
        )
        print(self.record_baseline_responder.apply(recorded, Path.cwd()))
        return 0
