import posixpath

from metatron.scan.domain.transaction_scripts.read_source_tree_ts.source_tree_mapper.import_resolution_projection import (  # noqa: E501
    ImportContextProjection,
    ImportResolutionProjection,
)
from metatron.scan.domain.transaction_scripts.read_source_tree_ts.source_tree_mapper.parsed_source_projection import (  # noqa: E501
    ImportStatementProjection,
)


class ImportResolutionConverter:
    """Where an import lands: scanned files, an external package, or nowhere it can say."""

    def apply(
        self, importer: str, statement: ImportStatementProjection, context: ImportContextProjection
    ) -> ImportResolutionProjection:
        if statement.level:
            bases = [self._relative_base(importer, statement)]
            local = True
        else:
            bases = [self._under_prefix(statement.module, prefix) for prefix in context.prefixes]
            local = statement.module.split(".")[0] in context.local_names
        for base in bases:
            targets = (
                self._targets(base, statement.names, context.files) if base is not None else []
            )
            if targets:
                return ImportResolutionProjection(targets=tuple(dict.fromkeys(targets)))
        if local:
            return ImportResolutionProjection()
        return ImportResolutionProjection(external=statement.module.split(".")[0])

    def _relative_base(self, importer: str, statement: ImportStatementProjection) -> str | None:
        """The importer's package, climbed `level - 1` times; None when that leaves the root."""
        package = posixpath.dirname(importer)
        for _ in range(statement.level - 1):
            if not package:
                return None
            package = posixpath.dirname(package)
        return self._join(package, statement.module.replace(".", "/"))

    def _under_prefix(self, module: str, prefix: str) -> str | None:
        if not prefix:
            return module.replace(".", "/")
        if module == prefix:
            return ""
        if module.startswith(prefix + "."):
            return module[len(prefix) + 1 :].replace(".", "/")
        return None

    def _targets(self, base: str, names: tuple[str, ...], files: frozenset[str]) -> list[str]:
        """`from base import name` lands on `base/name` when that is a submodule, else on `base`."""
        if not names:
            module = self._module_file(base, files)
            return [module] if module else []
        submodules = [self._module_file(self._join(base, n), files) for n in names if n != "*"]
        found = [submodule for submodule in submodules if submodule]
        if len(found) < len(names):
            module = self._module_file(base, files)
            found += [module] if module else []
        return found

    def _module_file(self, base: str, files: frozenset[str]) -> str | None:
        candidates = ["__init__.py"] if not base else [f"{base}.py", f"{base}/__init__.py"]
        return next((candidate for candidate in candidates if candidate in files), None)

    def _join(self, head: str, tail: str) -> str:
        return "/".join(part for part in (head, tail) if part)
