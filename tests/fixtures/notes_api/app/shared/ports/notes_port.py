from typing import Protocol


class NotesPort(Protocol):
    def count_for(self, user_id: int) -> int: ...
