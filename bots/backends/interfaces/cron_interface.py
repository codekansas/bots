#!/usr/bin/env python

from abc import ABC
from datetime import datetime, timedelta
from typing import Any, Dict, Optional

from bots.backends.base import BaseBackend
from croniter import croniter


class CronBackend(BaseBackend, ABC):
    """Provides a Cron-specific backend interface."""

    def __init__(self, config: Dict[str, str]) -> None:
        """Builds the backend using its associated config."""

        self.cron: Optional[str] = config.pop("cron", None)
        if self.cron is not None:
            assert croniter.is_valid(self.cron), self.cron

        super().__init__(config)

    def should_run(self, time: Optional[datetime] = None) -> bool:
        cron = self.cron
        if cron is None:
            return False
        if time is None:
            time = datetime.now()
        itr = croniter(cron, time)
        delta = itr.get_next(ret_type=datetime) - time
        return delta < timedelta(seconds=10)

    def props(self) -> Dict[str, Any]:
        return {**super().props(), "cron": self.cron}
