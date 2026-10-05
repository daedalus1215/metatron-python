"""The config a scan runs under, and the port any context loads it through."""

import re
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import Protocol


class ConfigError(Exception):
    """The config cannot be found, read, or trusted. A tool error, not a finding."""


@dataclass(frozen=True)
class TierProjection:
    name: str
    sub: str


@dataclass(frozen=True)
class PatternProjection:
    id: str
    tier: str
    test: re.Pattern[str]


@dataclass(frozen=True)
class ForbiddenProjection:
    source: str
    target: str
    why: str


@dataclass(frozen=True)
class LayerRuleProjection:
    id: str
    source: str
    target: str
    why: str


@dataclass(frozen=True)
class NamingRuleProjection:
    id: str
    title: str
    test: re.Pattern[str]
    why: str


@dataclass(frozen=True)
class ArchConfigProjection:
    name: str
    config_file: Path
    directory: Path
    root: Path
    source_roots: tuple[Path, ...]
    out_dir: Path
    ignore: tuple[re.Pattern[str], ...]
    tiers: tuple[TierProjection, ...]
    patterns: tuple[PatternProjection, ...]
    fallback: str
    fallback_tier: str
    flow: tuple[str, ...]
    flow_aliases: Mapping[str, tuple[str, ...]]
    allowed_skips: tuple[str, ...]
    forbidden: tuple[ForbiddenProjection, ...]
    layers: tuple[LayerRuleProjection, ...]
    no_same_level: tuple[str, ...]
    infra_modules: tuple[str, ...]
    cross_domain_gateways: tuple[str, ...]
    naming: tuple[NamingRuleProjection, ...]
    name_warning: str | None = None


class ConfigPort(Protocol):
    def load(self, start: Path) -> ArchConfigProjection:
        """The config governing `start`. Raises ConfigError."""
        ...
