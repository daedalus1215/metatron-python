from app.notes.domain.services.note_service import NoteService
from app.notes.domain.transaction_scripts.create_note_ts.note_to_projection_converter import (
    NoteToProjectionConverter,
)
from app.notes.infrastructure.repositories.note_repository import NoteRepository


class CreateNoteTS:
    def __init__(self, repository: NoteRepository, converter: NoteToProjectionConverter):
        self.repository = repository
        self.converter = converter
