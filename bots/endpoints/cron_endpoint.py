#!/usr/bin/env python

import argparse
import sys
import textwrap
from pathlib import Path
from typing import List, Type

from bots.backends.base import BaseBackend
from bots.backends.interfaces.cron_interface import CronBackend
from bots.config import get_config_path, parse_config
from bots.run import run_sync
from bots.state import STATE
from termcolor import colored


def get_tab() -> str:
    root = Path(__file__).absolute().parent.parent.parent
    cfg_path = get_config_path()
    state_cfg_path = STATE.path()
    run_cmd = " ".join([
        f"BOTS_CONFIG={cfg_path}",
        f"BOTS_STATE_CONFIG={state_cfg_path}",
        f"{sys.executable} -m bots.endpoints.cron_endpoint",
    ])
    command = " && ".join([
        colored(f"cd {root}", "red"),
        colored(run_cmd, "cyan"),
    ])
    cron = colored("* * * * *", "green")
    return f"{cron} {command}"


DESCRIPTION = textwrap.dedent(f"""
    Tool for running bots that should run once every hour, day, or year. To
    set this up in your crontab, add the command below to your crontab:

        {get_tab()}

    This runs the Python script every minute, which in turn decides whether
    or not to run each bot.
""")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=DESCRIPTION,
        formatter_class=argparse.RawTextHelpFormatter,
    )
    parser.add_argument("-v", "--verbose", action="store_true",
                        help="If set, print verbose")
    parser.add_argument("-b", "--bots", nargs="+", default=[],
                        help="Specific bot names to run")
    return parser.parse_args()


def get_bots(bots: List[str]) -> List[str]:

    def should_instantiate(t: Type[BaseBackend], name: str) -> bool:
        if bots:
            return issubclass(t, CronBackend) and name in bots
        else:
            return issubclass(t, CronBackend)

    backends = parse_config(should_instantiate=should_instantiate)
    return [
        k for k, v in backends.items()
        if isinstance(v, CronBackend) and v.should_run()
    ]


def main() -> None:
    args = parse_args()

    bots = get_bots(args.bots)

    if args.verbose:
        for bot in bots:
            print(f"Running {colored(bot, 'green')}")
    run_sync(bots)


if __name__ == "__main__":
    main()
