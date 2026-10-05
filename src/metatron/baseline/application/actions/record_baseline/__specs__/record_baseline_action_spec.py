import argparse
from pathlib import Path

import pytest

from metatron.baseline.application.actions.record_baseline.record_baseline_action import (
    RecordBaselineAction,
)
from metatron.baseline.application.actions.record_baseline.record_baseline_responder import (
    RecordBaselineResponder,
)
from metatron.baseline.domain.services.baseline_service import BaselineService
from metatron.baseline.domain.services.record_baseline_command import RecordBaselineCommand
from metatron.shared.test_utils.test_utils import create_apply_mock


@pytest.fixture
def baseline_service_mock():
    return create_apply_mock(BaselineService)


@pytest.fixture
def record_baseline_responder_mock():
    mock = create_apply_mock(RecordBaselineResponder)
    mock.apply.return_value = "recorded"
    return mock


@pytest.fixture
def target(baseline_service_mock, record_baseline_responder_mock):
    return RecordBaselineAction(baseline_service_mock, record_baseline_responder_mock)


def parse(target, *argv):
    parser = argparse.ArgumentParser()
    target.configure(parser)
    return parser.parse_args(argv)


class GivenRecordBaselineAction:
    class WhenRunWithUpdate:
        def then_it_records_with_update_and_prints_the_result(
            self, target, baseline_service_mock, capsys
        ):
            # Act
            result = target.apply(parse(target, "/code/notes", "--update"))

            # Assert
            baseline_service_mock.record.assert_called_once_with(
                RecordBaselineCommand(start=Path("/code/notes"), update=True)
            )
            assert capsys.readouterr().out == "recorded\n"
            assert result == 0

    class WhenRunWithNothing:
        def then_it_records_here_without_update(self, target, baseline_service_mock):
            # Act
            target.apply(parse(target))

            # Assert
            baseline_service_mock.record.assert_called_once_with(
                RecordBaselineCommand(start=Path("."), update=False)
            )
