from metatron.scan.infrastructure.repositories.model_repository import ModelRepository
from metatron.scan.infrastructure.repositories.source_file_repository import (
    SourceFileRepository,
)

repository_registry = [
    SourceFileRepository,
    ModelRepository,
]
