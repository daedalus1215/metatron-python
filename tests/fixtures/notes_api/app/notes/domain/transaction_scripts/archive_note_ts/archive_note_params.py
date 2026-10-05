from dataclasses import dataclass

from app.notes.application.actions.create_note.create_note_request_dto import (
    CreateNoteRequestDTO,
)


@dataclass(frozen=True)
class ArchiveNoteParams:
    note: CreateNoteRequestDTO
