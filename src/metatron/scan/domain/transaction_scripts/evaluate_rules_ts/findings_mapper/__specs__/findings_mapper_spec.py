import pytest

from metatron.scan.domain.transaction_scripts.evaluate_rules_ts.findings_mapper.absent_patterns_findings_converter import (  # noqa: E501
    AbsentPatternsFindingsConverter,
)
from metatron.scan.domain.transaction_scripts.evaluate_rules_ts.findings_mapper.circular_findings_converter import (  # noqa: E501
    CircularFindingsConverter,
)
from metatron.scan.domain.transaction_scripts.evaluate_rules_ts.findings_mapper.cross_domain_findings_converter import (  # noqa: E501
    CrossDomainFindingsConverter,
)
from metatron.scan.domain.transaction_scripts.evaluate_rules_ts.findings_mapper.findings_mapper import (  # noqa: E501
    FindingsMapper,
)
from metatron.scan.domain.transaction_scripts.evaluate_rules_ts.findings_mapper.forbidden_findings_converter import (  # noqa: E501
    ForbiddenFindingsConverter,
)
from metatron.scan.domain.transaction_scripts.evaluate_rules_ts.findings_mapper.layer_findings_converter import (  # noqa: E501
    LayerFindingsConverter,
)
from metatron.scan.domain.transaction_scripts.evaluate_rules_ts.findings_mapper.module_cycles_findings_converter import (  # noqa: E501
    ModuleCyclesFindingsConverter,
)
from metatron.scan.domain.transaction_scripts.evaluate_rules_ts.findings_mapper.naming_findings_converter import (  # noqa: E501
    NamingFindingsConverter,
)
from metatron.scan.domain.transaction_scripts.evaluate_rules_ts.findings_mapper.same_level_findings_converter import (  # noqa: E501
    SameLevelFindingsConverter,
)
from metatron.scan.domain.transaction_scripts.evaluate_rules_ts.findings_mapper.skip_findings_converter import (  # noqa: E501
    SkipFindingsConverter,
)
from metatron.scan.test_utils import create_mock_arch_config, create_mock_source_tree
from metatron.shared.domain.ports.model_port import FindingProjection
from metatron.shared.test_utils.test_utils import create_apply_mock

CONVERTERS = [
    CrossDomainFindingsConverter,
    ModuleCyclesFindingsConverter,
    SameLevelFindingsConverter,
    ForbiddenFindingsConverter,
    LayerFindingsConverter,
    SkipFindingsConverter,
    NamingFindingsConverter,
    CircularFindingsConverter,
    AbsentPatternsFindingsConverter,
]
CONFIG = create_mock_arch_config()
TREE = create_mock_source_tree({})
SKIP_RULES = ()


@pytest.fixture
def converter_mocks():
    mocks = []
    for converter in CONVERTERS:
        mock = create_apply_mock(converter)
        mock.apply.return_value = (FindingProjection(id=converter.__name__, tone="good", title=""),)
        mocks.append(mock)
    return mocks


@pytest.fixture
def target(converter_mocks):
    return FindingsMapper(*converter_mocks)


class GivenFindingsMapper:
    class WhenMapping:
        def then_every_rules_findings_come_back_in_reporting_order(self, target):
            # Act
            result = target.apply(CONFIG, TREE, SKIP_RULES)

            # Assert
            assert [f.id for f in result] == [c.__name__ for c in CONVERTERS]

        def then_the_skip_rules_go_to_the_skip_converter_and_the_tree_to_all(
            self, target, converter_mocks
        ):
            # Act
            target.apply(CONFIG, TREE, SKIP_RULES)

            # Assert
            skip = converter_mocks[CONVERTERS.index(SkipFindingsConverter)]
            circular = converter_mocks[CONVERTERS.index(CircularFindingsConverter)]
            skip.apply.assert_called_once_with(CONFIG, TREE, SKIP_RULES)
            circular.apply.assert_called_once_with(TREE)
