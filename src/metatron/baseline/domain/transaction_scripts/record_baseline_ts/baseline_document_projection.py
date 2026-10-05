from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class BaselineDocumentProjection:
    """The baseline as it will be written, and what happened to the notes on the way."""

    document: dict[str, Any]
    count: int
    kept: int
    dropped: int
