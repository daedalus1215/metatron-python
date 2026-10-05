import os
import re
from pathlib import Path

from metatron.scan.domain.transaction_scripts.read_source_tree_ts.source_text_projection import (
    SourceTextProjection,
)
from metatron.shared.domain.ports.config_port import ConfigError


class SourceFileRepository:
    def read_tree(
        self, root: Path, ignore: tuple[re.Pattern[str], ...]
    ) -> tuple[SourceTextProjection, ...]:
        """Every `.py` file under `root`, in path order.

        `ignore` is tested against root-relative paths, so a project that
        happens to live under a `build/` directory is not ignored wholesale. An
        ignored directory is pruned, not walked.
        """
        if not root.is_dir():
            raise ConfigError(
                f"root not found: {root}\n"
                "Set `root` in [tool.metatron]; it is relative to the config file."
            )
        found: list[SourceTextProjection] = []
        for directory, subdirectories, files in os.walk(root):
            here = Path(directory).relative_to(root).as_posix()
            prefix = "" if here == "." else here + "/"
            subdirectories[:] = sorted(
                d for d in subdirectories if not self._ignored(f"{prefix}{d}/", ignore)
            )
            for name in sorted(files):
                path = prefix + name
                if name.endswith(".py") and not self._ignored(path, ignore):
                    text = (Path(directory) / name).read_text(encoding="utf-8", errors="replace")
                    found.append(SourceTextProjection(path=path, text=text))
        return tuple(sorted(found, key=lambda source: source.path))

    def local_top_level_names(self, source_roots: tuple[Path, ...]) -> frozenset[str]:
        """The names an absolute import can start with and still mean this project."""
        names: set[str] = set()
        for source_root in source_roots:
            if not source_root.is_dir():
                continue
            for entry in source_root.iterdir():
                if entry.name.startswith("."):
                    continue
                if entry.is_file() and entry.suffix == ".py":
                    names.add(entry.stem)
                elif entry.is_dir() and any(child.suffix == ".py" for child in entry.iterdir()):
                    names.add(entry.name)
        return frozenset(names)

    def _ignored(self, path: str, ignore: tuple[re.Pattern[str], ...]) -> bool:
        return any(pattern.search(path) for pattern in ignore)
