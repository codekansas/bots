#!/usr/bin/env python

import atexit
import functools
import json
import os
from pathlib import Path
from typing import Dict, Optional, Union


class _NoDefault:
    pass

NO_DEFAULT = _NoDefault()


class _State:
    def __init__(self, state: Dict[str, Dict[str, str]]) -> None:
        self.state = state

    def set(self, task: str, key: str, val: str) -> None:
        if task not in self.state:
            self.state[task] = {}
        self.state[task][key] = val

    def get(
        self,
        task: str,
        key: str,
        default: Optional[Union[str, _NoDefault]] = NO_DEFAULT,
    ) -> Optional[str]:
        try:
            return self.state[task][key]
        except KeyError as e:
            if isinstance(default, _NoDefault):
                raise e
            return default

    @staticmethod
    @functools.lru_cache(None)
    def path() -> Path:
        if "BOTS_STATE_CONFIG" in os.environ:
            path = Path(os.environ["BOTS_STATE_CONFIG"])
        else:
            path = Path("~/.config").expanduser() / "bots" / "state.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        return path

    @classmethod
    def load(cls) -> "State":
        if not _State.path().exists():
            return cls({})
        with open(_State.path(), "r") as f:
            state = json.load(f)
        return cls(state)

    def save(self) -> None:
        with open(_State.path(), "w") as f:
            json.dump(self.state, f, indent=2)


STATE = _State.load()
atexit.register(STATE.save)
