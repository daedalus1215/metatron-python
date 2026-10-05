import pytest

from metatron.scan.domain.transaction_scripts.read_source_tree_ts.source_tree_mapper.coverage_converter import (  # noqa: E501
    CoverageConverter,
)
from metatron.shared.domain.ports.model_port import CoverageProjection, SourceFileProjection


def file(path, pattern):
    return SourceFileProjection(
        path=path, module="notes", folder="notes", pattern=pattern, tier=0, loc=1
    )


@pytest.fixture
def target():
    return CoverageConverter()


class GivenCoverageConverter:
    class WhenSomeFilesFellThrough:
        def then_it_counts_them_and_lists_them_sorted(self, target):
            # Arrange
            files = (
                file("notes/b_service.py", "service"),
                file("notes/z_exception.py", "other"),
                file("notes/a_exception.py", "other"),
                file("notes/a_service.py", "service"),
            )

            # Act
            result = target.apply(files, "other")

            # Assert
            assert result == CoverageProjection(
                files=4,
                classified=2,
                unclassified=("notes/a_exception.py", "notes/z_exception.py"),
                by_pattern={"other": 2, "service": 2},
            )
            assert result.percent == 50.0

    class WhenTheTreeIsEmpty:
        def then_the_percentage_is_zero_rather_than_a_division_error(self, target):
            # Act
            result = target.apply((), "other")

            # Assert
            assert result.percent == 0.0
