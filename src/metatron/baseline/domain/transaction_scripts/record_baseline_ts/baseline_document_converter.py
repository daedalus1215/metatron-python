from metatron.baseline.domain.entities.baseline_entity import BaselineEntity
from metatron.baseline.domain.transaction_scripts.record_baseline_ts.baseline_document_projection import (  # noqa: E501
    BaselineDocumentProjection,
)
from metatron.shared.domain.ports.model_port import ArchModelProjection


class BaselineDocumentConverter:
    """Today's violations as a baseline document, carrying forward every note still attached.

    A note is the only record of why a violation is tolerated; losing them on
    every refresh is how a baseline decays into an unexamined list. A note whose
    violation is gone goes with it, and is counted as dropped, not kept.
    """

    def apply(
        self, model: ArchModelProjection, previous: BaselineEntity | None
    ) -> BaselineDocumentProjection:
        notes = {
            fingerprint: entry.note
            for fingerprint, entry in (previous.entries.items() if previous else ())
            if entry.note
        }
        violations = {
            v.fingerprint: {"rule": v.rule, "from": v.source, "to": v.target}
            | ({"note": notes[v.fingerprint]} if v.fingerprint in notes else {})
            for v in model.violations
        }
        kept = sum(1 for fingerprint in violations if fingerprint in notes)
        return BaselineDocumentProjection(
            document={"version": 1, "project": model.project, "violations": violations},
            count=len(violations),
            kept=kept,
            dropped=len(notes) - kept,
        )
