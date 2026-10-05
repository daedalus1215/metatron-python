from pathlib import Path

from metatron.config.domain.transaction_scripts.load_config_ts.arch_config_mapper.project_name_converter import (  # noqa: E501
    ProjectNameConverter,
)


class GivenProjectNameConverter:
    class WhenNoNameIsConfigured:
        def then_it_is_the_folder_holding_the_config(self):
            # Arrange
            target = ProjectNameConverter()

            # Act
            result = target.apply(Path("/code/chronus/pyproject.toml"), None)

            # Assert
            assert result.name == "chronus"
            assert result.warning is None

        def then_it_climbs_past_generic_wrappers(self):
            # Arrange
            target = ProjectNameConverter()

            # Act
            result = target.apply(Path("/code/chronus/backend/pyproject.toml"), None)

            # Assert
            assert result.name == "chronus"

    class WhenTheConfiguredNameMatchesTheFolderLoosely:
        def then_it_is_kept_without_a_warning(self):
            # Arrange
            target = ProjectNameConverter()

            # Act
            result = target.apply(Path("/code/chronus-python-fastapi/pyproject.toml"), "Chronus")

            # Assert
            assert result.name == "Chronus"
            assert result.warning is None

    class WhenTheConfiguredNameIsSomeOtherProjects:
        def then_it_is_kept_and_a_warning_says_it_was_probably_copied(self):
            # Arrange
            target = ProjectNameConverter()

            # Act
            result = target.apply(Path("/code/omega/pyproject.toml"), "chronus")

            # Assert
            assert result.name == "chronus"
            assert result.warning is not None
            assert 'sits in "omega"' in result.warning
