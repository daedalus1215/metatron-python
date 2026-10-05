import ast

from metatron.scan.domain.transaction_scripts.read_source_tree_ts.source_text_projection import (
    SourceTextProjection,
)
from metatron.scan.domain.transaction_scripts.read_source_tree_ts.source_tree_mapper.parsed_source_projection import (  # noqa: E501
    ImportStatementProjection,
    ParsedSourceProjection,
)


class PythonSourceConverter:
    """A file's imports, read with `ast` from anywhere in the file.

    Imports inside functions and under `if TYPE_CHECKING:` count: a type-only
    import is still a dependency someone has to honour.
    """

    def apply(self, source: SourceTextProjection) -> ParsedSourceProjection:
        try:
            tree = ast.parse(source.text, filename=source.path)
        except SyntaxError as error:
            return ParsedSourceProjection(imports=(), error=error.msg, error_line=error.lineno or 0)
        except ValueError as error:
            return ParsedSourceProjection(imports=(), error=str(error))
        statements = sorted(
            (node for node in ast.walk(tree) if isinstance(node, ast.Import | ast.ImportFrom)),
            key=lambda node: (node.lineno, node.col_offset),
        )
        return ParsedSourceProjection(
            imports=tuple(imported for node in statements for imported in self._imports(node))
        )

    def _imports(self, node: ast.Import | ast.ImportFrom) -> list[ImportStatementProjection]:
        if isinstance(node, ast.Import):
            return [
                ImportStatementProjection(module=alias.name, names=(), level=0, line=node.lineno)
                for alias in node.names
            ]
        return [
            ImportStatementProjection(
                module=node.module or "",
                names=tuple(alias.name for alias in node.names),
                level=node.level,
                line=node.lineno,
            )
        ]
