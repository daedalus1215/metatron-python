"""Spec 05's acceptance, end to end through the commands, on a real tree."""

import json

import pytest

from metatron.main import main

ACTION = "app/notes/application/create_note_action.py"
REPOSITORY = "app/notes/infrastructure/note_repository.py"
SERVICE = "app/notes/domain/note_service.py"


def write(root, path, text=""):
    (root / path).parent.mkdir(parents=True, exist_ok=True)
    (root / path).write_text(text)


@pytest.fixture
def project(tmp_path):
    write(tmp_path, "pyproject.toml", '[tool.metatron]\nroot = "app"\n')
    write(tmp_path, "app/__init__.py")
    write(tmp_path, ACTION, "from app.notes.infrastructure.note_repository import NoteRepository\n")
    write(tmp_path, SERVICE)
    write(tmp_path, REPOSITORY)
    return tmp_path


def baseline_of(project):
    return json.loads((project / "arch.baseline.json").read_text())


class GivenTheBaselineCommands:
    class WhenABaselineIsRecordedAndNothingChanges:
        def then_check_passes(self, project, capsys):
            # Act
            recorded = main(["baseline", str(project)])
            checked = main(["check", str(project)])

            # Assert
            assert (recorded, checked) == (0, 0)
            assert "PASS — no new violations." in capsys.readouterr().out
            assert [v["rule"] for v in baseline_of(project)["violations"].values()] == [
                "action>repository"
            ]

    class WhenANewViolationAppears:
        def then_check_fails_naming_the_pair(self, project, capsys):
            # Arrange
            main(["baseline", str(project)])
            write(project, SERVICE, "from app.notes.application import create_note_action\n")
            capsys.readouterr()

            # Act
            result = main(["check", str(project)])

            # Assert
            out = capsys.readouterr().out
            assert result == 1
            assert "domain-no-application" in out
            assert "notes/domain/note_service.py" in out

    class WhenOneViolationIsSwappedForAnother:
        def then_check_still_fails(self, project):
            # Arrange
            main(["baseline", str(project)])
            write(project, ACTION, "from app.notes.domain.note_service import NoteService\n")
            write(project, SERVICE, "from app.notes.application import create_note_action\n")

            # Act
            result = main(["check", str(project), "--no-fixed"])

            # Assert
            assert result == 1

    class WhenABaselineAlreadyExists:
        def then_recording_again_without_update_is_refused(self, project, capsys):
            # Arrange
            main(["baseline", str(project)])

            # Act
            result = main(["baseline", str(project)])

            # Assert
            assert result == 2
            assert "baseline --update" in capsys.readouterr().err

        def then_update_keeps_a_note_whose_violation_remains(self, project):
            # Arrange
            main(["baseline", str(project)])
            document = baseline_of(project)
            next(iter(document["violations"].values()))["note"] = "legacy, pre-dates the service"
            (project / "arch.baseline.json").write_text(json.dumps(document))

            # Act
            result = main(["baseline", str(project), "--update"])

            # Assert
            assert result == 0
            notes = [v.get("note") for v in baseline_of(project)["violations"].values()]
            assert notes == ["legacy, pre-dates the service"]

    class WhenThereIsNoBaseline:
        def then_check_is_a_tool_error(self, project, capsys):
            # Act
            result = main(["check", str(project)])

            # Assert
            assert result == 2
            assert "Create one with `metatron-py baseline`" in capsys.readouterr().err

    class WhenAskedForJson:
        def then_the_check_parses(self, project, capsys):
            # Arrange
            main(["baseline", str(project)])
            capsys.readouterr()

            # Act
            main(["check", str(project), "--json"])

            # Assert
            assert json.loads(capsys.readouterr().out)["ok"] is True
