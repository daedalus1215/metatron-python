"""The architecture model a scan produces, and the port any context builds it through."""

from collections.abc import Mapping
from dataclasses import dataclass
from functools import cached_property


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
