from collections import Counter

from metatron.shared.domain.ports.model_port import CoverageProjection, SourceFileProjection


class CoverageConverter:
    """How much of the tree the config understood: the number printed before anything else."""

    def apply(self, files: tuple[SourceFileProjection, ...], fallback: str) -> CoverageProjection:
        unclassified = tuple(sorted(f.path for f in files if f.pattern == fallback))
        return CoverageProjection(
            files=len(files),
            classified=len(files) - len(unclassified),
            unclassified=unclassified,
            by_pattern=dict(sorted(Counter(f.pattern for f in files).items())),
        )
