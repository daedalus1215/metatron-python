import pytest

from metatron.config.infrastructure.repositories.profile_repository import ProfileRepository
from metatron.shared.domain.ports.config_port import ConfigError


class GivenProfileRepository:
    class WhenReadingTheFastapiProfile:
        def then_it_returns_the_profile_table(self):
            # Arrange
            target = ProfileRepository()

            # Act
            result = target.read("fastapi")

            # Assert
            assert result["flow"] == ["action", "service", "transaction-script", "repository"]
            assert result["fallback"] == {"id": "other", "tier": "Wiring"}

    class WhenTheProfileDoesNotExist:
        def then_it_raises_naming_the_available_ones(self):
            # Arrange
            target = ProfileRepository()

            # Act & Assert
            with pytest.raises(ConfigError, match='unknown profile "django" — available: fastapi'):
                target.read("django")
