import pytest

from metatron.scan.domain.transaction_scripts.evaluate_rules_ts.findings_mapper.cross_domain_findings_converter import (  # noqa: E501
    CrossDomainFindingsConverter,
)
from metatron.scan.test_utils import create_mock_arch_config, create_mock_source_tree
from metatron.shared.domain.ports.model_port import InstanceProjection

CONFIG = create_mock_arch_config()
FILES = {
    "notes/domain/note_service.py": "service",
    "notes/notes_module.py": "module",
    "users/domain/user_service.py": "service",
    "users/domain/users_aggregator.py": "aggregator",
    "shared/ports/users_port.py": "port",
    "main.py": "bootstrap",
}


@pytest.fixture
def target():
    return CrossDomainFindingsConverter()


class GivenCrossDomainFindingsConverter:
    class WhenAContextImportsAnothersService:
        def then_it_bypasses_the_gateways(self, target):
            # Arrange
            edge = ("notes/domain/note_service.py", "users/domain/user_service.py")
            tree = create_mock_source_tree(FILES, [edge])

            # Act
            result = target.apply(CONFIG, tree)

            # Assert
            assert (result[0].id, result[0].tone) == ("cross-domain", "warn")
            assert result[0].items == ("notes/service -> users/domain/user_service.py",)
            assert result[0].instances == (InstanceProjection(*edge),)

    class WhenAContextLandsOnAnothersAggregator:
        def then_the_gateway_holds(self, target):
            # Arrange
            tree = create_mock_source_tree(
                FILES, [("notes/domain/note_service.py", "users/domain/users_aggregator.py")]
            )

            # Act
            result = target.apply(CONFIG, tree)

            # Assert
            assert result[0].tone == "good"
            assert result[0].detail.startswith("1 import cross")

    class WhenWiringBootstrapOrInfraModulesCross:
        def then_they_are_set_aside(self, target):
            # Arrange
            tree = create_mock_source_tree(
                FILES,
                [
                    ("notes/notes_module.py", "users/domain/user_service.py"),
                    ("main.py", "users/domain/user_service.py"),
                    ("notes/domain/note_service.py", "shared/ports/users_port.py"),
                ],
            )

            # Act
            result = target.apply(CONFIG, tree)

            # Assert
            assert result[0].tone == "good"
            assert result[0].detail.startswith("0 imports cross")
