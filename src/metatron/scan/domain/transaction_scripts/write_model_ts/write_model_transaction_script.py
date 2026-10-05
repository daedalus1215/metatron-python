from pathlib import Path

from metatron.scan.domain.transaction_scripts.write_model_ts.arch_model_to_json_converter import (  # noqa: E501
    ArchModelToJsonConverter,
)
from metatron.scan.domain.transaction_scripts.write_model_ts.write_model_params import (
    WriteModelParams,
)
from metatron.scan.infrastructure.repositories.model_repository import ModelRepository


class WriteModelTS:
    def __init__(
        self,
        model_repository: ModelRepository,
        arch_model_to_json_converter: ArchModelToJsonConverter,
    ) -> None:
        self.model_repository = model_repository
        self.arch_model_to_json_converter = arch_model_to_json_converter

    def apply(self, params: WriteModelParams) -> Path:
        document = self.arch_model_to_json_converter.apply(params.model)
        return self.model_repository.save(document, params.out_dir)
