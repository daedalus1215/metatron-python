import tomllib
from pathlib import Path
from typing import Any

from metatron.config.domain.transaction_scripts.load_config_ts.config_table_projection import (
    ConfigTableProjection,
)
from metatron.shared.domain.ports.config_port import ConfigError

# metatron.toml first: a standalone file is the more deliberate of the two.
NAMES = ("metatron.toml", "pyproject.toml")


class ConfigFileRepository:
    def find(self, start: Path) -> ConfigTableProjection | None:
        """The nearest metatron table at or above `start`.

        A pyproject.toml with no [tool.metatron] is passed over.
        """
        here = start.resolve()
        directory = here.parent if here.is_file() else here
        for candidate in (directory, *directory.parents):
            for name in NAMES:
                file = candidate / name
                table = self._table(file) if file.is_file() else None
                if table is not None:
                    return ConfigTableProjection(file=file, table=table)
        return None

    def _table(self, file: Path) -> dict[str, Any] | None:
        try:
            document = tomllib.loads(file.read_text(encoding="utf-8"))
        except tomllib.TOMLDecodeError as error:
            raise ConfigError(f"{file} is not valid TOML: {error}") from error
        if file.name == "metatron.toml":
            return document
        return document.get("tool", {}).get("metatron")
