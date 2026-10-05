from collections import Counter
from collections.abc import Iterator

from metatron.scan.domain.transaction_scripts.read_source_tree_ts.source_text_projection import (
    SourceTextProjection,
)
from metatron.scan.domain.transaction_scripts.read_source_tree_ts.source_tree_mapper.coverage_converter import (  # noqa: E501
    CoverageConverter,
)
from metatron.scan.domain.transaction_scripts.read_source_tree_ts.source_tree_mapper.file_classification_converter import (  # noqa: E501
    FileClassificationConverter,
)
from metatron.scan.domain.transaction_scripts.read_source_tree_ts.source_tree_mapper.import_resolution_converter import (  # noqa: E501
    ImportResolutionConverter,
)
from metatron.scan.domain.transaction_scripts.read_source_tree_ts.source_tree_mapper.import_resolution_projection import (  # noqa: E501
    ImportContextProjection,
)
from metatron.scan.domain.transaction_scripts.read_source_tree_ts.source_tree_mapper.module_prefix_converter import (  # noqa: E501
    ModulePrefixConverter,
)
from metatron.scan.domain.transaction_scripts.read_source_tree_ts.source_tree_mapper.python_source_converter import (  # noqa: E501
    PythonSourceConverter,
)
from metatron.scan.domain.transaction_scripts.read_source_tree_ts.source_tree_mapper.source_location_converter import (  # noqa: E501
    SourceLocationConverter,
)
from metatron.shared.domain.ports.config_port import ArchConfigProjection
from metatron.shared.domain.ports.model_port import (
    DiagnosticProjection,
    ImportEdgeProjection,
    SourceFileProjection,
    SourceTreeProjection,
)


class SourceTreeMapper:
    """Read source as files, edges, externals and diagnostics, with the coverage of the lot."""

    def __init__(
        self,
        python_source_converter: PythonSourceConverter,
        module_prefix_converter: ModulePrefixConverter,
        import_resolution_converter: ImportResolutionConverter,
        file_classification_converter: FileClassificationConverter,
        source_location_converter: SourceLocationConverter,
        coverage_converter: CoverageConverter,
    ) -> None:
        self.python_source_converter = python_source_converter
        self.module_prefix_converter = module_prefix_converter
        self.import_resolution_converter = import_resolution_converter
        self.file_classification_converter = file_classification_converter
        self.source_location_converter = source_location_converter
        self.coverage_converter = coverage_converter

    def apply(
        self,
        sources: tuple[SourceTextProjection, ...],
        config: ArchConfigProjection,
        local_names: frozenset[str],
    ) -> SourceTreeProjection:
        context = ImportContextProjection(
            files=frozenset(source.path for source in sources),
            prefixes=self.module_prefix_converter.apply(config.root, config.source_roots),
            local_names=local_names,
        )
        files = tuple(self._file(source, config) for source in sources)
        edges: dict[tuple[str, str], ImportEdgeProjection] = {}
        externals: Counter[str] = Counter()
        diagnostics: list[DiagnosticProjection] = []
        for source in sources:
            for kind, line, detail, targets, external in self._imports(source, context):
                if kind:
                    diagnostics.append(DiagnosticProjection(kind, source.path, line, detail))
                if external:
                    externals[external] += 1
                for target in targets:
                    if target != source.path:
                        edges.setdefault(
                            (source.path, target), ImportEdgeProjection(source.path, target, line)
                        )
        return SourceTreeProjection(
            files=files,
            edges=tuple(edges.values()),
            externals=dict(sorted(externals.items())),
            diagnostics=tuple(diagnostics),
            coverage=self.coverage_converter.apply(files, config.fallback),
        )

    def _file(
        self, source: SourceTextProjection, config: ArchConfigProjection
    ) -> SourceFileProjection:
        location = self.source_location_converter.apply(source.path)
        classification = self.file_classification_converter.apply(source.path, config)
        return SourceFileProjection(
            path=source.path,
            module=location.module,
            folder=location.folder,
            pattern=classification.pattern,
            tier=classification.tier,
            loc=len(source.text.splitlines()),
        )

    def _imports(
        self, source: SourceTextProjection, context: ImportContextProjection
    ) -> Iterator[tuple[str, int, str, tuple[str, ...], str | None]]:
        """(diagnostic kind, line, detail, targets, external) per import and parse failure."""
        parsed = self.python_source_converter.apply(source)
        if parsed.error is not None:
            yield "parse-failed", parsed.error_line, parsed.error, (), None
        for statement in parsed.imports:
            resolution = self.import_resolution_converter.apply(source.path, statement, context)
            if resolution.unresolved:
                detail = f"'{statement.written}' names no file in the scanned tree"
                yield "import-unresolved", statement.line, detail, (), None
            else:
                yield "", statement.line, "", resolution.targets, resolution.external
