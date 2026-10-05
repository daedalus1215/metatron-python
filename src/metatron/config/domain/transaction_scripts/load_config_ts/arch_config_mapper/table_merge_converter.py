from typing import Any


class TableMergeConverter:
    """A project's table laid over its profile.

    Each key the project sets replaces the profile's wholesale, except
    `add-patterns`, which is prepended to the patterns in effect so a project can
    refine the profile without restating it.
    """

    def apply(self, profile: dict[str, Any], project: dict[str, Any]) -> dict[str, Any]:
        merged = {**profile, **project}
        merged.pop("extends", None)
        added = merged.pop("add-patterns", [])
        merged["patterns"] = [*added, *merged.get("patterns", [])]
        return merged
