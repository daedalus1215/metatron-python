import posixpath

from metatron.scan.domain.utils.text_utils import count
from metatron.shared.domain.ports.config_port import ArchConfigProjection
from metatron.shared.domain.ports.model_port import (
    FindingProjection,
    InstanceProjection,
    SourceTreeProjection,
)


class SameLevelFindingsConverter:
    """`no-same-level`: a file importing another of its own `no-same-level` pattern.

    Two such files in one directory are a helper split and are only mentioned.
    The directory is the file's own, not metatron-nestjs's three-segment folder:
    every `*_ts/` sits under one `transaction_scripts/`, and a transaction
    script importing another is exactly what the rule is for.
    """

    def apply(
        self, config: ArchConfigProjection, tree: SourceTreeProjection
    ) -> tuple[FindingProjection, ...]:
        same = [
            edge
            for edge in tree.edges
            if tree.by_path[edge.source].pattern == tree.by_path[edge.target].pattern
            and tree.by_path[edge.source].pattern in config.no_same_level
        ]
        split = [e for e in same if posixpath.dirname(e.source) == posixpath.dirname(e.target)]
        hits = [edge for edge in same if edge not in split]
        detail = f"Checked among {', '.join(config.no_same_level)}." + (
            f" {count(len(split), 'same-pattern import')} inside one directory"
            " treated as a helper split."
            if split
            else ""
        )
        return (
            FindingProjection(
                id="no-same-level",
                tone="warn" if hits else "good",
                title=f"{count(len(hits), 'same-level import')}"
                if hits
                else "No same-level injection",
                detail=detail,
                items=tuple(
                    f"[{tree.by_path[e.source].pattern}] {e.source} -> {e.target}"
                    for e in (hits or split)
                ),
                instances=tuple(InstanceProjection(e.source, e.target) for e in hits),
            ),
        )
