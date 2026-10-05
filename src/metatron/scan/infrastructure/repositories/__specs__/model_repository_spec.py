import json

import pytest

from metatron.scan.infrastructure.repositories.model_repository import ModelRepository


@pytest.fixture
def target():
    return ModelRepository()


class GivenModelRepository:
    class WhenSavingIntoADirectoryThatDoesNotExistYet:
        def then_it_creates_it_and_writes_model_json(self, target, tmp_path):
            # Act
            result = target.save({"project": "notes"}, tmp_path / ".metatron")

            # Assert
            assert result == tmp_path / ".metatron" / "model.json"
            assert json.loads(result.read_text()) == {"project": "notes"}
