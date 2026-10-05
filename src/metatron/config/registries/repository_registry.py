from metatron.config.infrastructure.repositories.config_file_repository import (
    ConfigFileRepository,
)
from metatron.config.infrastructure.repositories.package_repository import PackageRepository
from metatron.config.infrastructure.repositories.profile_repository import ProfileRepository

repository_registry = [
    ConfigFileRepository,
    ProfileRepository,
    PackageRepository,
]
