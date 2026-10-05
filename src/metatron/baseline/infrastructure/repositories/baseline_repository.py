import json
from pathlib import Path
from typing import Any

from metatron.baseline.domain.entities.baseline_entity import BaselineEntity, BaselineEntryEntity
from metatron.shared.domain.ports.config_port import ConfigError

FILENAME = "arch.baseline.json"


class BaselineRepository:
    """`arch.baseline.json`, beside the config: committed, unlike the generated output."""

    def path_in(self, directory: Path) -> Path:
        return directory / FILENAME

    def read(self, directory: Path) -> BaselineEntity | None:
        path = self.path_in(directory)
        if not path.is_file():
            return None
        try:
            document = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as error:
            raise ConfigError(f"{path} is not valid JSON: {error}") from error
        violations = document.get("violations") if isinstance(document, dict) else None
        if not isinstance(violations, dict):
            raise ConfigError(
                f'{path} has no "violations" object — delete it and re-run `metatron-py baseline`.'
            )
        return BaselineEntity(
            project=document.get("project", ""),
            entries={
                fingerprint: BaselineEntryEntity(
                    fingerprint=fingerprint,
                    rule=entry.get("rule", ""),
                    source=entry.get("from", ""),
                    target=entry.get("to", ""),
                    note=entry.get("note"),
                )
                for fingerprint, entry in violations.items()
            },
        )

    def write(self, directory: Path, document: dict[str, Any]) -> Path:
        path = self.path_in(directory)
        path.write_text(json.dumps(document, indent=2) + "\n", encoding="utf-8")
        return path
