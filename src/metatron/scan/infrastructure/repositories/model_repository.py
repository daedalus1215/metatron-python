import json
from pathlib import Path
from typing import Any

FILENAME = "model.json"


class ModelRepository:
    def save(self, document: dict[str, Any], out_dir: Path) -> Path:
        out_dir.mkdir(parents=True, exist_ok=True)
        path = out_dir / FILENAME
        path.write_text(json.dumps(document, separators=(",", ":")) + "\n", encoding="utf-8")
        return path
