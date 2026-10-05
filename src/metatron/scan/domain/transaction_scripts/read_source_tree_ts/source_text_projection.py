from dataclasses import dataclass


@dataclass(frozen=True)
class SourceTextProjection:
    """A scanned file's root-relative path, with `/` separators, and its text."""

    path: str
    text: str
