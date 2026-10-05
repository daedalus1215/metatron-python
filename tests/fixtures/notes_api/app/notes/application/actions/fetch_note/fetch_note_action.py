from fastapi import Depends

from app.notes.infrastructure.repositories.note_repository import NoteRepository


def fetch_note(note_id: int, repository: NoteRepository = Depends()):
    return repository.find(note_id)
