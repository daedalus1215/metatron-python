import re
from pathlib import Path

from metatron.config.domain.transaction_scripts.load_config_ts.arch_config_mapper.project_name_projection import (  # noqa: E501
    ProjectNameProjection,
)

# Containers, not project names: a config in backend/ names the folder above it.
GENERIC = frozenset(
    {
        "backend",
        "frontend",
        "client",
        "web",
        "src",
        "api",
        "server",
        "app",
        "apps",
        "packages",
        "services",
    }
)


class ProjectNameConverter:
    def apply(self, config_file: Path, configured: str | None) -> ProjectNameProjection:
        inferred = self._inferred(config_file.parent)
        if configured is None:
            return ProjectNameProjection(name=inferred)
        if self._loosely_matches(configured, inferred):
            return ProjectNameProjection(name=configured)
        # Almost always a config copied from another project with its name left behind.
        return ProjectNameProjection(
            name=configured,
            warning=(
                f'config name is "{configured}" but it sits in "{inferred}"'
                f" — copied from another project?\n  {config_file}"
            ),
        )

    def _inferred(self, directory: Path) -> str:
        candidates = [directory, *directory.parents][:3]
        named = next((d.name for d in candidates if d.name.lower() not in GENERIC), None)
        return named or directory.name

    def _loosely_matches(self, a: str, b: str) -> bool:
        """So that `chronus` is happy inside `chronus-python-fastapi`."""
        left, right = (re.sub(r"[^a-z0-9]", "", x.lower()) for x in (a, b))
        return not left or not right or left in right or right in left
