from app.notes.infrastructure.repositories.note_repository import NoteRepository


class NotesAggregator:
    def __init__(self, note_repository: NoteRepository):
        self.note_repository = note_repository
