"""Wording helpers for what the scan says."""


def count(n: int, noun: str, plural: str | None = None) -> str:
    """`1 upward call`, `3 upward calls`."""
    return f"{n} {noun if n == 1 else plural or noun + 's'}"
