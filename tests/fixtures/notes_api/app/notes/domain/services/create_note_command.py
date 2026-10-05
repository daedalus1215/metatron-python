from dataclasses import dataclass


@dataclass(frozen=True)
class CreateNoteCommand:
    title: str
