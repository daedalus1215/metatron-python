from metatron.shared.domain.ports.model_port import ArchModelProjection


class UngatedFindingsConverter:
    """Warnings that cannot become violations: aggregates, or findings with no instances.

    Listed so that a rule cannot sit outside the gate without anyone noticing.
    """

    def apply(self, model: ArchModelProjection) -> tuple[str, ...]:
        return tuple(
            finding.id
            for finding in model.findings
            if finding.tone == "warn" and (not finding.gate or not finding.instances)
        )
