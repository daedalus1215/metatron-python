from sqlalchemy.orm import Session

from app.notes.domain.entities.note_entity import NoteEntity


class NoteRepository:
    def __init__(self, session: Session):
        self.session = session

    def find(self, note_id: int) -> NoteEntity | None: ...
