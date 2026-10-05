import pytest

from metatron.scan.domain.transaction_scripts.evaluate_rules_ts.findings_mapper.absent_patterns_findings_converter import (  # noqa: E501
    AbsentPatternsFindingsConverter,
)
from metatron.scan.test_utils import (
    create_mock_arch_config,
    create_mock_pattern,
    create_mock_source_tree,
)

CONFIG = create_mock_arch_config(
    patterns=(
        create_mock_pattern("service", "Service", r"_service\.py$"),
        create_mock_pattern("mapper", "Mapping", r"_mapper\.py$"),
    )
)


@pytest.fixture
def target():
    return AbsentPatternsFindingsConverter()


class GivenAbsentPatternsFindingsConverter:
    class WhenAPatternMatchesNoFile:
        def then_it_is_noted_with_its_tier(self, target):
            # Arrange
            tree = create_mock_source_tree({"notes/note_service.py": "service"})

            # Act
            result = target.apply(CONFIG, tree)

            # Assert
            assert [(f.id, f.tone, f.items) for f in result] == [
                ("absent-patterns", "note", ("mapper (tier Mapping)",))
            ]

    class WhenEveryPatternIsUsed:
        def then_there_is_nothing_to_note(self, target):
            # Arrange
            tree = create_mock_source_tree(
                {"notes/note_service.py": "service", "notes/note_mapper.py": "mapper"}
            )

            # Act
            result = target.apply(CONFIG, tree)

            # Assert
            assert result == ()
