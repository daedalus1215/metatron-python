from pathlib import Path

import pytest

from metatron.scan.domain.transaction_scripts.evaluate_rules_ts.evaluate_rules_params import (
    EvaluateRulesParams,
)
from metatron.scan.domain.transaction_scripts.evaluate_rules_ts.evaluate_rules_transaction_script import (  # noqa: E501
    EvaluateRulesTS,
)
from metatron.scan.domain.transaction_scripts.evaluate_rules_ts.findings_mapper.findings_mapper import (  # noqa: E501
    FindingsMapper,
)
from metatron.scan.domain.transaction_scripts.evaluate_rules_ts.skip_rules_converter import (
    SkipRulesConverter,
)
from metatron.scan.domain.transaction_scripts.evaluate_rules_ts.violations_converter import (
    ViolationsConverter,
)
from metatron.scan.test_utils import create_mock_arch_config, create_mock_source_tree
from metatron.shared.domain.ports.model_port import FindingProjection, SkipRuleProjection
from metatron.shared.test_utils.test_utils import create_apply_mock

CONFIG = create_mock_arch_config()
TREE = create_mock_source_tree({"main.py": "bootstrap"})
SKIP_RULES = (SkipRuleProjection("a>c", "a", "c", "warn", 1, "skips b"),)
FINDINGS = (FindingProjection(id="circular", tone="good", title="No circular imports"),)


@pytest.fixture
def skip_rules_converter_mock():
    mock = create_apply_mock(SkipRulesConverter)
    mock.apply.return_value = SKIP_RULES
    return mock


@pytest.fixture
def findings_mapper_mock():
    mock = create_apply_mock(FindingsMapper)
    mock.apply.return_value = FINDINGS
    return mock


@pytest.fixture
def violations_converter_mock():
    mock = create_apply_mock(ViolationsConverter)
    mock.apply.return_value = ()
    return mock


@pytest.fixture
def target(skip_rules_converter_mock, findings_mapper_mock, violations_converter_mock):
    return EvaluateRulesTS(
        skip_rules_converter_mock, findings_mapper_mock, violations_converter_mock
    )


class GivenEvaluateRulesTS:
    class WhenEvaluating:
        def then_the_derived_skip_rules_feed_the_findings_and_the_violations(
            self, target, findings_mapper_mock, violations_converter_mock
        ):
            # Act
            target.apply(EvaluateRulesParams(config=CONFIG, tree=TREE))

            # Assert
            findings_mapper_mock.apply.assert_called_once_with(CONFIG, TREE, SKIP_RULES)
            violations_converter_mock.apply.assert_called_once_with(FINDINGS, SKIP_RULES)

        def then_the_model_carries_the_project_tree_and_findings(self, target):
            # Act
            result = target.apply(EvaluateRulesParams(config=CONFIG, tree=TREE))

            # Assert
            assert (result.project, result.root, result.flow) == ("notes", "app", CONFIG.flow)
            assert (result.tree, result.findings, result.skip_rules) == (TREE, FINDINGS, SKIP_RULES)

    class WhenTheRootSitsOutsideTheConfigsDirectory:
        def then_the_model_names_it_in_full(self, target):
            # Arrange
            config = create_mock_arch_config(root=Path("/elsewhere/app"))

            # Act
            result = target.apply(EvaluateRulesParams(config=config, tree=TREE))

            # Assert
            assert result.root == "/elsewhere/app"
