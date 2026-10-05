from pathlib import Path

import pytest

from metatron.baseline.domain.transaction_scripts.compare_baseline_ts.baseline_comparison_converter import (  # noqa: E501
    BaselineComparisonConverter,
)
from metatron.baseline.domain.transaction_scripts.compare_baseline_ts.compare_baseline_params import (  # noqa: E501
    CompareBaselineParams,
)
from metatron.baseline.domain.transaction_scripts.compare_baseline_ts.compare_baseline_transaction_script import (  # noqa: E501
    CompareBaselineTS,
)
from metatron.baseline.infrastructure.repositories.baseline_repository import BaselineRepository
from metatron.baseline.test_utils import create_mock_baseline, create_mock_model
from metatron.shared.domain.ports.config_port import ConfigError
from metatron.shared.test_utils.test_utils import create_apply_mock

DIRECTORY = Path("/code/notes")
MODEL = create_mock_model()
BASELINE = create_mock_baseline()
PARAMS = CompareBaselineParams(MODEL, DIRECTORY, ("circular",), 1)


@pytest.fixture
def baseline_repository_mock():
    mock = create_apply_mock(BaselineRepository)
    mock.read.return_value = BASELINE
    mock.path_in.return_value = DIRECTORY / "arch.baseline.json"
    return mock


@pytest.fixture
def baseline_comparison_converter_mock():
    return create_apply_mock(BaselineComparisonConverter)


@pytest.fixture
def target(baseline_repository_mock, baseline_comparison_converter_mock):
    return CompareBaselineTS(baseline_repository_mock, baseline_comparison_converter_mock)


class GivenCompareBaselineTS:
    class WhenABaselineExists:
        def then_it_compares_the_model_against_it(
            self, target, baseline_repository_mock, baseline_comparison_converter_mock
        ):
            # Act
            result = target.apply(PARAMS)

            # Assert
            baseline_repository_mock.read.assert_called_once_with(DIRECTORY)
            baseline_comparison_converter_mock.apply.assert_called_once_with(
                MODEL, BASELINE, ("circular",), 1
            )
            assert result is baseline_comparison_converter_mock.apply.return_value

    class WhenThereIsNoBaseline:
        def then_it_is_an_error_that_says_how_to_create_one(
            self, target, baseline_repository_mock, baseline_comparison_converter_mock
        ):
            # Arrange
            baseline_repository_mock.read.return_value = None

            # Act & Assert
            with pytest.raises(ConfigError, match="No arch.baseline.json in /code/notes"):
                target.apply(PARAMS)
            baseline_comparison_converter_mock.apply.assert_not_called()
