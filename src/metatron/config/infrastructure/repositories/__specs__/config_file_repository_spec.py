import pytest

from metatron.config.infrastructure.repositories.config_file_repository import (
    ConfigFileRepository,
)
from metatron.shared.domain.ports.config_port import ConfigError


class GivenConfigFileRepository:
    class WhenAPyprojectAboveHoldsAMetatronTable:
        def then_it_finds_it_from_a_nested_directory(self, tmp_path):
            # Arrange
            (tmp_path / "pyproject.toml").write_text('[tool.metatron]\nroot = "app"\n')
            nested = tmp_path / "app" / "notes"
            nested.mkdir(parents=True)
            target = ConfigFileRepository()

            # Act
            result = target.find(nested)

            # Assert
            assert result is not None
            assert result.file == tmp_path / "pyproject.toml"
            assert result.table == {"root": "app"}

    class WhenTheNearestPyprojectHasNoMetatronTable:
        def then_it_is_passed_over_for_one_further_up(self, tmp_path):
            # Arrange
            (tmp_path / "pyproject.toml").write_text('[tool.metatron]\nroot = "app"\n')
            inner = tmp_path / "packages" / "lib"
            inner.mkdir(parents=True)
            (inner / "pyproject.toml").write_text('[project]\nname = "lib"\n')
            target = ConfigFileRepository()

            # Act
            result = target.find(inner)

            # Assert
            assert result is not None
            assert result.file == tmp_path / "pyproject.toml"

    class WhenAMetatronTomlSitsBesideThePyproject:
        def then_the_standalone_file_wins_and_is_the_whole_table(self, tmp_path):
            # Arrange
            (tmp_path / "pyproject.toml").write_text('[tool.metatron]\nroot = "a"\n')
            (tmp_path / "metatron.toml").write_text('root = "b"\n')
            target = ConfigFileRepository()

            # Act
            result = target.find(tmp_path)

            # Assert
            assert result is not None
            assert result.table == {"root": "b"}

    class WhenStartIsTheConfigFileItself:
        def then_it_reads_that_file(self, tmp_path):
            # Arrange
            file = tmp_path / "pyproject.toml"
            file.write_text('[tool.metatron]\nroot = "app"\n')
            target = ConfigFileRepository()

            # Act
            result = target.find(file)

            # Assert
            assert result is not None
            assert result.file == file

    class WhenTheTomlIsMalformed:
        def then_it_raises_naming_the_file(self, tmp_path):
            # Arrange
            (tmp_path / "metatron.toml").write_text("root = \n")
            target = ConfigFileRepository()

            # Act & Assert
            with pytest.raises(ConfigError, match="metatron.toml is not valid TOML"):
                target.find(tmp_path)
