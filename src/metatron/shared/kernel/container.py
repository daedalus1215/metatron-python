"""Builds providers from their constructor type hints — the analog of Nest's injector.

One instance per implementation. A port bound with `Bind` and the class it is
bound to resolve to the same instance.
"""

import inspect
import typing
from collections.abc import Iterable
from typing import Any, TypeVar

from metatron.shared.kernel.module import Bind, Module

T = TypeVar("T")


class Container:
    def __init__(self, modules: Iterable[Module]) -> None:
        self._implementations: dict[type, type] = {}
        self._actions: list[type] = []
        for module in modules:
            for provider in module.providers:
                if isinstance(provider, Bind):
                    self._implementations[provider.port] = provider.to
                    self._implementations.setdefault(provider.to, provider.to)
                else:
                    self._implementations[provider] = provider
            for action in module.actions:
                self._implementations[action] = action
                self._actions.append(action)
        self._instances: dict[type, Any] = {}

    def get(self, token: type[T]) -> T:
        return self._resolve(token, ())

    def actions(self) -> tuple[Any, ...]:
        return tuple(self.get(action) for action in self._actions)

    def _resolve(self, token: type, chain: tuple[type, ...]) -> Any:
        implementation = self._implementations.get(token)
        if implementation is None:
            asked_by = f" (asked for by {chain[-1].__name__})" if chain else ""
            raise LookupError(f"no module provides {token.__name__}{asked_by}")
        if implementation in self._instances:
            return self._instances[implementation]
        if implementation in chain:
            loop = " -> ".join(c.__name__ for c in (*chain, implementation))
            raise LookupError(f"circular injection: {loop}")
        instance = implementation(**self._arguments(implementation, (*chain, implementation)))
        self._instances[implementation] = instance
        return instance

    def _arguments(self, implementation: type, chain: tuple[type, ...]) -> dict[str, Any]:
        if implementation.__init__ is object.__init__:
            return {}
        hints = typing.get_type_hints(implementation.__init__)
        parameters = list(inspect.signature(implementation).parameters.values())
        return {
            parameter.name: self._resolve(hints[parameter.name], chain)
            for parameter in parameters
            if parameter.name in hints and parameter.default is inspect.Parameter.empty
        }
