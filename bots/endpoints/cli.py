#!/usr/bin/env python

import argparse
import logging
import textwrap

import coloredlogs
from bots.backends.registry import REGISTRY
from bots.backends.run import run_sync
from bots.config import parse_config

logger = logging.getLogger(__name__)

DESCRIPTION = textwrap.dedent("""
    Tool for running bots from the command line. By default, this runs all
    available bots.
""")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=DESCRIPTION)
    parser.add_argument("-b", "--bots", nargs="+", default=[],
                        help="Names of the bots to run")
    return parser.parse_args()


def main() -> None:
    coloredlogs.install(level="INFO")
    args = parse_args()

    print(REGISTRY)

    backends = parse_config()
    available = list(backends.keys())
    if not args.bots:
        args.bots = available

    run_sync(args.bots)


if __name__ == "__main__":
    main()
