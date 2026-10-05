from app.notes.domain.entities.note_entity import NoteEntity


class NoteToProjectionConverter:
    def apply(self, note: NoteEntity) -> dict:
        return {"id": note.id, "title": note.title}
