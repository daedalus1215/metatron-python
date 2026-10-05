from pathlib import Path

import pytest

from metatron.config.domain.aggregators.config_aggregator import ConfigAggregator
from metatron.config.domain.transaction_scripts.load_config_ts.load_config_params import (
    LoadConfigParams,
)
from metatron.config.domain.transaction_scripts.load_config_ts.load_config_transaction_script import (  # noqa: E501
    LoadConfigTS,
)
from metatron.shared.test_utils.test_utils import create_apply_mock


@pytest.fixture
def load_config_ts_mock():
    return create_apply_mock(LoadConfigTS)


@pytest.fixture
def target(load_config_ts_mock):
    return ConfigAggregator(load_config_ts_mock)


class GivenConfigAggregator:
    class WhenLoading:
        def then_it_delegates_to_load_config_ts(self, target, load_config_ts_mock):
            # Act
            result = target.load(Path("/code/notes"))

            # Assert
            load_config_ts_mock.apply.assert_called_once_with(
                LoadConfigParams(start=Path("/code/notes"))
            )
            assert result is load_config_ts_mock.apply.return_value
