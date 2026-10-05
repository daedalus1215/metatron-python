from pathlib import Path

import pytest

from metatron.config.domain.transaction_scripts.load_config_ts.arch_config_mapper.config_shape_validator import (  # noqa: E501
    ConfigShapeValidator,
)
from metatron.shared.domain.ports.config_port import ConfigError

FILE = Path("/code/notes/pyproject.toml")


class GivenConfigShapeValidator:
    class WhenEveryKeyIsKnownAndWellTyped:
        def then_it_passes(self):
            # Arrange
            table = {
                "root": "app",
                "flow": ["action", "service"],
                "flow-aliases": {"action": ["router"]},
                "fallback": {"id": "other", "tier": "Wiring"},
                "forbidden": [{"from": "a", "to": ["b"], "why": "up"}],
            }
            target = ConfigShapeValidator()

            # Act
            result = target.apply(table, FILE)

            # Assert
            assert result is None

    class WhenAKeyIsCamelCased:
        def then_it_raises_suggesting_the_kebab_case_key(self):
            # Arrange
            target = ConfigShapeValidator()

            # Act & Assert
            expected = r"`addPatterns` \(did you mean `add-patterns`\?\)"
            with pytest.raises(ConfigError, match=expected):
                target.apply({"addPatterns": []}, FILE)

    class WhenAKeyIsUnknown:
        def then_it_raises_listing_the_known_keys(self):
            # Arrange
            target = ConfigShapeValidator()

            # Act & Assert
            expected = "unknown key `colour`\n  known keys: add-patterns"
            with pytest.raises(ConfigError, match=expected):
                target.apply({"colour": "red"}, FILE)

    class WhenAStringIsGivenAList:
        def then_it_raises_naming_the_key(self):
            # Arrange
            target = ConfigShapeValidator()

            # Act & Assert
            with pytest.raises(ConfigError, match="`root` must be a string"):
                target.apply({"root": ["app"]}, FILE)

    class WhenAPatternHasNoTest:
        def then_it_raises_naming_the_entry_and_the_missing_key(self):
            # Arrange
            table = {"add-patterns": [{"id": "exception", "tier": "Contract"}]}
            target = ConfigShapeValidator()

            # Act & Assert
            with pytest.raises(ConfigError, match="`add-patterns` entry 1 has no `test`"):
                target.apply(table, FILE)

    class WhenATableListHoldsSomethingElse:
        def then_it_raises(self):
            # Arrange
            target = ConfigShapeValidator()

            # Act & Assert
            with pytest.raises(ConfigError, match="`tiers` must be a list of tables"):
                target.apply({"tiers": ["Entry"]}, FILE)

    class WhenFlowAliasesIsNotATableOfLists:
        def then_it_raises(self):
            # Arrange
            target = ConfigShapeValidator()

            # Act & Assert
            with pytest.raises(ConfigError, match="`flow-aliases` must map each station"):
                target.apply({"flow-aliases": {"action": "router"}}, FILE)

    class WhenFallbackIsNotATable:
        def then_it_raises(self):
            # Arrange
            target = ConfigShapeValidator()

            # Act & Assert
            with pytest.raises(ConfigError, match="`fallback` must be a table"):
                target.apply({"fallback": "other"}, FILE)
