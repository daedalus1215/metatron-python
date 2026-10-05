from metatron.baseline.domain.transaction_scripts.record_baseline_ts.baseline_document_converter import (  # noqa: E501
    BaselineDocumentConverter,
)
from metatron.baseline.domain.transaction_scripts.record_baseline_ts.record_baseline_params import (  # noqa: E501
    RecordBaselineParams,
)
from metatron.baseline.domain.transaction_scripts.record_baseline_ts.recorded_baseline_projection import (  # noqa: E501
    RecordedBaselineProjection,
)
from metatron.baseline.domain.transaction_scripts.record_baseline_ts.ungated_findings_converter import (  # noqa: E501
    UngatedFindingsConverter,
)
from metatron.baseline.infrastructure.repositories.baseline_repository import BaselineRepository
from metatron.shared.domain.ports.config_port import ConfigError


class RecordBaselineTS:
    """Accept today's violations. An existing baseline is rewritten only when asked to."""

    def __init__(
        self,
        baseline_repository: BaselineRepository,
        baseline_document_converter: BaselineDocumentConverter,
        ungated_findings_converter: UngatedFindingsConverter,
    ) -> None:
        self.baseline_repository = baseline_repository
        self.baseline_document_converter = baseline_document_converter
        self.ungated_findings_converter = ungated_findings_converter

    def apply(self, params: RecordBaselineParams) -> RecordedBaselineProjection:
        previous = self.baseline_repository.read(params.directory)
        if previous is not None and not params.update:
            raise ConfigError(
                f"{self.baseline_repository.path_in(params.directory)} already exists.\n"
                "Run `metatron-py baseline --update` to rewrite it."
                " Hand-written `note` fields are preserved."
            )
        written = self.baseline_document_converter.apply(params.model, previous)
        return RecordedBaselineProjection(
            project=params.model.project,
            path=self.baseline_repository.write(params.directory, written.document),
            updated=previous is not None,
            count=written.count,
            kept=written.kept,
            dropped=written.dropped,
            ungated=self.ungated_findings_converter.apply(params.model),
        )
