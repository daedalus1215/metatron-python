import pytest

from metatron.baseline.domain.transaction_scripts.record_baseline_ts.baseline_document_converter import (  # noqa: E501
    BaselineDocumentConverter,
)
from metatron.baseline.test_utils import (
    create_mock_baseline,
    create_mock_entry,
    create_mock_model,
    create_mock_violation,
)


@pytest.fixture
def target():
    return BaselineDocumentConverter()


class GivenBaselineDocumentConverter:
    class WhenThereIsNoPreviousBaseline:
        def then_every_violation_is_accepted_without_a_note(self, target):
            # Arrange
            model = create_mock_model(create_mock_violation("aaa", "circular"))

            # Act
            result = target.apply(model, None)

            # Assert
            assert result.document == {
                "version": 1,
                "project": "notes",
                "violations": {
                    "aaa": {
                        "rule": "circular",
                        "from": "notes/aaa_from.py",
                        "to": "notes/aaa_to.py",
                    }
                },
            }
            assert (result.count, result.kept, result.dropped) == (1, 0, 0)

    class WhenAPreviousBaselineHasNotes:
        def then_a_note_whose_violation_remains_is_kept(self, target):
            # Arrange
            model = create_mock_model(create_mock_violation("aaa"))
            previous = create_mock_baseline(create_mock_entry("aaa", note="legacy"))

            # Act
            result = target.apply(model, previous)

            # Assert
            assert result.document["violations"]["aaa"]["note"] == "legacy"
            assert (result.kept, result.dropped) == (1, 0)

        def then_a_note_whose_violation_is_gone_is_dropped_and_counted(self, target):
            # Arrange
            model = create_mock_model(create_mock_violation("bbb"))
            previous = create_mock_baseline(
                create_mock_entry("aaa", note="legacy"), create_mock_entry("bbb")
            )

            # Act
            result = target.apply(model, previous)

            # Assert
            assert list(result.document["violations"]) == ["bbb"]
            assert (result.kept, result.dropped) == (0, 1)
