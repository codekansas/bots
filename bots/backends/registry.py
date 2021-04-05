#!/usr/bin/env python

from typing import Callable, Dict, List, Type

from bots.backends.base import BaseBackend


class _Registry:
    """Maps backend names to their instantiations."""

    def __init__(self) -> None:
        self.backends: Dict[str, Type[BaseBackend]] = {}

    def register_backend(self, name: str) -> Callable[[Type[BaseBackend]], None]:
        """Adds the backend to the backend registry.

        After importing all the backends, the REGISTRY singleton will be
        populated, allowing backends to be instantiated from their names.
        """

        def _wrapper(backend: Type[BaseBackend]) -> None:
            assert issubclass(backend, BaseBackend), backend
            self.backends[name] = backend

        return _wrapper

    @property
    def types(self) -> List[str]:
        return list(self.backends.keys())

    def __repr__(self) -> str:
        items = "\n".join([
            f"{name}: {backend.help()}"
            for name, backend in self.backends.items()
        ])
        return f"-------\nRegistry\n-------\n\n{items}"


REGISTRY = _Registry()

register = REGISTRY.register_backend
