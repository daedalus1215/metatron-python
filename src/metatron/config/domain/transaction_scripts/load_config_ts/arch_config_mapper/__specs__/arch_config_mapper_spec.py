from pathlib import Path

import pytest

from metatron.config.domain.transaction_scripts.load_config_ts.arch_config_mapper.arch_config_mapper import (  # noqa: E501
    ArchConfigMapper,
)
from metatron.config.domain.transaction_scripts.load_config_ts.arch_config_mapper.config_references_validator import (  # noqa: E501
    ConfigReferencesValidator,
)
from metatron.config.domain.transaction_scripts.load_config_ts.arch_config_mapper.config_shape_validator import (  # noqa: E501
    ConfigShapeValidator,
)
from metatron.config.domain.transaction_scripts.load_config_ts.arch_config_mapper.project_name_converter import (  # noqa: E501
    ProjectNameConverter,
)
from metatron.config.domain.transaction_scripts.load_config_ts.arch_config_mapper.project_name_projection import (  # noqa: E501
    ProjectNameProjection,
)
from metatron.config.domain.transaction_scripts.load_config_ts.arch_config_mapper.table_merge_converter import (  # noqa: E501
    TableMergeConverter,
)
from metatron.config.domain.transaction_scripts.load_config_ts.arch_config_mapper.table_to_arch_config_converter import (  # noqa: E501
    TableToArchConfigConverter,
)
from metatron.config.domain.transaction_scripts.load_config_ts.config_table_projection import (
    ConfigTableProjection,
)
from metatron.config.infrastructure.repositories.package_repository import PackageRepository
from metatron.shared.domain.ports.config_port import ConfigError
from metatron.shared.test_utils.test_utils import create_apply_mock

FILE = Path("/code/notes/pyproject.toml")
FOUND = ConfigTableProjection(file=FILE, table={"root": "app", "name": "notes"})
PROFILE = {"root": "src", "flow": ["action"]}
MERGED = {"root": "app", "name": "notes", "flow": ["action"]}


@pytest.fixture
def config_shape_validator_mock():
    return create_apply_mock(ConfigShapeValidator)


@pytest.fixture
def table_merge_converter_mock():
    mock = create_apply_mock(TableMergeConverter)
    mock.apply.return_value = MERGED
    return mock


@pytest.fixture
def config_references_validator_mock():
    return create_apply_mock(ConfigReferencesValidator)


@pytest.fixture
def project_name_converter_mock():
    mock = create_apply_mock(ProjectNameConverter)
    mock.apply.return_value = ProjectNameProjection(name="notes")
    return mock


@pytest.fixture
def table_to_arch_config_converter_mock():
    return create_apply_mock(TableToArchConfigConverter)


@pytest.fixture
def package_repository_mock():
    mock = create_apply_mock(PackageRepository)
    mock.source_roots_for.return_value = (Path("/code/notes"),)
    return mock


@pytest.fixture
def target(
    config_shape_validator_mock,
    table_merge_converter_mock,
    config_references_validator_mock,
    project_name_converter_mock,
    table_to_arch_config_converter_mock,
    package_repository_mock,
):
    return ArchConfigMapper(
        config_shape_validator_mock,
        table_merge_converter_mock,
        config_references_validator_mock,
        project_name_converter_mock,
        table_to_arch_config_converter_mock,
        package_repository_mock,
    )


class GivenArchConfigMapper:
    class WhenMapping:
        def then_it_validates_the_projects_table_before_merging(
            self, target, config_shape_validator_mock, table_merge_converter_mock
        ):
            # Act
            target.apply(FOUND, PROFILE)

            # Assert
            config_shape_validator_mock.apply.assert_called_once_with(FOUND.table, FILE)
            table_merge_converter_mock.apply.assert_called_once_with(PROFILE, FOUND.table)

        def then_it_checks_references_in_the_merged_table(
            self, target, config_references_validator_mock
        ):
            # Act
            target.apply(FOUND, PROFILE)

            # Assert
            config_references_validator_mock.apply.assert_called_once_with(
                MERGED, FOUND.table, FILE
            )

        def then_it_infers_source_roots_from_the_resolved_root(
            self, target, package_repository_mock
        ):
            # Act
            target.apply(FOUND, PROFILE)

            # Assert
            package_repository_mock.source_roots_for.assert_called_once_with(
                Path("/code/notes/app")
            )

        def then_it_returns_the_converted_config(self, target, table_to_arch_config_converter_mock):
            # Act
            result = target.apply(FOUND, PROFILE)

            # Assert
            table_to_arch_config_converter_mock.apply.assert_called_once_with(
                MERGED, FILE, (Path("/code/notes"),), ProjectNameProjection(name="notes")
            )
            assert result is table_to_arch_config_converter_mock.apply.return_value

    class WhenTheShapeIsWrong:
        def then_nothing_is_merged(
            self, target, config_shape_validator_mock, table_merge_converter_mock
        ):
            # Arrange
            config_shape_validator_mock.apply.side_effect = ConfigError("bad key")

            # Act & Assert
            with pytest.raises(ConfigError, match="bad key"):
                target.apply(FOUND, PROFILE)
            table_merge_converter_mock.apply.assert_not_called()
