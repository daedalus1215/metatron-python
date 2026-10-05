"""Mock helpers every spec uses, rather than hand-rolled `Mock()` objects."""

from typing import Any, TypeVar
from unittest.mock import create_autospec

T = TypeVar("T")


def create_apply_mock(cls: type[T], **methods: Any) -> Any:
    """`createApplyMock<T>()`: a mock of `cls` whose calls are checked against its signatures.

    Pass `methods` to replace a method with a stub of your own.
    """
    mock = create_autospec(cls, instance=True)
    for name, stub in methods.items():
        setattr(mock, name, stub)
    return mock
