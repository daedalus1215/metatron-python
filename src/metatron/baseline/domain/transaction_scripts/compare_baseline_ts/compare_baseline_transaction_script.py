from metatron.baseline.domain.transaction_scripts.compare_baseline_ts.baseline_check_projection import (  # noqa: E501
    BaselineCheckProjection,
)
from metatron.baseline.domain.transaction_scripts.compare_baseline_ts.baseline_comparison_converter import (  # noqa: E501
    BaselineComparisonConverter,
)
from metatron.baseline.domain.transaction_scripts.compare_baseline_ts.compare_baseline_params import (  # noqa: E501
    CompareBaselineParams,
)
from metatron.baseline.infrastructure.repositories.baseline_repository import BaselineRepository
from metatron.shared.domain.ports.config_port import ConfigError


class CompareBaselineTS:
    """Today's violations against the committed baseline. No baseline is an error, not a pass."""

    def __init__(
        self,
        baseline_repository: BaselineRepository,
        baseline_comparison_converter: BaselineComparisonConverter,
    ) -> None:
        self.baseline_repository = baseline_repository
        self.baseline_comparison_converter = baseline_comparison_converter

    def apply(self, params: CompareBaselineParams) -> BaselineCheckProjection:
        baseline = self.baseline_repository.read(params.directory)
        if baseline is None:
            raise ConfigError(
                f"No {self.baseline_repository.path_in(params.directory).name}"
                f" in {params.directory}.\nCreate one with `metatron-py baseline`."
            )
        return self.baseline_comparison_converter.apply(
            params.model, baseline, params.rules, params.allow_new
        )
