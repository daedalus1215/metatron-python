import re
from collections.abc import Iterator
from pathlib import Path
from typing import Any

from metatron.shared.domain.ports.config_port import ConfigError


class ConfigReferencesValidator:
    """Every tier, regex and pattern id the merged config names exists.

    A rule naming a pattern no file can have never fires, and a gate that
    cannot fire passes everything. Only the rules the project wrote itself are
    checked for that: a profile rule about a pattern the project removed is the
    project's deliberate choice.
    """

    def apply(self, merged: dict[str, Any], project: dict[str, Any], config_file: Path) -> None:
        tiers = {tier["name"] for tier in merged["tiers"]}
        for pattern in [*merged["patterns"], merged["fallback"]]:
            if pattern["tier"] not in tiers:
                raise ConfigError(
                    f'{config_file}: pattern "{pattern["id"]}" names tier "{pattern["tier"]}",'
                    f" which is not in `tiers`"
                )
        for where, regex in self._regexes(merged):
            try:
                re.compile(regex)
            except re.error as error:
                message = f"{config_file}: {where} is not a valid regex: {error}"
                raise ConfigError(message) from error
        ids = {pattern["id"] for pattern in merged["patterns"]} | {merged["fallback"]["id"]}
        for key, named in self._references(project):
            if named not in ids:
                message = f'{config_file}: `{key}` names "{named}", which no pattern declares'
                raise ConfigError(message)

    def _regexes(self, merged: dict[str, Any]) -> Iterator[tuple[str, str]]:
        yield from ((f"`ignore` entry {i + 1}", r) for i, r in enumerate(merged.get("ignore", [])))
        yield from ((f'pattern "{p["id"]}"', p["test"]) for p in merged["patterns"])
        yield from ((f'naming rule "{n["id"]}"', n["test"]) for n in merged.get("naming", []))

    def _references(self, project: dict[str, Any]) -> Iterator[tuple[str, str]]:
        for key in ("flow", "no-same-level", "cross-domain-gateways"):
            yield from ((key, named) for named in project.get(key, []))
        for station, aliases in project.get("flow-aliases", {}).items():
            yield from (("flow-aliases", named) for named in (station, *aliases))
        for skip in project.get("allowed-skips", []):
            yield from (("allowed-skips", named) for named in skip.split(">"))
        for rule in project.get("forbidden", []):
            targets = [rule["to"]] if isinstance(rule["to"], str) else rule["to"]
            yield from (("forbidden", named) for named in (rule["from"], *targets))
