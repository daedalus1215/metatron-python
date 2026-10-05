"""A context's providers and actions, declared as data — the analog of `@Module()`."""

from collections.abc import Sequence
from dataclasses import dataclass, field


@dataclass(frozen=True)
class Bind:
    """`{ provide: Port, useClass: to }`: whoever asks for `port` gets a `to`."""

    port: type
    to: type


@dataclass(frozen=True)
class Module:
    providers: Sequence[type | Bind] = field(default_factory=tuple)
    actions: Sequence[type] = field(default_factory=tuple)
