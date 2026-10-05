import argparse
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class RecordBaselineRequestDTO:
    path: Path
    update: bool

    @staticmethod
    def add_arguments(parser: argparse.ArgumentParser) -> None:
        parser.add_argument(
            "path",
            nargs="?",
            type=Path,
            default=Path("."),
            help="the project, or any directory under it (default: here)",
        )
        parser.add_argument(
            "--update",
            action="store_true",
            help="rewrite an existing baseline, keeping its hand-written notes",
        )

    @classmethod
    def from_namespace(cls, arguments: argparse.Namespace) -> "RecordBaselineRequestDTO":
        return cls(path=arguments.path, update=arguments.update)
