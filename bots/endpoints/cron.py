#!/usr/bin/env python

import argparse
import sys
import textwrap
from datetime import datetime
from pathlib import Path
from typing import List

from bots.backends.interfaces.cron import CronBackend
from bots.backends.run import run_sync
from bots.config import get_config_path, parse_config
from termcolor import colored


def get_tab() -> str:
    root = Path(__file__).absolute().parent.parent.parent
    cfg_path = get_config_path()
    run_cmd = f"BOTS_CONFIG={cfg_path} {sys.executable} -m bots.endpoints.cron"
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
    parser.add_argument("-p", "--print-tab", action="store_true",
                        help="Prints lines to add to your crontab")
    return parser.parse_args()


def get_bots() -> List[str]:
    now = datetime.now()
    backends = parse_config()
    bots = {k: v for k, v in backends.items() if isinstance(v, CronBackend)}
    return [k for k, v in bots.items() if v.should_run(now)]


def main() -> None:
    args = parse_args()

    if args.print_tab:
        print(get_tab())
        return

    run_sync(get_bots())


if __name__ == "__main__":
    main()
