from app.notes.domain.transaction_scripts.create_note_ts.create_note_transaction_script import (
    CreateNoteTS,
)
from app.notes.infrastructure.repositories.note_repository import NoteRepository


class NoteService:
    def __init__(self, create_note_ts: CreateNoteTS, note_repository: NoteRepository):
        self.create_note_ts = create_note_ts
        self.note_repository = note_repository
