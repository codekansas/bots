#!/usr/bin/env python

import json
import textwrap
from abc import ABC, abstractmethod
from typing import Any, Dict, List

from termcolor import colored


class BaseBackend(ABC):
    """Defines the base backend.

    The config is the parsed config, as a dictionary. Subclasses should pop
    the relevant keys before calling super().__init__(config). This helps check
    that there aren't typos in the config.
    """

    def __init__(self, name: str, config: Dict[str, str]) -> None:
        """Builds the backend using its associated config."""

        self.name = name
        self.depends: List[str] = json.loads(config.pop("depends", "[]"))

        if config:
            raise ValueError(f"Unexpected config keys: {list(config.keys())}")

    @abstractmethod
    async def run(self) -> None:
        """Runs the backend."""

    def props(self) -> Dict[str, Any]:
        """Gets properties for this backend."""

        return {}

    @classmethod
    def help(cls) -> str:
        doc = cls.__doc__
        name = colored(cls.__name__, "green")
        if doc:
            doc = "\n".join(l.strip() for l in doc.splitlines()).strip()
            doc = textwrap.indent(doc, prefix="    ")
            doc = colored(doc, "cyan")
            return f"{name}\n\n{doc}\n"
        else:
            return f"{name}"

    def __repr__(self) -> str:
        cls = self.__class__.__name__
        props = ", ".join(f"{k}={v}" for k, v in self.props().items())
        return f"{cls}{{{props}}}"
