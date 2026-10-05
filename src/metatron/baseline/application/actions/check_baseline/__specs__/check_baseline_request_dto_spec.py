import argparse
from pathlib import Path

import pytest

from metatron.baseline.application.actions.check_baseline.check_baseline_request_dto import (
    CheckBaselineRequestDTO,
)


@pytest.fixture
def parser():
    parser = argparse.ArgumentParser()
    CheckBaselineRequestDTO.add_arguments(parser)
    return parser


class GivenCheckBaselineRequestDTO:
    class WhenNoFlagsAreGiven:
        def then_it_gates_everything_here_listing_fixed_ones_as_text(self, parser):
            # Act
            result = CheckBaselineRequestDTO.from_namespace(parser.parse_args([]))

            # Assert
            assert result == CheckBaselineRequestDTO(
                path=Path("."), rules=(), allow_new=0, show_fixed=True, as_json=False
            )

    class WhenEveryFlagIsGiven:
        def then_each_is_read(self, parser):
            # Arrange
            argv = ["app", "--rule", "circular", "--rule", "no-upward", "--allow-new", "3"]
            argv += ["--no-fixed", "--json"]

            # Act
            result = CheckBaselineRequestDTO.from_namespace(parser.parse_args(argv))

            # Assert
            assert result == CheckBaselineRequestDTO(
                path=Path("app"),
                rules=("circular", "no-upward"),
                allow_new=3,
                show_fixed=False,
                as_json=True,
            )
