from pathlib import Path

from metatron.config.domain.transaction_scripts.load_config_ts.arch_config_mapper.project_name_projection import (  # noqa: E501
    ProjectNameProjection,
)
from metatron.config.domain.transaction_scripts.load_config_ts.arch_config_mapper.table_to_arch_config_converter import (  # noqa: E501
    TableToArchConfigConverter,
)
from metatron.config.infrastructure.repositories.profile_repository import ProfileRepository
from metatron.shared.domain.ports.config_port import ForbiddenProjection

FILE = Path("/code/notes/pyproject.toml")
INFERRED = (Path("/code/notes"),)
NAME = ProjectNameProjection(name="notes")


def profile(**overrides):
    return {**ProfileRepository().read("fastapi"), **overrides}


class GivenTableToArchConfigConverter:
    class WhenConvertingTheProfile:
        def then_paths_resolve_against_the_config_files_directory(self):
            # Arrange
            target = TableToArchConfigConverter()

            # Act
            result = target.apply(profile(), FILE, INFERRED, NAME)

            # Assert
            assert result.root == Path("/code/notes/app")
            assert result.out_dir == Path("/code/notes/.metatron")
            assert result.directory == Path("/code/notes")

        def then_patterns_are_compiled_and_kept_in_order(self):
            # Arrange
            target = TableToArchConfigConverter()

            # Act
            result = target.apply(profile(), FILE, INFERRED, NAME)

            # Assert
            assert result.patterns[0].id == "spec"
            assert result.patterns[0].test.search("notes/__specs__/x_spec.py")

        def then_the_inferred_source_roots_are_used(self):
            # Arrange
            target = TableToArchConfigConverter()

            # Act
            result = target.apply(profile(), FILE, INFERRED, NAME)

            # Assert
            assert result.source_roots == INFERRED

    class WhenSourceRootsAreConfigured:
        def then_they_win_over_the_inferred_ones(self):
            # Arrange
            target = TableToArchConfigConverter()

            # Act
            result = target.apply(profile(**{"source-roots": ["src"]}), FILE, INFERRED, NAME)

            # Assert
            assert result.source_roots == (Path("/code/notes/src"),)

    class WhenAForbiddenRuleHasSeveralTargets:
        def then_it_becomes_one_rule_per_target(self):
            # Arrange
            rule = {"from": "mapper", "to": ["service", "action"], "why": "up"}
            table = profile(forbidden=[rule])
            target = TableToArchConfigConverter()

            # Act
            result = target.apply(table, FILE, INFERRED, NAME)

            # Assert
            assert result.forbidden == (
                ForbiddenProjection(source="mapper", target="service", why="up"),
                ForbiddenProjection(source="mapper", target="action", why="up"),
            )

    class WhenTheNameCarriesAWarning:
        def then_the_warning_travels_with_the_config(self):
            # Arrange
            name = ProjectNameProjection(name="chronus", warning="copied?")
            target = TableToArchConfigConverter()

            # Act
            result = target.apply(profile(), FILE, INFERRED, name)

            # Assert
            assert (result.name, result.name_warning) == ("chronus", "copied?")
