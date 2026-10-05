from pydantic import BaseModel


class CreateNoteRequestDTO(BaseModel):
    title: str
