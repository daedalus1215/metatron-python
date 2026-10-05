import tomllib
from importlib import resources
from typing import Any

from metatron.shared.domain.ports.config_port import ConfigError


class ProfileRepository:
    """The bundled profiles, one TOML file each, read by name."""

    def read(self, name: str) -> dict[str, Any]:
        profiles = resources.files("metatron.config.infrastructure") / "profiles"
        available = sorted(
            entry.name.removesuffix(".toml")
            for entry in profiles.iterdir()
            if entry.name.endswith(".toml")
        )
        if name not in available:
            raise ConfigError(f'unknown profile "{name}" — available: {", ".join(available)}')
        return tomllib.loads((profiles / f"{name}.toml").read_text(encoding="utf-8"))
