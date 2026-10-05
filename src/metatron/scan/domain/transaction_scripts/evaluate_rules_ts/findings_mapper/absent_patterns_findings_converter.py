from metatron.shared.domain.ports.config_port import ArchConfigProjection
from metatron.shared.domain.ports.model_port import FindingProjection, SourceTreeProjection
from metatron.shared.utils.text_utils import count


class AbsentPatternsFindingsConverter:
    """`absent-patterns`: configured patterns no file has. A note, never a violation."""

    def apply(
        self, config: ArchConfigProjection, tree: SourceTreeProjection
    ) -> tuple[FindingProjection, ...]:
        present = {file.pattern for file in tree.files}
        absent = [pattern for pattern in config.patterns if pattern.id not in present]
        if not absent:
            return ()
        return (
            FindingProjection(
                id="absent-patterns",
                tone="note",
                title=f"{count(len(absent), 'configured pattern')} exist nowhere in the code",
                detail="Either the architecture describes shapes that were never built,"
                " or the config names patterns this project does not use.",
                items=tuple(f"{pattern.id} (tier {pattern.tier})" for pattern in absent),
            ),
        )
