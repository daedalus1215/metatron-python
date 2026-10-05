import argparse
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class ScanRequestDTO:
    path: Path

    @staticmethod
    def add_arguments(parser: argparse.ArgumentParser) -> None:
        parser.add_argument(
            "path",
            nargs="?",
            type=Path,
            default=Path("."),
            help="the project, or any directory under it (default: here)",
        )

    @classmethod
    def from_namespace(cls, arguments: argparse.Namespace) -> "ScanRequestDTO":
        return cls(path=arguments.path)
