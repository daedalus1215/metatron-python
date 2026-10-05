import argparse
import sys
from pathlib import Path

from metatron.scan.application.actions.scan.scan_request_dto import ScanRequestDTO
from metatron.scan.application.actions.scan.scan_responder import ScanResponder
from metatron.scan.domain.services.scan_command import ScanCommand
from metatron.scan.domain.services.scan_service import ScanService


class ScanAction:
    """`metatron-py scan`: build the model, write it, say what it found. A report, not a gate."""

    name = "scan"
    help = "build the model, write .metatron/model.json, and print what it found"

    def __init__(self, scan_service: ScanService, scan_responder: ScanResponder) -> None:
        self.scan_service = scan_service
        self.scan_responder = scan_responder

    def configure(self, parser: argparse.ArgumentParser) -> None:
        ScanRequestDTO.add_arguments(parser)

    def apply(self, arguments: argparse.Namespace) -> int:
        request = ScanRequestDTO.from_namespace(arguments)
        result = self.scan_service.scan(ScanCommand(start=request.path))
        if result.config.name_warning:
            print(f"warning: {result.config.name_warning}\n", file=sys.stderr)
        print(self.scan_responder.apply(result, Path.cwd()))
        return 0
