import json

import pytest

from metatron.baseline.domain.entities.baseline_entity import BaselineEntryEntity
from metatron.baseline.infrastructure.repositories.baseline_repository import BaselineRepository
from metatron.shared.domain.ports.config_port import ConfigError

DOCUMENT = {
    "version": 1,
    "project": "notes",
    "violations": {
        "a3f19c4b2e01": {
            "rule": "action>repository",
            "from": "notes/a_action.py",
            "to": "notes/r_repository.py",
            "note": "legacy",
        }
    },
}


@pytest.fixture
def target():
    return BaselineRepository()


class GivenBaselineRepository:
    class WhenNoBaselineExists:
        def then_reading_returns_none(self, target, tmp_path):
            # Act
            result = target.read(tmp_path)

            # Assert
            assert result is None

    class WhenABaselineWasWritten:
        def then_it_reads_back_as_entries_by_fingerprint(self, target, tmp_path):
            # Arrange
            written = target.write(tmp_path, DOCUMENT)

            # Act
            result = target.read(tmp_path)

            # Assert
            assert written == tmp_path / "arch.baseline.json"
            assert result is not None
            assert result.project == "notes"
            assert result.entries == {
                "a3f19c4b2e01": BaselineEntryEntity(
                    fingerprint="a3f19c4b2e01",
                    rule="action>repository",
                    source="notes/a_action.py",
                    target="notes/r_repository.py",
                    note="legacy",
                )
            }

        def then_the_file_is_indented_for_a_readable_diff(self, target, tmp_path):
            # Act
            target.write(tmp_path, DOCUMENT)

            # Assert
            text = (tmp_path / "arch.baseline.json").read_text()
            assert text == json.dumps(DOCUMENT, indent=2) + "\n"

    class WhenTheFileIsNotJson:
        def then_it_raises_naming_the_file(self, target, tmp_path):
            # Arrange
            (tmp_path / "arch.baseline.json").write_text("{nope")

            # Act & Assert
            with pytest.raises(ConfigError, match="arch.baseline.json is not valid JSON"):
                target.read(tmp_path)

    class WhenTheFileHasNoViolationsObject:
        def then_it_raises_saying_how_to_recover(self, target, tmp_path):
            # Arrange
            (tmp_path / "arch.baseline.json").write_text('{"violations": []}')

            # Act & Assert
            with pytest.raises(ConfigError, match="re-run `metatron-py baseline`"):
                target.read(tmp_path)
