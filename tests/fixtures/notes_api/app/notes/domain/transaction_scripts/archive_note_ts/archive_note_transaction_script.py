from app.notes.domain.transaction_scripts.archive_note_ts.archive_note_params import (
    ArchiveNoteParams,
)
from app.notes.domain.transaction_scripts.create_note_ts.create_note_transaction_script import (
    CreateNoteTS,
)


class ArchiveNoteTS:
    def apply(self, params: ArchiveNoteParams) -> None: ...
