from pathlib import Path

import pytest

from metatron.baseline.domain.services.baseline_service import BaselineService
from metatron.baseline.domain.services.check_baseline_command import CheckBaselineCommand
from metatron.baseline.domain.services.record_baseline_command import RecordBaselineCommand
from metatron.baseline.domain.transaction_scripts.compare_baseline_ts.compare_baseline_params import (  # noqa: E501
    CompareBaselineParams,
)
from metatron.baseline.domain.transaction_scripts.compare_baseline_ts.compare_baseline_transaction_script import (  # noqa: E501
    CompareBaselineTS,
)
from metatron.baseline.domain.transaction_scripts.record_baseline_ts.record_baseline_params import (  # noqa: E501
    RecordBaselineParams,
)
from metatron.baseline.domain.transaction_scripts.record_baseline_ts.record_baseline_transaction_script import (  # noqa: E501
    RecordBaselineTS,
)
from metatron.baseline.test_utils import create_mock_model
from metatron.shared.domain.ports.config_port import ArchConfigProjection, ConfigPort
from metatron.shared.domain.ports.model_port import ModelPort
from metatron.shared.test_utils.test_utils import create_apply_mock

START = Path("/code/notes/app")
DIRECTORY = Path("/code/notes")
MODEL = create_mock_model()


@pytest.fixture
def config():
    config = create_apply_mock(ArchConfigProjection)
    config.directory = DIRECTORY
    return config


@pytest.fixture
def config_port_mock(config):
    mock = create_apply_mock(ConfigPort)
    mock.load.return_value = config
    return mock


@pytest.fixture
def model_port_mock():
    mock = create_apply_mock(ModelPort)
    mock.build.return_value = MODEL
    return mock


@pytest.fixture
def record_baseline_ts_mock():
    return create_apply_mock(RecordBaselineTS)


@pytest.fixture
def compare_baseline_ts_mock():
    return create_apply_mock(CompareBaselineTS)


@pytest.fixture
def target(config_port_mock, model_port_mock, record_baseline_ts_mock, compare_baseline_ts_mock):
    return BaselineService(
        config_port_mock, model_port_mock, record_baseline_ts_mock, compare_baseline_ts_mock
    )


class GivenBaselineService:
    class WhenRecording:
        def then_it_builds_the_model_through_the_port_and_records_it_beside_the_config(
            self, target, config, config_port_mock, model_port_mock, record_baseline_ts_mock
        ):
            # Act
            result = target.record(RecordBaselineCommand(start=START, update=True))

            # Assert
            config_port_mock.load.assert_called_once_with(START)
            model_port_mock.build.assert_called_once_with(config)
            record_baseline_ts_mock.apply.assert_called_once_with(
                RecordBaselineParams(model=MODEL, directory=DIRECTORY, update=True)
            )
            assert result is record_baseline_ts_mock.apply.return_value

    class WhenChecking:
        def then_it_compares_the_model_with_the_rules_and_allowance(
            self, target, compare_baseline_ts_mock
        ):
            # Act
            result = target.check(
                CheckBaselineCommand(start=START, rules=("circular",), allow_new=2)
            )

            # Assert
            compare_baseline_ts_mock.apply.assert_called_once_with(
                CompareBaselineParams(
                    model=MODEL, directory=DIRECTORY, rules=("circular",), allow_new=2
                )
            )
            assert result is compare_baseline_ts_mock.apply.return_value
