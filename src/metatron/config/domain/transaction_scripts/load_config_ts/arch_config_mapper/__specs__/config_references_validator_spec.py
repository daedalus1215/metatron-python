from pathlib import Path

import pytest

from metatron.config.domain.transaction_scripts.load_config_ts.arch_config_mapper.config_references_validator import (  # noqa: E501
    ConfigReferencesValidator,
)
from metatron.config.infrastructure.repositories.profile_repository import ProfileRepository
from metatron.shared.domain.ports.config_port import ConfigError

FILE = Path("/code/notes/pyproject.toml")


def merged(**overrides):
    return {
        "tiers": [{"name": "Entry"}, {"name": "Service"}, {"name": "Wiring"}],
        "patterns": [
            {"id": "action", "tier": "Entry", "test": "_action\\.py$"},
            {"id": "service", "tier": "Service", "test": "_service\\.py$"},
        ],
        "fallback": {"id": "other", "tier": "Wiring"},
        **overrides,
    }


class GivenConfigReferencesValidator:
    class WhenTheBundledProfileIsCheckedAsIfAProjectWroteIt:
        def then_every_reference_in_it_resolves(self):
            # Arrange
            profile = ProfileRepository().read("fastapi")
            target = ConfigReferencesValidator()

            # Act
            result = target.apply(profile, profile, FILE)

            # Assert
            assert result is None

    class WhenAPatternNamesATierThatDoesNotExist:
        def then_it_raises_naming_both(self):
            # Arrange
            config = merged(patterns=[{"id": "dto", "tier": "Contract", "test": "_dto"}])
            target = ConfigReferencesValidator()

            # Act & Assert
            expected = 'pattern "dto" names tier "Contract", which is not in `tiers`'
            with pytest.raises(ConfigError, match=expected):
                target.apply(config, {}, FILE)

    class WhenAPatternRegexDoesNotCompile:
        def then_it_raises_naming_the_pattern(self):
            # Arrange
            config = merged(patterns=[{"id": "action", "tier": "Entry", "test": "(unclosed"}])
            target = ConfigReferencesValidator()

            # Act & Assert
            with pytest.raises(ConfigError, match='pattern "action" is not a valid regex'):
                target.apply(config, {}, FILE)

    class WhenTheProjectsFlowNamesAnUnknownPattern:
        def then_it_raises_naming_the_key_and_the_id(self):
            # Arrange
            project = {"flow": ["action", "servise"]}
            target = ConfigReferencesValidator()

            # Act & Assert
            expected = '`flow` names "servise", which no pattern declares'
            with pytest.raises(ConfigError, match=expected):
                target.apply(merged(**project), project, FILE)

    class WhenTheProjectsForbiddenRuleTargetsAnUnknownPattern:
        def then_it_raises(self):
            # Arrange
            project = {"forbidden": [{"from": "service", "to": ["action", "nope"]}]}
            target = ConfigReferencesValidator()

            # Act & Assert
            with pytest.raises(ConfigError, match='`forbidden` names "nope"'):
                target.apply(merged(**project), project, FILE)

    class WhenAnInheritedRuleNamesAPatternTheProjectRemoved:
        def then_it_passes(self):
            # Arrange
            config = merged(flow=["action", "service", "repository"])
            target = ConfigReferencesValidator()

            # Act
            result = target.apply(config, {}, FILE)

            # Assert
            assert result is None
