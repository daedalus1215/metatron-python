from app.notes.domain.aggregators.notes_aggregator import NotesAggregator
from app.shared.ports.notes_port import NotesPort

bindings = {NotesPort: NotesAggregator}
