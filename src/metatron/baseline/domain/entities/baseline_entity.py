from collections.abc import Mapping
from dataclasses import dataclass


@dataclass(frozen=True)
class BaselineEntryEntity:
    """One accepted violation, and the hand-written reason it is tolerated, if anyone gave one."""

    fingerprint: str
    rule: str
    source: str
    target: str
    note: str | None = None


@dataclass(frozen=True)
class BaselineEntity:
    """`arch.baseline.json`: the violations a project has accepted, by fingerprint."""

    project: str
    entries: Mapping[str, BaselineEntryEntity]
