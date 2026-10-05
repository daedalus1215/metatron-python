import hashlib

from metatron.shared.domain.ports.model_port import (
    FindingProjection,
    SkipRuleProjection,
    ViolationProjection,
)


class ViolationsConverter:
    """Every instance of a gating warning, individually addressable.

    A count per rule cannot name the offender, and it passes a swap: one
    violation fixed and another introduced nets to zero. A fingerprint per
    instance names which, and catches the swap. `sha1(rule|from|to)[:12]` is
    metatron-nestjs's scheme, so a baseline reads the same in either tool.
    """

    def apply(
        self, findings: tuple[FindingProjection, ...], skip_rules: tuple[SkipRuleProjection, ...]
    ) -> tuple[ViolationProjection, ...]:
        severity = {rule.id: rule.severity for rule in skip_rules}
        violations: dict[str, ViolationProjection] = {}
        for finding in findings:
            if finding.tone != "warn" or not finding.gate:
                continue
            for instance in finding.instances:
                fingerprint = self._fingerprint(finding.id, instance.source, instance.target)
                violations.setdefault(
                    fingerprint,
                    ViolationProjection(
                        fingerprint=fingerprint,
                        rule=finding.id,
                        source=instance.source,
                        target=instance.target,
                        severity=severity.get(finding.id, "warn"),
                    ),
                )
        return tuple(sorted(violations.values(), key=lambda v: (v.rule, v.source, v.target)))

    def _fingerprint(self, rule: str, source: str, target: str) -> str:
        return hashlib.sha1(f"{rule}|{source}|{target}".encode()).hexdigest()[:12]
