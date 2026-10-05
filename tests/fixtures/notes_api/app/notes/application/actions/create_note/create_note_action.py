from fastapi import Depends

from app.notes.application.actions.create_note.create_note_request_dto import (
    CreateNoteRequestDTO,
)
from app.notes.domain.services.note_service import NoteService


def create_note(request: CreateNoteRequestDTO, service: NoteService = Depends()):
    return service.create(request.title)
