import argparse
from pathlib import Path

import pytest

from metatron.baseline.application.actions.check_baseline.check_baseline_action import (
    CheckBaselineAction,
)
from metatron.baseline.application.actions.check_baseline.check_baseline_responder import (
    CheckBaselineResponder,
)
from metatron.baseline.domain.services.baseline_service import BaselineService
from metatron.baseline.domain.services.check_baseline_command import CheckBaselineCommand
from metatron.baseline.domain.transaction_scripts.compare_baseline_ts.baseline_check_projection import (  # noqa: E501
    BaselineCheckProjection,
)
from metatron.baseline.test_utils import create_mock_violation
from metatron.shared.test_utils.test_utils import create_apply_mock

PASSED = BaselineCheckProjection("notes", 0, 0, (), (), (), (), 0)
FAILED = BaselineCheckProjection("notes", 1, 0, (create_mock_violation("aaa"),), (), (), (), 0)


@pytest.fixture
def baseline_service_mock():
    mock = create_apply_mock(BaselineService)
    mock.check.return_value = PASSED
    return mock


@pytest.fixture
def check_baseline_responder_mock():
    mock = create_apply_mock(CheckBaselineResponder)
    mock.apply.return_value = "checked"
    return mock


@pytest.fixture
def target(baseline_service_mock, check_baseline_responder_mock):
    return CheckBaselineAction(baseline_service_mock, check_baseline_responder_mock)


def parse(target, *argv):
    parser = argparse.ArgumentParser()
    target.configure(parser)
    return parser.parse_args(argv)


class GivenCheckBaselineAction:
    class WhenNothingIsNew:
        def then_it_prints_the_check_and_exits_zero(
            self, target, baseline_service_mock, check_baseline_responder_mock, capsys
        ):
            # Act
            result = target.apply(parse(target, "app", "--rule", "circular", "--json"))

            # Assert
            baseline_service_mock.check.assert_called_once_with(
                CheckBaselineCommand(start=Path("app"), rules=("circular",), allow_new=0)
            )
            check_baseline_responder_mock.apply.assert_called_once_with(PASSED, True, True)
            assert capsys.readouterr().out == "checked\n"
            assert result == 0

    class WhenAViolationIsNew:
        def then_it_exits_one(self, target, baseline_service_mock):
            # Arrange
            baseline_service_mock.check.return_value = FAILED

            # Act
            result = target.apply(parse(target))

            # Assert
            assert result == 1
