from pathlib import Path


class PackageRepository:
    def source_roots_for(self, root: Path) -> tuple[Path, ...]:
        """Where `from x.y import z` is resolved from, when the config does not say.

        A root that is a package resolves from the directory above its outermost
        package. A root without `__init__.py` is either a source root (`src/`)
        or a namespace package (`app/`), and only the imports can tell which, so
        both are tried.
        """
        if not (root / "__init__.py").is_file():
            return (root, root.parent)
        top = root
        while (top.parent / "__init__.py").is_file():
            top = top.parent
        return (top.parent,)
