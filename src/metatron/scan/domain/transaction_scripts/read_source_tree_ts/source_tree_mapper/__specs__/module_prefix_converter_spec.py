from pathlib import Path

import pytest

from metatron.scan.domain.transaction_scripts.read_source_tree_ts.source_tree_mapper.module_prefix_converter import (  # noqa: E501
    ModulePrefixConverter,
)


@pytest.fixture
def target():
    return ModulePrefixConverter()


class GivenModulePrefixConverter:
    class WhenTheRootIsAPackageBelowTheSourceRoot:
        def then_the_prefix_is_its_dotted_path(self, target):
            # Act
            result = target.apply(Path("/x/src/metatron/scan"), (Path("/x/src"),))

            # Assert
            assert result == ("metatron.scan",)

    class WhenTheRootIsItselfASourceRoot:
        def then_the_first_prefix_is_empty(self, target):
            # Act
            result = target.apply(Path("/x/app"), (Path("/x/app"), Path("/x")))

            # Assert
            assert result == ("", "app")

    class WhenASourceRootDoesNotHoldTheRoot:
        def then_it_contributes_nothing(self, target):
            # Act
            result = target.apply(Path("/x/app"), (Path("/y"),))

            # Assert
            assert result == ()
