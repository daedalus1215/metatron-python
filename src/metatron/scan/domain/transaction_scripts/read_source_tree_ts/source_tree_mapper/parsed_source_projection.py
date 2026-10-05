from dataclasses import dataclass


@dataclass(frozen=True)
class ImportStatementProjection:
    """One imported module: `import a.b` has no names; `from .a import b` has level 1."""

    module: str
    names: tuple[str, ...]
    level: int
    line: int

    @property
    def written(self) -> str:
        if not self.level and not self.names:
            return f"import {self.module}"
        return f"from {'.' * self.level}{self.module} import {', '.join(self.names)}"


@dataclass(frozen=True)
class ParsedSourceProjection:
    imports: tuple[ImportStatementProjection, ...]
    error: str | None = None
    error_line: int = 0
