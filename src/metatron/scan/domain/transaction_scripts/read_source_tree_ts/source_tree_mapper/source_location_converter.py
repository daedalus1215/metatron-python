from metatron.scan.domain.transaction_scripts.read_source_tree_ts.source_tree_mapper.source_location_projection import (  # noqa: E501
    SourceLocationProjection,
)

ROOT = "(root)"


class SourceLocationConverter:
    """A path's bounded context and its folder.

    The module is the first segment; a file at the top has no module of its
    own. The folder goes at most three segments deep, as in metatron-nestjs, so
    `notes/domain/services/x/y.py` and `notes/domain/services/z.py` share one.
    """

    def apply(self, path: str) -> SourceLocationProjection:
        parts = path.split("/")
        if len(parts) == 1:
            return SourceLocationProjection(module=ROOT, folder=ROOT)
        if len(parts) == 2:
            return SourceLocationProjection(module=parts[0], folder=f"{parts[0]}/{ROOT}")
        return SourceLocationProjection(
            module=parts[0], folder="/".join(parts[: min(3, len(parts) - 1)])
        )
