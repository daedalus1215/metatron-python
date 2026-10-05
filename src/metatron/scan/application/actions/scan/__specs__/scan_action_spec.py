import argparse
from dataclasses import replace
from pathlib import Path

import pytest

from metatron.scan.application.actions.scan.scan_action import ScanAction
from metatron.scan.application.actions.scan.scan_responder import ScanResponder
from metatron.scan.domain.services.scan_command import ScanCommand
from metatron.scan.domain.services.scan_result_projection import ScanResultProjection
from metatron.scan.domain.services.scan_service import ScanService
from metatron.scan.test_utils import create_mock_arch_config, create_mock_arch_model
from metatron.shared.test_utils.test_utils import create_apply_mock

RESULT = ScanResultProjection(
    config=create_mock_arch_config(),
    model=create_mock_arch_model(),
    model_path=Path("/code/notes/.metatron/model.json"),
)


@pytest.fixture
def scan_service_mock():
    mock = create_apply_mock(ScanService)
    mock.scan.return_value = RESULT
    return mock


@pytest.fixture
def scan_responder_mock():
    mock = create_apply_mock(ScanResponder)
    mock.apply.return_value = "the report"
    return mock


@pytest.fixture
def target(scan_service_mock, scan_responder_mock):
    return ScanAction(scan_service_mock, scan_responder_mock)


def parse(target, *argv):
    parser = argparse.ArgumentParser()
    target.configure(parser)
    return parser.parse_args(argv)


class GivenScanAction:
    class WhenRunWithAPath:
        def then_it_scans_from_there_prints_the_report_and_exits_zero(
            self, target, scan_service_mock, capsys
        ):
            # Act
            result = target.apply(parse(target, "/code/notes"))

            # Assert
            scan_service_mock.scan.assert_called_once_with(ScanCommand(start=Path("/code/notes")))
            assert capsys.readouterr().out == "the report\n"
            assert result == 0

    class WhenTheConfigCarriesANameWarning:
        def then_the_warning_goes_to_stderr(self, target, scan_service_mock, capsys):
            # Arrange
            config = create_mock_arch_config(name_warning="copied?")
            scan_service_mock.scan.return_value = replace(RESULT, config=config)

            # Act
            target.apply(parse(target))

            # Assert
            assert capsys.readouterr().err == "warning: copied?\n\n"
