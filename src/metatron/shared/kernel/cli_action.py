"""One command line entry point: the CLI's analog of an HTTP Action."""

import argparse
from typing import Protocol


class CliAction(Protocol):
    name: str
    help: str

    def configure(self, parser: argparse.ArgumentParser) -> None:
        """Declare the command's arguments, usually by delegating to its request DTO."""
        ...

    def apply(self, arguments: argparse.Namespace) -> int:
        """Run the command and return its exit code."""
        ...
