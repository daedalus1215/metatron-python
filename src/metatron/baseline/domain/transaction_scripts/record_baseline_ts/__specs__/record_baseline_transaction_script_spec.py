from pathlib import Path

import pytest

from metatron.baseline.domain.transaction_scripts.record_baseline_ts.baseline_document_converter import (  # noqa: E501
    BaselineDocumentConverter,
)
from metatron.baseline.domain.transaction_scripts.record_baseline_ts.baseline_document_projection import (  # noqa: E501
    BaselineDocumentProjection,
)
from metatron.baseline.domain.transaction_scripts.record_baseline_ts.record_baseline_params import (  # noqa: E501
    RecordBaselineParams,
)
from metatron.baseline.domain.transaction_scripts.record_baseline_ts.record_baseline_transaction_script import (  # noqa: E501
    RecordBaselineTS,
)
from metatron.baseline.domain.transaction_scripts.record_baseline_ts.recorded_baseline_projection import (  # noqa: E501
    RecordedBaselineProjection,
)
from metatron.baseline.domain.transaction_scripts.record_baseline_ts.ungated_findings_converter import (  # noqa: E501
    UngatedFindingsConverter,
)
from metatron.baseline.infrastructure.repositories.baseline_repository import BaselineRepository
from metatron.baseline.test_utils import create_mock_baseline, create_mock_model
from metatron.shared.domain.ports.config_port import ConfigError
from metatron.shared.test_utils.test_utils import create_apply_mock

DIRECTORY = Path("/code/notes")
FILE = DIRECTORY / "arch.baseline.json"
MODEL = create_mock_model()
DOCUMENT = BaselineDocumentProjection(document={"version": 1}, count=3, kept=1, dropped=2)


@pytest.fixture
def baseline_repository_mock():
    mock = create_apply_mock(BaselineRepository)
    mock.read.return_value = None
    mock.write.return_value = FILE
    mock.path_in.return_value = FILE
    return mock


@pytest.fixture
def baseline_document_converter_mock():
    mock = create_apply_mock(BaselineDocumentConverter)
    mock.apply.return_value = DOCUMENT
    return mock


@pytest.fixture
def ungated_findings_converter_mock():
    mock = create_apply_mock(UngatedFindingsConverter)
    mock.apply.return_value = ("dag",)
    return mock


@pytest.fixture
def target(
    baseline_repository_mock, baseline_document_converter_mock, ungated_findings_converter_mock
):
    return RecordBaselineTS(
        baseline_repository_mock, baseline_document_converter_mock, ungated_findings_converter_mock
    )


class GivenRecordBaselineTS:
    class WhenNoBaselineExistsYet:
        def then_it_writes_one_and_reports_what_it_wrote(
            self, target, baseline_repository_mock, baseline_document_converter_mock
        ):
            # Act
            result = target.apply(RecordBaselineParams(MODEL, DIRECTORY, update=False))

            # Assert
            baseline_document_converter_mock.apply.assert_called_once_with(MODEL, None)
            baseline_repository_mock.write.assert_called_once_with(DIRECTORY, {"version": 1})
            assert result == RecordedBaselineProjection(
                project="notes",
                path=FILE,
                updated=False,
                count=3,
                kept=1,
                dropped=2,
                ungated=("dag",),
            )

    class WhenABaselineExistsAndUpdateWasNotAsked:
        def then_it_refuses_and_writes_nothing(self, target, baseline_repository_mock):
            # Arrange
            baseline_repository_mock.read.return_value = create_mock_baseline()

            # Act & Assert
            with pytest.raises(ConfigError, match="already exists[\\s\\S]*baseline --update"):
                target.apply(RecordBaselineParams(MODEL, DIRECTORY, update=False))
            baseline_repository_mock.write.assert_not_called()

    class WhenABaselineExistsAndUpdateWasAsked:
        def then_it_rewrites_it_from_the_previous_one(
            self, target, baseline_repository_mock, baseline_document_converter_mock
        ):
            # Arrange
            previous = create_mock_baseline()
            baseline_repository_mock.read.return_value = previous

            # Act
            result = target.apply(RecordBaselineParams(MODEL, DIRECTORY, update=True))

            # Assert
            baseline_document_converter_mock.apply.assert_called_once_with(MODEL, previous)
            assert result.updated
