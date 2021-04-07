#!/usr/bin/env python

import functools
import os
import warnings
from configparser import ConfigParser
from pathlib import Path
from typing import Callable, Dict, Optional, Type

from bots.backends.base import BaseBackend
from bots.backends.registry import REGISTRY


class ConfigParseException(Exception):
    pass


def get_config_path() -> Path:
    if "BOTS_CONFIG" in os.environ:
        cfg_file = Path(os.environ["BOTS_CONFIG"])
        if not cfg_file.is_file():
            raise FileNotFoundError("Config file specified by BOTS_CONFIG "
                                    f"not found: {cfg_file}")
        return cfg_file

    cfg_files = [
        Path("~/.config").expanduser() / "bots" / "bots.ini",
        Path("~/.botsrc").expanduser(),
    ]

    for cfg_file in cfg_files:
        if cfg_file.is_file():
            return cfg_file

    raise FileNotFoundError("Couldn't find config file. This should be set to "
                            f"one of {cfg_files}")


@functools.lru_cache(None)
def parse_config(
    cfg_file: Optional[Path] = None,
    should_instantiate: Optional[Callable[[Type[BaseBackend], str], bool]] = None,
) -> Dict[str, BaseBackend]:
    if cfg_file is None:
        cfg_file = get_config_path()

    config = ConfigParser()
    config.read(cfg_file)

    backends: Dict[str, BaseBackend] = {}
    for section in config.sections():
        items = {k: v for k, v in config[section].items()}

        if "type" not in items:
            warnings.warn(f"Section [{section}] missing `type` key; skipping")
            continue

        btype = items.pop("type")
        if btype not in REGISTRY.backends:
            available = list(REGISTRY.backends.keys())
            raise ConfigParseException(f"Backend '{btype}' not found; "
                                       f"available: {available}")

        try:
            backend_type = REGISTRY.backends[btype]
            if should_instantiate is None:
                backends[section] = backend_type(section, items)
            elif should_instantiate(backend_type, section):
                backends[section] = backend_type(section, items)
        except Exception as exp:
            raise ConfigParseException from exp

    return backends
