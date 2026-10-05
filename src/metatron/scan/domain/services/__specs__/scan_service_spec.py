from pathlib import Path

import pytest

from metatron.scan.domain.services.scan_command import ScanCommand
from metatron.scan.domain.services.scan_result_projection import ScanResultProjection
from metatron.scan.domain.services.scan_service import ScanService
from metatron.scan.domain.transaction_scripts.evaluate_rules_ts.evaluate_rules_params import (
    EvaluateRulesParams,
)
from metatron.scan.domain.transaction_scripts.evaluate_rules_ts.evaluate_rules_transaction_script import (  # noqa: E501
    EvaluateRulesTS,
)
from metatron.scan.domain.transaction_scripts.read_source_tree_ts.read_source_tree_params import (
    ReadSourceTreeParams,
)
from metatron.scan.domain.transaction_scripts.read_source_tree_ts.read_source_tree_transaction_script import (  # noqa: E501
    ReadSourceTreeTS,
)
from metatron.scan.domain.transaction_scripts.write_model_ts.write_model_params import (
    WriteModelParams,
)
from metatron.scan.domain.transaction_scripts.write_model_ts.write_model_transaction_script import (  # noqa: E501
    WriteModelTS,
)
from metatron.scan.test_utils import (
    create_mock_arch_config,
    create_mock_arch_model,
    create_mock_source_tree,
)
from metatron.shared.domain.ports.config_port import ConfigError, ConfigPort
from metatron.shared.test_utils.test_utils import create_apply_mock

CONFIG = create_mock_arch_config()
TREE = create_mock_source_tree({"main.py": "bootstrap"})
MODEL = create_mock_arch_model()
WRITTEN = Path("/code/notes/.metatron/model.json")


@pytest.fixture
def config_port_mock():
    mock = create_apply_mock(ConfigPort)
    mock.load.return_value = CONFIG
    return mock


@pytest.fixture
def read_source_tree_ts_mock():
    mock = create_apply_mock(ReadSourceTreeTS)
    mock.apply.return_value = TREE
    return mock


@pytest.fixture
def evaluate_rules_ts_mock():
    mock = create_apply_mock(EvaluateRulesTS)
    mock.apply.return_value = MODEL
    return mock


@pytest.fixture
def write_model_ts_mock():
    mock = create_apply_mock(WriteModelTS)
    mock.apply.return_value = WRITTEN
    return mock


@pytest.fixture
def target(config_port_mock, read_source_tree_ts_mock, evaluate_rules_ts_mock, write_model_ts_mock):
    return ScanService(
        config_port_mock, read_source_tree_ts_mock, evaluate_rules_ts_mock, write_model_ts_mock
    )


class GivenScanService:
    class WhenScanning:
        def then_it_loads_reads_judges_and_writes_in_that_order(
            self,
            target,
            config_port_mock,
            read_source_tree_ts_mock,
            evaluate_rules_ts_mock,
            write_model_ts_mock,
        ):
            # Act
            target.scan(ScanCommand(start=Path("/code/notes")))

            # Assert
            config_port_mock.load.assert_called_once_with(Path("/code/notes"))
            read_source_tree_ts_mock.apply.assert_called_once_with(
                ReadSourceTreeParams(config=CONFIG)
            )
            evaluate_rules_ts_mock.apply.assert_called_once_with(
                EvaluateRulesParams(config=CONFIG, tree=TREE)
            )
            write_model_ts_mock.apply.assert_called_once_with(
                WriteModelParams(model=MODEL, out_dir=CONFIG.out_dir)
            )

        def then_it_returns_the_config_the_model_and_where_it_went(self, target):
            # Act
            result = target.scan(ScanCommand(start=Path("/code/notes")))

            # Assert
            assert result == ScanResultProjection(config=CONFIG, model=MODEL, model_path=WRITTEN)

    class WhenTheConfigCannotBeLoaded:
        def then_nothing_is_read_or_written(
            self, target, config_port_mock, read_source_tree_ts_mock, write_model_ts_mock
        ):
            # Arrange
            config_port_mock.load.side_effect = ConfigError("no config")

            # Act & Assert
            with pytest.raises(ConfigError):
                target.scan(ScanCommand(start=Path("/nowhere")))
            read_source_tree_ts_mock.apply.assert_not_called()
            write_model_ts_mock.apply.assert_not_called()
