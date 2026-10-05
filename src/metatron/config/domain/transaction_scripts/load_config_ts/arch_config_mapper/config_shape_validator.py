import re
from pathlib import Path
from typing import Any

from metatron.shared.domain.ports.config_port import ConfigError

STRINGS = frozenset({"extends", "root", "name", "out-dir"})
STRING_LISTS = frozenset(
    {
        "source-roots",
        "ignore",
        "flow",
        "allowed-skips",
        "no-same-level",
        "infra-modules",
        "cross-domain-gateways",
    }
)
# Each entry of these is a table with the listed keys required.
TABLE_LISTS = {
    "tiers": ("name",),
    "patterns": ("id", "tier", "test"),
    "add-patterns": ("id", "tier", "test"),
    "forbidden": ("from", "to"),
    "layers": ("id", "from", "to"),
    "naming": ("id", "test"),
}
TABLES = {"fallback": ("id", "tier"), "flow-aliases": ()}
KNOWN = STRINGS | STRING_LISTS | TABLE_LISTS.keys() | TABLES.keys()


class ConfigShapeValidator:
    """Every key a project writes is one metatron reads, holding the type it expects.

    An unknown key would otherwise be ignored, and the scan would run on
    defaults while looking configured.
    """

    def apply(self, table: dict[str, Any], config_file: Path) -> None:
        unknown = sorted(set(table) - KNOWN)
        if unknown:
            raise ConfigError(
                f"{config_file}: unknown key{'s' if len(unknown) > 1 else ''} "
                + ", ".join(f"`{key}`{self._hint(key)}" for key in unknown)
                + f"\n  known keys: {', '.join(sorted(KNOWN))}"
            )
        for key, value in table.items():
            problem = self._problem(key, value)
            if problem:
                raise ConfigError(f"{config_file}: `{key}` {problem}")

    def _hint(self, key: str) -> str:
        kebab = re.sub(r"(?<!^)(?=[A-Z])", "-", key).lower().replace("_", "-")
        return f" (did you mean `{kebab}`?)" if kebab in KNOWN else ""

    def _problem(self, key: str, value: Any) -> str | None:
        if key in STRINGS:
            return None if isinstance(value, str) else "must be a string"
        if key in STRING_LISTS:
            return None if self._strings(value) else "must be a list of strings"
        if key in TABLE_LISTS:
            if not isinstance(value, list) or not all(isinstance(v, dict) for v in value):
                return "must be a list of tables"
            return self._missing(value, TABLE_LISTS[key])
        if key == "flow-aliases":
            ok = isinstance(value, dict) and all(self._strings(v) for v in value.values())
            return None if ok else "must map each station to a list of pattern ids"
        if not isinstance(value, dict):
            return "must be a table"
        return self._missing([value], TABLES[key])

    def _missing(self, entries: list[dict[str, Any]], required: tuple[str, ...]) -> str | None:
        for index, entry in enumerate(entries):
            absent = [k for k in required if k not in entry]
            if absent:
                return f"entry {index + 1} has no `{absent[0]}`"
        return None

    def _strings(self, value: Any) -> bool:
        return isinstance(value, list) and all(isinstance(v, str) for v in value)
