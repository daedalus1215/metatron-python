import pytest

from metatron.scan.domain.transaction_scripts.evaluate_rules_ts.findings_mapper.circular_findings_converter import (  # noqa: E501
    CircularFindingsConverter,
)
from metatron.scan.test_utils import create_mock_source_tree
from metatron.shared.domain.ports.model_port import InstanceProjection

FILES = {"a.py": "other", "b.py": "other", "c.py": "other"}


@pytest.fixture
def target():
    return CircularFindingsConverter()


class GivenCircularFindingsConverter:
    class WhenThreeFilesImportRoundInALoop:
        def then_it_is_one_cycle_fingerprinted_by_its_first_file(self, target):
            # Arrange
            tree = create_mock_source_tree(
                FILES, [("a.py", "b.py"), ("b.py", "c.py"), ("c.py", "a.py")]
            )

            # Act
            result = target.apply(tree)

            # Assert
            assert (result[0].id, result[0].tone, result[0].title) == (
                "circular",
                "warn",
                "1 import cycle between files",
            )
            assert result[0].items == ("a.py  <->  b.py  <->  c.py",)
            assert result[0].instances == (InstanceProjection("a.py", "b.py,c.py"),)

    class WhenTheImportsFormNoLoop:
        def then_it_holds(self, target):
            # Arrange
            tree = create_mock_source_tree(FILES, [("a.py", "b.py"), ("b.py", "c.py")])

            # Act
            result = target.apply(tree)

            # Assert
            assert [(f.id, f.tone) for f in result] == [("circular", "good")]
