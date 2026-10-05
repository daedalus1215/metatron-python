"""The bootstrap: one container, one argument parser, one action run."""

import argparse
import sys
from collections.abc import Sequence

from metatron.app_module import app_modules
from metatron.shared.domain.ports.config_port import ConfigError
from metatron.shared.kernel.cli_action import CliAction
from metatron.shared.kernel.container import Container

DESCRIPTION = (
    "Compile a Python (FastAPI) backend into a measured architecture model, "
    "and check it against its own rules."
)


def main(argv: Sequence[str] | None = None) -> int:
    actions: dict[str, CliAction] = {
        action.name: action for action in Container(app_modules).actions()
    }
    parser = argparse.ArgumentParser(prog="metatron-py", description=DESCRIPTION)
    commands = parser.add_subparsers(dest="command", metavar="command")
    for action in actions.values():
        action.configure(
            commands.add_parser(action.name, help=action.help, description=action.help)
        )
    arguments = list(sys.argv[1:] if argv is None else argv)
    # `metatron-py` and `metatron-py ~/code/api` both mean scan.
    if not arguments or (arguments[0] not in actions and not arguments[0].startswith("-")):
        arguments.insert(0, "scan")
    parsed = parser.parse_args(arguments)
    try:
        return actions[parsed.command].apply(parsed)
    except ConfigError as error:
        print(error, file=sys.stderr)
        return 2
