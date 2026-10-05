"""Test data for the baseline context's specs."""

from dataclasses import replace
from typing import Any

from metatron.baseline.domain.entities.baseline_entity import BaselineEntity, BaselineEntryEntity
from metatron.shared.domain.ports.config_port import TierProjection
from metatron.shared.domain.ports.model_port import (
    ArchModelProjection,
    CoverageProjection,
    FindingProjection,
    SourceTreeProjection,
    ViolationProjection,
)


def create_mock_violation(fingerprint: str, rule: str = "no-upward") -> ViolationProjection:
    return ViolationProjection(
        fingerprint=fingerprint,
        rule=rule,
        source=f"notes/{fingerprint}_from.py",
        target=f"notes/{fingerprint}_to.py",
        severity="warn",
    )


def create_mock_entry(fingerprint: str, rule: str = "no-upward", note: str | None = None):
    violation = create_mock_violation(fingerprint, rule)
    return BaselineEntryEntity(
        fingerprint=fingerprint,
        rule=rule,
        source=violation.source,
        target=violation.target,
        note=note,
    )


def create_mock_baseline(*entries: BaselineEntryEntity) -> BaselineEntity:
    return BaselineEntity(project="notes", entries={e.fingerprint: e for e in entries})


def create_mock_model(
    *violations: ViolationProjection, findings: tuple[FindingProjection, ...] = (), **overrides: Any
) -> ArchModelProjection:
    model = ArchModelProjection(
        project="notes",
        root="app",
        tiers=(TierProjection("Entry", ""),),
        flow=(),
        skip_rules=(),
        tree=SourceTreeProjection(
            files=(),
            edges=(),
            externals={},
            diagnostics=(),
            coverage=CoverageProjection(0, 0, (), {}),
        ),
        findings=findings,
        violations=violations,
    )
    return replace(model, **overrides)
