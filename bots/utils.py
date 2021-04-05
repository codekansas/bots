#!/usr/bin/env python

from datetime import datetime
from typing import Optional


class Time:
    """Helper functions for handling time formatting."""

    FORMAT = "%Y-%m-%d %H:%M:%S"

    @staticmethod
    def parse(t: str) -> datetime:
        return datetime.strptime(t, Time.FORMAT)

    @staticmethod
    def get(t: Optional[datetime] = None) -> str:
        """Formats time for SQLite."""

        if t is None:
            t = datetime.now()
        return t.strftime(Time.FORMAT)
