from dataclasses import dataclass


@dataclass(frozen=True)
class SourceLocationProjection:
    module: str
    folder: str
