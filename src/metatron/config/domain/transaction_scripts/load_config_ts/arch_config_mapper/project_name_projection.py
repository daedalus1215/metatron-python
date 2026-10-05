from dataclasses import dataclass


@dataclass(frozen=True)
class ProjectNameProjection:
    name: str
    warning: str | None = None
