import pytest

from metatron.config.config_module import config_module
from metatron.shared.domain.ports.config_port import ConfigError, ConfigPort
from metatron.shared.kernel.container import Container


@pytest.fixture
def target():
    return Container([config_module]).get(ConfigPort)


class GivenTheConfigModule:
    class WhenAProjectSetsOnlyItsRoot:
        def then_the_port_loads_the_whole_fastapi_profile(self, target, tmp_path):
            # Arrange
            project = tmp_path / "notes"
            (project / "app").mkdir(parents=True)
            (project / "app" / "__init__.py").write_text("")
            (project / "pyproject.toml").write_text('[tool.metatron]\nroot = "app"\n')

            # Act
            result = target.load(project / "app")

            # Assert
            assert result.name == "notes"
            assert result.root == project / "app"
            assert result.source_roots == (project,)
            assert result.flow == ("action", "service", "transaction-script", "repository")
            assert "service>repository" in result.allowed_skips

    class WhenAProjectAddsAPattern:
        def then_it_is_tried_first(self, target, tmp_path):
            # Arrange
            (tmp_path / "metatron.toml").write_text(
                'root = "app"\n'
                "[[add-patterns]]\n"
                'id = "exception"\n'
                'tier = "Contract"\n'
                "test = '_exception\\.py$'\n"
            )

            # Act
            result = target.load(tmp_path)

            # Assert
            assert result.patterns[0].id == "exception"
            assert result.patterns[0].test.search("notes/domain/not_found_exception.py")

    class WhenAProjectCopiedACamelCasedKey:
        def then_loading_fails_naming_it(self, target, tmp_path):
            # Arrange
            (tmp_path / "metatron.toml").write_text("addPatterns = []\n")

            # Act & Assert
            with pytest.raises(ConfigError, match="did you mean `add-patterns`"):
                target.load(tmp_path)

    class WhenAProjectsFlowNamesNoPattern:
        def then_loading_fails_naming_it(self, target, tmp_path):
            # Arrange
            (tmp_path / "metatron.toml").write_text('flow = ["action", "handler"]\n')

            # Act & Assert
            with pytest.raises(ConfigError, match='`flow` names "handler"'):
                target.load(tmp_path)
