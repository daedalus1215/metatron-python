import pytest

from metatron.scan.domain.aggregators.scan_aggregator import ScanAggregator
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
from metatron.scan.test_utils import create_mock_arch_config, create_mock_source_tree
from metatron.shared.test_utils.test_utils import create_apply_mock

CONFIG = create_mock_arch_config()
TREE = create_mock_source_tree({"main.py": "bootstrap"})


@pytest.fixture
def read_source_tree_ts_mock():
    mock = create_apply_mock(ReadSourceTreeTS)
    mock.apply.return_value = TREE
    return mock


@pytest.fixture
def evaluate_rules_ts_mock():
    return create_apply_mock(EvaluateRulesTS)


@pytest.fixture
def target(read_source_tree_ts_mock, evaluate_rules_ts_mock):
    return ScanAggregator(read_source_tree_ts_mock, evaluate_rules_ts_mock)


class GivenScanAggregator:
    class WhenBuilding:
        def then_it_reads_the_tree_and_judges_it(
            self, target, read_source_tree_ts_mock, evaluate_rules_ts_mock
        ):
            # Act
            result = target.build(CONFIG)

            # Assert
            read_source_tree_ts_mock.apply.assert_called_once_with(
                ReadSourceTreeParams(config=CONFIG)
            )
            evaluate_rules_ts_mock.apply.assert_called_once_with(
                EvaluateRulesParams(config=CONFIG, tree=TREE)
            )
            assert result is evaluate_rules_ts_mock.apply.return_value
