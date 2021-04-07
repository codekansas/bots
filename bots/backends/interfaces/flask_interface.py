#!/usr/bin/env python

import logging
from abc import ABC, abstractmethod
from typing import Dict, Union

import flask
from bots.backends.base import BaseBackend

logger = logging.getLogger(__name__)


class FlaskBackend(BaseBackend, ABC):
    """Provides a Flask-specific backend interface."""

    def __init__(self, name: str, config: Dict[str, str]) -> None:

        super().__init__(name, config)

    @abstractmethod
    def run_flask(self) -> Union[str, flask.Response]:
        """Runs the backend, returning a Flask response."""

    async def run(self) -> None:
        logger.info("`flask-backend` doesn't need to implement `run`")
