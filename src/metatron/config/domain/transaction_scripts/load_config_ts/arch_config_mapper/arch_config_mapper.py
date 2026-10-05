from typing import Any

from metatron.config.domain.transaction_scripts.load_config_ts.arch_config_mapper.config_references_validator import (  # noqa: E501
    ConfigReferencesValidator,
)
from metatron.config.domain.transaction_scripts.load_config_ts.arch_config_mapper.config_shape_validator import (  # noqa: E501
    ConfigShapeValidator,
)
from metatron.config.domain.transaction_scripts.load_config_ts.arch_config_mapper.project_name_converter import (  # noqa: E501
    ProjectNameConverter,
)
from metatron.config.domain.transaction_scripts.load_config_ts.arch_config_mapper.table_merge_converter import (  # noqa: E501
    TableMergeConverter,
)
from metatron.config.domain.transaction_scripts.load_config_ts.arch_config_mapper.table_to_arch_config_converter import (  # noqa: E501
    TableToArchConfigConverter,
)
from metatron.config.domain.transaction_scripts.load_config_ts.config_table_projection import (
    ConfigTableProjection,
)
from metatron.config.infrastructure.repositories.package_repository import PackageRepository
from metatron.shared.domain.ports.config_port import ArchConfigProjection


class ArchConfigMapper:
    """A project's table and its profile, validated and merged into the config a scan runs under."""

    def __init__(
        self,
        config_shape_validator: ConfigShapeValidator,
        table_merge_converter: TableMergeConverter,
        config_references_validator: ConfigReferencesValidator,
        project_name_converter: ProjectNameConverter,
        table_to_arch_config_converter: TableToArchConfigConverter,
        package_repository: PackageRepository,
    ) -> None:
        self.config_shape_validator = config_shape_validator
        self.table_merge_converter = table_merge_converter
        self.config_references_validator = config_references_validator
        self.project_name_converter = project_name_converter
        self.table_to_arch_config_converter = table_to_arch_config_converter
        self.package_repository = package_repository

    def apply(self, found: ConfigTableProjection, profile: dict[str, Any]) -> ArchConfigProjection:
        self.config_shape_validator.apply(found.table, found.file)
        merged = self.table_merge_converter.apply(profile, found.table)
        self.config_references_validator.apply(merged, found.table, found.file)
        root = (found.file.parent / merged["root"]).resolve()
        return self.table_to_arch_config_converter.apply(
            merged,
            found.file,
            self.package_repository.source_roots_for(root),
            self.project_name_converter.apply(found.file, merged.get("name")),
        )
