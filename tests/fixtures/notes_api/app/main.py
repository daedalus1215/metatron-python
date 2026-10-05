from fastapi import FastAPI

from app.notes.application.routers.notes_router import notes_router

app = FastAPI()
app.include_router(notes_router)
