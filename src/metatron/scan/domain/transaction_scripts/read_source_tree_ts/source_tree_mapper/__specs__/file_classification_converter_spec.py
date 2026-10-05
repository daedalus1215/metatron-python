import pytest

from metatron.scan.domain.transaction_scripts.read_source_tree_ts.source_tree_mapper.file_classification_converter import (  # noqa: E501
    FileClassificationConverter,
)
from metatron.scan.domain.transaction_scripts.read_source_tree_ts.source_tree_mapper.file_classification_projection import (  # noqa: E501
    FileClassificationProjection,
)
from metatron.scan.test_utils import TIER_NAMES, create_mock_arch_config

CONFIG = create_mock_arch_config()


@pytest.fixture
def target():
    return FileClassificationConverter()


class GivenFileClassificationConverter:
    class WhenAPathMatchesAPattern:
        def then_it_takes_that_pattern_and_its_tiers_index(self, target):
            # Act
            result = target.apply("notes/domain/services/note_service.py", CONFIG)

            # Assert
            assert result == FileClassificationProjection(
                pattern="service", tier=TIER_NAMES.index("Service")
            )

    class WhenAPathMatchesSeveralPatterns:
        def then_the_first_in_config_order_wins(self, target):
            # Act
            result = target.apply("notes/domain/services/__specs__/note_service_spec.py", CONFIG)

            # Assert
            assert result.pattern == "spec"

    class WhenAPathMatchesNoPattern:
        def then_it_takes_the_fallback(self, target):
            # Act
            result = target.apply("notes/domain/not_found_exception.py", CONFIG)

            # Assert
            assert result == FileClassificationProjection(
                pattern="other", tier=TIER_NAMES.index("Wiring")
            )
