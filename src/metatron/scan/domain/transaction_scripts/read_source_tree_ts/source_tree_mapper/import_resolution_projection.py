from dataclasses import dataclass


@dataclass(frozen=True)
class ImportContextProjection:
    """What every import in a tree is resolved against."""

    files: frozenset[str]
    prefixes: tuple[str, ...]
    local_names: frozenset[str]


@dataclass(frozen=True)
class ImportResolutionProjection:
    """Scanned files the import lands on, or the external package it names, or neither."""

    targets: tuple[str, ...] = ()
    external: str | None = None

    @property
    def unresolved(self) -> bool:
        return not self.targets and self.external is None
