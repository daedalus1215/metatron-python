from metatron.config.domain.transaction_scripts.load_config_ts.arch_config_mapper.arch_config_mapper import (  # noqa: E501
    ArchConfigMapper,
)
from metatron.config.domain.transaction_scripts.load_config_ts.load_config_params import (
    LoadConfigParams,
)
from metatron.config.infrastructure.repositories.config_file_repository import (
    ConfigFileRepository,
)
from metatron.config.infrastructure.repositories.profile_repository import ProfileRepository
from metatron.shared.domain.ports.config_port import ArchConfigProjection, ConfigError

NOT_FOUND = """No metatron config found (searched upward from {start}).
Add one to the pyproject.toml beside the code you want scanned:

  [tool.metatron]
  root = "app"
"""


class LoadConfigTS:
    def __init__(
        self,
        config_file_repository: ConfigFileRepository,
        profile_repository: ProfileRepository,
        arch_config_mapper: ArchConfigMapper,
    ) -> None:
        self.config_file_repository = config_file_repository
        self.profile_repository = profile_repository
        self.arch_config_mapper = arch_config_mapper

    def apply(self, params: LoadConfigParams) -> ArchConfigProjection:
        found = self.config_file_repository.find(params.start)
        if found is None:
            raise ConfigError(NOT_FOUND.format(start=params.start.resolve()))
        profile = self.profile_repository.read(found.table.get("extends", "fastapi"))
        return self.arch_config_mapper.apply(found, profile)
