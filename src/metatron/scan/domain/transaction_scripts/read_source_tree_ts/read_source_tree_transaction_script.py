from metatron.scan.domain.transaction_scripts.read_source_tree_ts.read_source_tree_params import (
    ReadSourceTreeParams,
)
from metatron.scan.domain.transaction_scripts.read_source_tree_ts.source_tree_mapper.source_tree_mapper import (  # noqa: E501
    SourceTreeMapper,
)
from metatron.scan.infrastructure.repositories.source_file_repository import (
    SourceFileRepository,
)
from metatron.shared.domain.ports.config_port import ConfigError
from metatron.shared.domain.ports.model_port import SourceTreeProjection


class ReadSourceTreeTS:
    def __init__(
        self, source_file_repository: SourceFileRepository, source_tree_mapper: SourceTreeMapper
    ) -> None:
        self.source_file_repository = source_file_repository
        self.source_tree_mapper = source_tree_mapper

    def apply(self, params: ReadSourceTreeParams) -> SourceTreeProjection:
        config = params.config
        sources = self.source_file_repository.read_tree(config.root, config.ignore)
        if not sources:
            raise ConfigError(f"no .py files under {config.root}")
        local_names = self.source_file_repository.local_top_level_names(config.source_roots)
        return self.source_tree_mapper.apply(sources, config, local_names)
