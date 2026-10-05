from fastapi import APIRouter

from app.notes.application.actions.create_note.create_note_action import create_note
from app.notes.application.actions.fetch_note.fetch_note_action import fetch_note
from app.notes.domain.transaction_scripts.archive_note_ts.archive_note_transaction_script import (
    ArchiveNoteTS,
)

notes_router = APIRouter(prefix="/notes")
notes_router.post("")(create_note)
notes_router.get("/{note_id}")(fetch_note)
notes_router.post("/{note_id}/archive")(lambda note_id: ArchiveNoteTS().apply(note_id))
