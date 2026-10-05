import re

import pytest

from metatron.scan.infrastructure.repositories.source_file_repository import (
    SourceFileRepository,
)
from metatron.shared.domain.ports.config_port import ConfigError

IGNORE = (re.compile(r"(^|/)\.venv/"), re.compile(r"(^|/)build/"))


def write(path, text=""):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text)


@pytest.fixture
def target():
    return SourceFileRepository()


class GivenSourceFileRepository:
    class WhenReadingATree:
        def then_it_returns_every_python_file_by_root_relative_path(self, target, tmp_path):
            # Arrange
            write(tmp_path / "notes" / "domain" / "note_service.py", "x = 1\n")
            write(tmp_path / "main.py")
            write(tmp_path / "notes" / "README.md")

            # Act
            result = target.read_tree(tmp_path, IGNORE)

            # Assert
            assert [source.path for source in result] == [
                "main.py",
                "notes/domain/note_service.py",
            ]
            assert result[1].text == "x = 1\n"

        def then_ignored_directories_are_not_read(self, target, tmp_path):
            # Arrange
            write(tmp_path / ".venv" / "lib" / "site.py")
            write(tmp_path / "notes" / "build" / "gen.py")
            write(tmp_path / "notes" / "builder.py")

            # Act
            result = target.read_tree(tmp_path, IGNORE)

            # Assert
            assert [source.path for source in result] == ["notes/builder.py"]

        def then_ignore_is_matched_below_the_root_only(self, target, tmp_path):
            # Arrange
            root = tmp_path / "build" / "app"
            write(root / "main.py")

            # Act
            result = target.read_tree(root, IGNORE)

            # Assert
            assert [source.path for source in result] == ["main.py"]

    class WhenTheRootDoesNotExist:
        def then_it_raises_saying_root_is_relative_to_the_config(self, target, tmp_path):
            # Act & Assert
            with pytest.raises(ConfigError, match="root not found[\\s\\S]*relative to the config"):
                target.read_tree(tmp_path / "nope", IGNORE)

    class WhenListingLocalTopLevelNames:
        def then_it_names_modules_and_directories_holding_python(self, target, tmp_path):
            # Arrange
            write(tmp_path / "app" / "__init__.py")
            write(tmp_path / "scripts" / "seed.py")
            write(tmp_path / "manage.py")
            write(tmp_path / "docs" / "index.md")
            write(tmp_path / ".venv" / "x.py")

            # Act
            result = target.local_top_level_names((tmp_path, tmp_path / "missing"))

            # Assert
            assert result == frozenset({"app", "scripts", "manage"})
