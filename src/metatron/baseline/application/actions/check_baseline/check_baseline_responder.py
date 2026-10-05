import json

from metatron.baseline.domain.entities.baseline_entity import BaselineEntryEntity
from metatron.baseline.domain.transaction_scripts.compare_baseline_ts.baseline_check_projection import (  # noqa: E501
    BaselineCheckProjection,
)
from metatron.shared.domain.ports.model_port import ViolationProjection
from metatron.shared.utils.text_utils import count

UPDATE = "`metatron-py baseline --update`"


class CheckBaselineResponder:
    """What `metatron-py check` prints: new first, then fixed, then known, then the verdict."""

    def apply(self, check: BaselineCheckProjection, show_fixed: bool, as_json: bool) -> str:
        return self._json(check) if as_json else self._text(check, show_fixed)

    def _text(self, check: BaselineCheckProjection, show_fixed: bool) -> str:
        lines = [f"metatron check · {check.project}", ""]
        lines += [f"  new violations        {len(check.added)}", *self._pairs(check.added)]
        if check.added_out_of_scope:
            lines += [
                "",
                f"  new, outside --rule   {len(check.added_out_of_scope)}  (reported, not gated)",
                *self._pairs(check.added_out_of_scope),
            ]
        if show_fixed and check.fixed:
            lines += ["", f"  fixed since baseline  {len(check.fixed)}", *self._pairs(check.fixed)]
        lines += [
            "",
            f"  known, unchanged      {check.unchanged}",
            "",
            self._verdict(check, show_fixed),
        ]
        return "\n".join(lines)

    def _verdict(self, check: BaselineCheckProjection, show_fixed: bool) -> str:
        if check.failed:
            allowed = f" (allowed {check.allow_new})" if check.allow_new else ""
            return (
                f"FAIL — {count(len(check.added), 'new violation')}{allowed}."
                f" Fix it, or run {UPDATE} to accept it."
            )
        if show_fixed and check.fixed:
            # Never removed automatically: a scan that failed to parse a file
            # would otherwise retire a real debt, and it would return as "new".
            return (
                f"PASS — no new violations. {len(check.fixed)} fixed; run {UPDATE} to record that."
            )
        return "PASS — no new violations."

    def _pairs(self, found: tuple[ViolationProjection | BaselineEntryEntity, ...]) -> list[str]:
        return [
            f"    {v.rule:<22}{v.source}" + (f"\n{' ' * 26}-> {v.target}" if v.target else "")
            for v in found
        ]

    def _json(self, check: BaselineCheckProjection) -> str:
        def violation(v: ViolationProjection) -> dict[str, str]:
            return {
                "fingerprint": v.fingerprint,
                "rule": v.rule,
                "from": v.source,
                "to": v.target,
                "sev": v.severity,
            }

        return json.dumps(
            {
                "project": check.project,
                "ok": not check.failed,
                "allowNew": check.allow_new,
                "rules": list(check.rules) or None,
                "total": check.total,
                "unchanged": check.unchanged,
                "added": [violation(v) for v in check.added],
                "addedOutOfScope": [violation(v) for v in check.added_out_of_scope],
                "fixed": [
                    {"fingerprint": e.fingerprint, "rule": e.rule, "from": e.source, "to": e.target}
                    | ({"note": e.note} if e.note else {})
                    for e in check.fixed
                ],
            },
            indent=2,
        )
