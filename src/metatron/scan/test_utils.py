"""Test data for the scan context's specs."""

import posixpath
import re
from collections.abc import Iterable, Mapping
from dataclasses import replace
from pathlib import Path
from typing import Any

from metatron.shared.domain.ports.config_port import (
    ArchConfigProjection,
    PatternProjection,
    TierProjection,
)
from metatron.shared.domain.ports.model_port import (
    ArchModelProjection,
    CoverageProjection,
    ImportEdgeProjection,
    SourceFileProjection,
    SourceTreeProjection,
)

TIER_NAMES = (
    "Entry",
    "Contract",
    "Service",
    "Aggregator",
    "Transaction Script",
    "Mapping",
    "Persistence",
    "Domain Model",
    "Wiring",
    "Platform",
    "Test",
)


def create_mock_pattern(id: str, tier: str, test: str) -> PatternProjection:
    return PatternProjection(id=id, tier=tier, test=re.compile(test))


PATTERNS = (
    create_mock_pattern("spec", "Test", r"_spec\.py$|(^|/)__specs__/"),
    create_mock_pattern("converter", "Mapping", r"_converter\.py$"),
    create_mock_pattern("mapper", "Mapping", r"_mapper\.py$"),
    create_mock_pattern("module", "Wiring", r"_module\.py$"),
    create_mock_pattern("action", "Entry", r"_action\.py$"),
    create_mock_pattern("router", "Entry", r"_router\.py$"),
    create_mock_pattern("transaction-script", "Transaction Script", r"_transaction_script\.py$"),
    create_mock_pattern("aggregator", "Aggregator", r"_aggregator\.py$"),
    create_mock_pattern("service", "Service", r"_service\.py$"),
    create_mock_pattern("repository", "Persistence", r"_repository\.py$"),
    create_mock_pattern("port", "Domain Model", r"_port\.py$"),
    create_mock_pattern("package", "Wiring", r"(^|/)__init__\.py$"),
)


def create_mock_arch_config(**overrides: Any) -> ArchConfigProjection:
    config = ArchConfigProjection(
        name="notes",
        config_file=Path("/code/notes/pyproject.toml"),
        directory=Path("/code/notes"),
        root=Path("/code/notes/app"),
        source_roots=(Path("/code/notes"),),
        out_dir=Path("/code/notes/.metatron"),
        ignore=(),
        tiers=tuple(TierProjection(name=name, sub="") for name in TIER_NAMES),
        patterns=PATTERNS,
        fallback="other",
        fallback_tier="Wiring",
        flow=("action", "service", "transaction-script", "repository"),
        flow_aliases={"action": ("router",)},
        allowed_skips=(),
        forbidden=(),
        layers=(),
        no_same_level=("transaction-script", "service", "converter", "mapper"),
        infra_modules=("shared",),
        cross_domain_gateways=("aggregator", "port"),
        naming=(),
    )
    return replace(config, **overrides)


def create_mock_source_tree(
    files: Mapping[str, str], edges: Iterable[tuple[str, str]] = ()
) -> SourceTreeProjection:
    """A tree from `{path: pattern}` and `(from, to)` pairs; module and folder follow the path."""
    projections = tuple(
        SourceFileProjection(
            path=path,
            module=path.split("/")[0] if "/" in path else "(root)",
            folder=posixpath.dirname(path) or "(root)",
            pattern=pattern,
            tier=0,
            loc=1,
        )
        for path, pattern in files.items()
    )
    return SourceTreeProjection(
        files=projections,
        edges=tuple(ImportEdgeProjection(source, target, 1) for source, target in edges),
        externals={},
        diagnostics=(),
        coverage=CoverageProjection(len(files), len(files), (), {}),
    )


def create_mock_arch_model(**overrides: Any) -> ArchModelProjection:
    model = ArchModelProjection(
        project="notes",
        root="app",
        tiers=create_mock_arch_config().tiers,
        flow=("action", "service"),
        skip_rules=(),
        tree=create_mock_source_tree({}),
        findings=(),
        violations=(),
    )
    return replace(model, **overrides)
