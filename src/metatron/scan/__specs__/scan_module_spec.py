"""The scan context wired by the container, run over a real tree on disk."""

from textwrap import dedent

import pytest

from metatron.config.config_module import config_module
from metatron.scan.domain.services.scan_command import ScanCommand
from metatron.scan.domain.services.scan_service import ScanService
from metatron.scan.scan_module import scan_module
from metatron.shared.domain.ports.config_port import ConfigPort
from metatron.shared.domain.ports.model_port import ModelPort
from metatron.shared.kernel.container import Container

TREE = {
    "pyproject.toml": '[tool.metatron]\nroot = "app"\n',
    "app/__init__.py": "",
    "app/main.py": "from app.notes.application.create_note_action import router\n",
    "app/notes/__init__.py": "",
    "app/notes/application/create_note_action.py": """\
        from app.notes.domain.note_service import NoteService
        from app.notes.infrastructure.note_repository import NoteRepository
        router = None
    """,
    "app/notes/domain/note_service.py": """\
        from app.notes.application.create_note_action import router
        from app.users.domain.user_service import UserService
    """,
    "app/notes/infrastructure/note_repository.py": "import sqlalchemy\n",
    "app/users/domain/user_service.py": "",
}


@pytest.fixture
def project(tmp_path):
    for path, text in TREE.items():
        (tmp_path / path).parent.mkdir(parents=True, exist_ok=True)
        (tmp_path / path).write_text(dedent(text))
    return tmp_path


@pytest.fixture
def container():
    return Container([config_module, scan_module])


class GivenTheScanModule:
    class WhenScanningAFastapiProject:
        def then_every_broken_rule_is_a_violation(self, container, project):
            # Act
            result = container.get(ScanService).scan(ScanCommand(start=project))

            # Assert
            assert sorted({v.rule for v in result.model.violations}) == [
                "action>repository",
                "circular",
                "cross-domain",
                "domain-no-application",
                "no-same-level",
            ]

        def then_the_model_is_written_beside_the_config(self, container, project):
            # Act
            result = container.get(ScanService).scan(ScanCommand(start=project))

            # Assert
            assert result.model_path == project / ".metatron" / "model.json"
            assert result.model_path.is_file()

    class WhenAnotherContextAsksThroughTheModelPort:
        def then_it_gets_the_same_model_without_writing_one(self, container, project):
            # Arrange
            config = container.get(ConfigPort).load(project)

            # Act
            result = container.get(ModelPort).build(config)

            # Assert
            assert result.tree.coverage.files == 7
            assert not (project / ".metatron").exists()
