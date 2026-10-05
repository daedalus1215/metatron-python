from metatron.config.domain.transaction_scripts.load_config_ts.arch_config_mapper.arch_config_mapper import (  # noqa: E501
    ArchConfigMapper,
)
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
from metatron.config.domain.transaction_scripts.load_config_ts.load_config_transaction_script import (  # noqa: E501
    LoadConfigTS,
)

transaction_script_registry = [
    LoadConfigTS,
    ArchConfigMapper,
    ConfigShapeValidator,
    TableMergeConverter,
    ConfigReferencesValidator,
    ProjectNameConverter,
    TableToArchConfigConverter,
]
