import pytest

from metatron.scan.domain.transaction_scripts.evaluate_rules_ts.findings_mapper.module_cycles_findings_converter import (  # noqa: E501
    ModuleCyclesFindingsConverter,
)
from metatron.scan.test_utils import create_mock_arch_config, create_mock_source_tree

CONFIG = create_mock_arch_config()
FILES = {
    "notes/note_service.py": "service",
    "notes/notes_port.py": "port",
    "users/user_service.py": "service",
    "users/users_module.py": "module",
}


@pytest.fixture
def target():
    return ModuleCyclesFindingsConverter()


class GivenModuleCyclesFindingsConverter:
    class WhenTwoContextsImportEachOther:
        def then_it_warns_without_gating(self, target):
            # Arrange
            tree = create_mock_source_tree(
                FILES,
                [
                    ("notes/note_service.py", "users/user_service.py"),
                    ("users/user_service.py", "notes/note_service.py"),
                ],
            )

            # Act
            result = target.apply(CONFIG, tree)

            # Assert
            assert [(f.id, f.tone, f.gate) for f in result] == [("dag", "warn", False)]
            assert result[0].items == ("notes <-> users",)

    class WhenTheWayBackGoesThroughAPortOrTheWiring:
        def then_the_contexts_form_a_dag(self, target):
            # Arrange
            tree = create_mock_source_tree(
                FILES,
                [
                    ("notes/note_service.py", "users/user_service.py"),
                    ("users/user_service.py", "notes/notes_port.py"),
                    ("users/users_module.py", "notes/note_service.py"),
                ],
            )

            # Act
            result = target.apply(CONFIG, tree)

            # Assert
            assert result[0].tone == "good"
