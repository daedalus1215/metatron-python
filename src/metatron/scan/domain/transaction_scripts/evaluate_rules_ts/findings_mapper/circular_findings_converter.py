from metatron.scan.domain.utils.graph_utils import cycles
from metatron.shared.domain.ports.model_port import (
    FindingProjection,
    InstanceProjection,
    SourceTreeProjection,
)
from metatron.shared.utils.text_utils import count


class CircularFindingsConverter:
    """`circular`: files that import each other, however far round.

    An import under `if TYPE_CHECKING:` counts. It does not fail at runtime, but
    the two files still cannot be understood apart.
    """

    def apply(self, tree: SourceTreeProjection) -> tuple[FindingProjection, ...]:
        loops = cycles((edge.source, edge.target) for edge in tree.edges)
        if not loops:
            return (FindingProjection(id="circular", tone="good", title="No circular imports"),)
        return (
            FindingProjection(
                id="circular",
                tone="warn",
                title=f"{count(len(loops), 'import cycle')} between files",
                detail="Files that reach themselves through their imports.",
                items=tuple("  <->  ".join(loop) for loop in loops),
                instances=tuple(InstanceProjection(loop[0], ",".join(loop[1:])) for loop in loops),
            ),
        )
