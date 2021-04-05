#!/usr/bin/env python

import logging
from typing import Dict, Union

import flask
from bots.backends.interfaces.flask_interface import FlaskBackend
from bots.backends.registry import register

logger = logging.getLogger(__name__)


@register("simple-website")
class SimpleWebsiteBackend(FlaskBackend):
    """Provides a simple website backend."""

    def __init__(self, config: Dict[str, str]) -> None:
        with open(config.pop("path"), "r") as f:
            self.site_contents: str = f.read()

        super().__init__(config)

    def run_flask(self) -> Union[str, flask.Response]:
        return self.site_contents
