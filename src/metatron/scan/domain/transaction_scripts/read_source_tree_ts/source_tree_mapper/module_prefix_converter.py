from pathlib import Path


class ModulePrefixConverter:
    """The dotted name the scanned root goes by below each source root.

    `app` for `<project>/app` under `<project>`, `metatron.scan` for
    `src/metatron/scan` under `src`, and `""` when the root is a source root.
    A source root the scanned root is not inside contributes nothing.
    """

    def apply(self, root: Path, source_roots: tuple[Path, ...]) -> tuple[str, ...]:
        return tuple(
            ".".join(root.relative_to(source_root).parts)
            for source_root in source_roots
            if root.is_relative_to(source_root)
        )
