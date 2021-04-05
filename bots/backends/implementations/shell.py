#!/usr/bin/env python

import subprocess
from typing import Dict

from bots.backends.interfaces.cron_interface import CronBackend
from bots.backends.registry import register


@register("shell")
class ShellBackend(CronBackend):
    """Runs arbitrary shell commands.

    This is admittedly a bit convoluted, since this will probably be run
    from cron in the first place, but adding it as a backend makes sense
    because it allows us to depend on other existing bot jobs.
    """

    def __init__(self, config: Dict[str, str]) -> None:
        # Gets the shell command to run.
        self.command = config.pop("command")

        super().__init__(config)

    async def run(self) -> None:
        process = subprocess.Popen(self.command, shell=True)
        process.communicate()
