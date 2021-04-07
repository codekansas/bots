#!/usr/bin/env python

import enum
from abc import ABC
from datetime import datetime, timedelta
from typing import Any, Dict, Optional

from bots.backends.base import BaseBackend
from bots.state import STATE
from bots.utils import Time


class CronMode(enum.Enum):
    never = "never"
    always = "always"
    hourly = "hourly"
    daily = "daily"
    monthly = "monthly"
    yearly = "yearly"

    def timedelta(self) -> Optional[timedelta]:
        if self == CronMode.never:
            return None
        if self == CronMode.always:
            return timedelta(seconds=0)
        if self == CronMode.hourly:
            return timedelta(hours=1)
        if self == CronMode.daily:
            return timedelta(days=1)
        if self == CronMode.monthly:
            return timedelta(days=30)
        if self == CronMode.yearly:
            return timedelta(days=365)
        raise NotImplementedError(f"Invalid time mode: {self}")


class CronBackend(BaseBackend, ABC):
    """Provides a Cron-specific backend interface."""

    def __init__(self, name: str, config: Dict[str, str]) -> None:
        """Builds the backend using its associated config."""

        self.run_mode = CronMode(config.pop("cron", "none"))

        super().__init__(name, config)

    def should_run(self) -> bool:
        curr_time = datetime.now()
        curr_time_str = Time.get(curr_time)
        last_run_str = STATE.get(self.name, "last_run", default=None)
        if last_run_str is None:
            should_run = True
        else:
            last_run = Time.parse(last_run_str)
            delta = curr_time - last_run
            min_delta = self.run_mode.timedelta()
            if min_delta is None:
                should_run = False
            else:
                should_run = delta >= min_delta

        if should_run:
            STATE.set(self.name, "last_run", curr_time_str)
        return should_run

    def props(self) -> Dict[str, Any]:
        return {**super().props(), "cron_run_mode": self.run_mode}
