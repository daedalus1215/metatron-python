"""The architecture model a scan produces, and the port any context builds it through."""

from collections.abc import Mapping
from dataclasses import dataclass
from functools import cached_property
from typing import Protocol

from metatron.shared.domain.ports.config_port import ArchConfigProjection, TierProjection


@dataclass(frozen=True)
class SourceFileProjection:
    path: str
    module: str
    folder: str
    pattern: str
    tier: int
    loc: int


@dataclass(frozen=True)
class ImportEdgeProjection:
    source: str
    target: str
    line: int


@dataclass(frozen=True)
class DiagnosticProjection:
    """Something the scan declined to interpret, recorded rather than dropped."""

    kind: str
    file: str
    line: int
    detail: str


@dataclass(frozen=True)
class CoverageProjection:
    files: int
    classified: int
    unclassified: tuple[str, ...]
    by_pattern: Mapping[str, int]

    @property
    def percent(self) -> float:
        return round(100 * self.classified / self.files, 1) if self.files else 0.0


@dataclass(frozen=True)
class SourceTreeProjection:
    files: tuple[SourceFileProjection, ...]
    edges: tuple[ImportEdgeProjection, ...]
    externals: Mapping[str, int]
    diagnostics: tuple[DiagnosticProjection, ...]
    coverage: CoverageProjection

    @cached_property
    def by_path(self) -> Mapping[str, SourceFileProjection]:
        return {file.path: file for file in self.files}


@dataclass(frozen=True)
class SkipRuleProjection:
    """A flow station reaching past the next one: derived from `flow`, never hand-listed."""

    id: str
    source: str
    target: str
    severity: str
    jump: int
    why: str


@dataclass(frozen=True)
class InstanceProjection:
    """One offending (from, to) pair: what a baseline fingerprints."""

    source: str
    target: str


@dataclass(frozen=True)
class FindingProjection:
    id: str
    tone: str
    title: str
    detail: str = ""
    items: tuple[str, ...] = ()
    instances: tuple[InstanceProjection, ...] = ()
    gate: bool = True


@dataclass(frozen=True)
class ViolationProjection:
    fingerprint: str
    rule: str
    source: str
    target: str
    severity: str


@dataclass(frozen=True)
class ArchModelProjection:
    project: str
    root: str
    tiers: tuple[TierProjection, ...]
    flow: tuple[str, ...]
    skip_rules: tuple[SkipRuleProjection, ...]
    tree: SourceTreeProjection
    findings: tuple[FindingProjection, ...]
    violations: tuple[ViolationProjection, ...]


class ModelPort(Protocol):
    def build(self, config: ArchConfigProjection) -> ArchModelProjection:
        """The model of the tree `config` governs. Raises ConfigError."""
        ...
