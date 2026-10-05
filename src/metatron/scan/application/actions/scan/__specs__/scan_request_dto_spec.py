import argparse
from pathlib import Path

import pytest

from metatron.scan.application.actions.scan.scan_request_dto import ScanRequestDTO


@pytest.fixture
def parser():
    parser = argparse.ArgumentParser()
    ScanRequestDTO.add_arguments(parser)
    return parser


class GivenScanRequestDTO:
    class WhenNoPathIsGiven:
        def then_it_scans_from_here(self, parser):
            # Act
            result = ScanRequestDTO.from_namespace(parser.parse_args([]))

            # Assert
            assert result == ScanRequestDTO(path=Path("."))

    class WhenAPathIsGiven:
        def then_it_scans_from_there(self, parser):
            # Act
            result = ScanRequestDTO.from_namespace(parser.parse_args(["~/code/notes"]))

            # Assert
            assert result.path == Path("~/code/notes")
