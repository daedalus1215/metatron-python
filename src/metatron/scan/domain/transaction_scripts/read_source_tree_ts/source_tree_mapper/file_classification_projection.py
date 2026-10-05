from dataclasses import dataclass


@dataclass(frozen=True)
class FileClassificationProjection:
    pattern: str
    tier: int
