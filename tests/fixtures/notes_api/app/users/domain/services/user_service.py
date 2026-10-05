from app.notes.domain.entities.note_entity import NoteEntity
from app.shared.ports.notes_port import NotesPort


class UserService:
    def __init__(self, notes: NotesPort):
        self.notes = notes

    def latest(self) -> NoteEntity | None: ...
