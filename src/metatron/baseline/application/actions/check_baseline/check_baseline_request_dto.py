import argparse
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class CheckBaselineRequestDTO:
    path: Path
    rules: tuple[str, ...]
    allow_new: int
    show_fixed: bool
    as_json: bool

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
            "--rule",
            action="append",
            default=[],
            metavar="ID",
            help="gate on this rule only (repeatable); the rest is reported, not gated",
        )
        parser.add_argument(
            "--allow-new",
            type=int,
            default=0,
            metavar="N",
            help="tolerate up to N new violations (default 0)",
        )
        parser.add_argument(
            "--no-fixed",
            dest="show_fixed",
            action="store_false",
            help="do not list violations fixed since the baseline",
        )
        parser.add_argument(
            "--json", dest="as_json", action="store_true", help="machine-readable result"
        )

    @classmethod
    def from_namespace(cls, arguments: argparse.Namespace) -> "CheckBaselineRequestDTO":
        return cls(
            path=arguments.path,
            rules=tuple(arguments.rule),
            allow_new=arguments.allow_new,
            show_fixed=arguments.show_fixed,
            as_json=arguments.as_json,
        )
