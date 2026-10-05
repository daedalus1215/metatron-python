import pytest

from metatron.scan.domain.transaction_scripts.read_source_tree_ts.source_tree_mapper.import_resolution_converter import (  # noqa: E501
    ImportResolutionConverter,
)
from metatron.scan.domain.transaction_scripts.read_source_tree_ts.source_tree_mapper.import_resolution_projection import (  # noqa: E501
    ImportContextProjection,
    ImportResolutionProjection,
)
from metatron.scan.domain.transaction_scripts.read_source_tree_ts.source_tree_mapper.parsed_source_projection import (  # noqa: E501
    ImportStatementProjection,
)

FILES = frozenset(
    {
        "__init__.py",
        "notes/__init__.py",
        "notes/domain/__init__.py",
        "notes/domain/note_service.py",
        "notes/domain/helpers.py",
        "notes/infrastructure/__init__.py",
        "notes/infrastructure/note_repository.py",
        "shared/ports/__init__.py",
        "shared/ports/users_port.py",
    }
)
CONTEXT = ImportContextProjection(files=FILES, prefixes=("app",), local_names=frozenset({"app"}))
IMPORTER = "notes/domain/note_service.py"


def absolute(module, *names):
    return ImportStatementProjection(module=module, names=names, level=0, line=1)


def relative(level, module, *names):
    return ImportStatementProjection(module=module, names=names, level=level, line=1)


@pytest.fixture
def target():
    return ImportResolutionConverter()


class GivenImportResolutionConverter:
    class WhenAnAbsoluteImportNamesAModuleUnderThePrefix:
        def then_it_lands_on_that_file(self, target):
            # Act
            result = target.apply(
                IMPORTER, absolute("app.notes.infrastructure.note_repository"), CONTEXT
            )

            # Assert
            assert result == ImportResolutionProjection(
                targets=("notes/infrastructure/note_repository.py",)
            )

        def then_a_package_lands_on_its_init(self, target):
            # Act
            result = target.apply(IMPORTER, absolute("app.shared.ports"), CONTEXT)

            # Assert
            assert result.targets == ("shared/ports/__init__.py",)

        def then_the_prefix_itself_lands_on_the_roots_init(self, target):
            # Act
            result = target.apply(IMPORTER, absolute("app"), CONTEXT)

            # Assert
            assert result.targets == ("__init__.py",)

    class WhenAFromImportNamesASubmodule:
        def then_it_lands_on_the_submodule_not_the_package(self, target):
            # Act
            result = target.apply(IMPORTER, absolute("app.shared.ports", "users_port"), CONTEXT)

            # Assert
            assert result.targets == ("shared/ports/users_port.py",)

    class WhenAFromImportNamesAClass:
        def then_it_lands_on_the_module_defining_it(self, target):
            # Act
            result = target.apply(
                IMPORTER,
                absolute("app.notes.infrastructure.note_repository", "NoteRepository"),
                CONTEXT,
            )

            # Assert
            assert result.targets == ("notes/infrastructure/note_repository.py",)

    class WhenAFromImportNamesASubmoduleAndAClass:
        def then_it_lands_on_both(self, target):
            # Act
            result = target.apply(
                IMPORTER, absolute("app.shared.ports", "users_port", "UsersPort"), CONTEXT
            )

            # Assert
            assert result.targets == ("shared/ports/users_port.py", "shared/ports/__init__.py")

    class WhenAnImportIsRelative:
        def then_one_dot_is_the_importers_package(self, target):
            # Act
            result = target.apply(IMPORTER, relative(1, "", "helpers"), CONTEXT)

            # Assert
            assert result.targets == ("notes/domain/helpers.py",)

        def then_two_dots_climb_a_package(self, target):
            # Act
            result = target.apply(
                IMPORTER, relative(2, "infrastructure.note_repository", "NoteRepository"), CONTEXT
            )

            # Assert
            assert result.targets == ("notes/infrastructure/note_repository.py",)

        def then_climbing_past_the_root_is_unresolved(self, target):
            # Act
            result = target.apply("main.py", relative(2, "elsewhere", "x"), CONTEXT)

            # Assert
            assert result.unresolved

    class WhenAnImportIsExternal:
        def then_it_is_counted_under_its_head(self, target):
            # Act
            result = target.apply(IMPORTER, absolute("sqlalchemy.orm", "Session"), CONTEXT)

            # Assert
            assert result == ImportResolutionProjection(external="sqlalchemy")

    class WhenALocalImportNamesNoScannedFile:
        def then_it_is_unresolved_rather_than_external(self, target):
            # Act
            result = target.apply(IMPORTER, absolute("app.missing", "x"), CONTEXT)

            # Assert
            assert result.unresolved

    class WhenTheRootIsAlsoASourceRoot:
        def then_an_unprefixed_name_resolves_too(self, target):
            # Arrange
            context = ImportContextProjection(
                files=FILES, prefixes=("", "app"), local_names=frozenset({"notes", "app"})
            )

            # Act
            result = target.apply(IMPORTER, absolute("notes.domain.helpers"), context)

            # Assert
            assert result.targets == ("notes/domain/helpers.py",)
