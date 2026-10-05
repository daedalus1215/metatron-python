from pathlib import Path

import pytest

from metatron.scan.domain.transaction_scripts.write_model_ts.arch_model_to_json_converter import (  # noqa: E501
    ArchModelToJsonConverter,
)
from metatron.scan.domain.transaction_scripts.write_model_ts.write_model_params import (
    WriteModelParams,
)
from metatron.scan.domain.transaction_scripts.write_model_ts.write_model_transaction_script import (  # noqa: E501
    WriteModelTS,
)
from metatron.scan.infrastructure.repositories.model_repository import ModelRepository
from metatron.scan.test_utils import create_mock_arch_model
from metatron.shared.test_utils.test_utils import create_apply_mock

MODEL = create_mock_arch_model()
OUT = Path("/code/notes/.metatron")


@pytest.fixture
def model_repository_mock():
    mock = create_apply_mock(ModelRepository)
    mock.save.return_value = OUT / "model.json"
    return mock


@pytest.fixture
def arch_model_to_json_converter_mock():
    mock = create_apply_mock(ArchModelToJsonConverter)
    mock.apply.return_value = {"project": "notes"}
    return mock


@pytest.fixture
def target(model_repository_mock, arch_model_to_json_converter_mock):
    return WriteModelTS(model_repository_mock, arch_model_to_json_converter_mock)


class GivenWriteModelTS:
    class WhenWriting:
        def then_it_saves_the_converted_model_and_returns_where(
            self, target, model_repository_mock, arch_model_to_json_converter_mock
        ):
            # Act
            result = target.apply(WriteModelParams(model=MODEL, out_dir=OUT))

            # Assert
            arch_model_to_json_converter_mock.apply.assert_called_once_with(MODEL)
            model_repository_mock.save.assert_called_once_with({"project": "notes"}, OUT)
            assert result == OUT / "model.json"
