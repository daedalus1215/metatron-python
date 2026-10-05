from pathlib import Path

import pytest

from metatron.config.domain.transaction_scripts.load_config_ts.arch_config_mapper.arch_config_mapper import (  # noqa: E501
    ArchConfigMapper,
)
from metatron.config.domain.transaction_scripts.load_config_ts.config_table_projection import (
    ConfigTableProjection,
)
from metatron.config.domain.transaction_scripts.load_config_ts.load_config_params import (
    LoadConfigParams,
)
from metatron.config.domain.transaction_scripts.load_config_ts.load_config_transaction_script import (  # noqa: E501
    LoadConfigTS,
)
from metatron.config.infrastructure.repositories.config_file_repository import (
    ConfigFileRepository,
)
from metatron.config.infrastructure.repositories.profile_repository import ProfileRepository
from metatron.shared.domain.ports.config_port import ConfigError
from metatron.shared.test_utils.test_utils import create_apply_mock

FILE = Path("/code/notes/pyproject.toml")
PROFILE = {"root": "app"}


@pytest.fixture
def config_file_repository_mock():
    return create_apply_mock(ConfigFileRepository)


@pytest.fixture
def profile_repository_mock():
    mock = create_apply_mock(ProfileRepository)
    mock.read.return_value = PROFILE
    return mock


@pytest.fixture
def arch_config_mapper_mock():
    return create_apply_mock(ArchConfigMapper)


@pytest.fixture
def target(config_file_repository_mock, profile_repository_mock, arch_config_mapper_mock):
    return LoadConfigTS(
        config_file_repository_mock, profile_repository_mock, arch_config_mapper_mock
    )


class GivenLoadConfigTS:
    class WhenATableIsFoundWithoutExtends:
        def then_it_maps_it_over_the_fastapi_profile(
            self,
            target,
            config_file_repository_mock,
            profile_repository_mock,
            arch_config_mapper_mock,
        ):
            # Arrange
            found = ConfigTableProjection(file=FILE, table={"root": "app"})
            config_file_repository_mock.find.return_value = found

            # Act
            result = target.apply(LoadConfigParams(start=Path("/code/notes/app")))

            # Assert
            config_file_repository_mock.find.assert_called_once_with(Path("/code/notes/app"))
            profile_repository_mock.read.assert_called_once_with("fastapi")
            arch_config_mapper_mock.apply.assert_called_once_with(found, PROFILE)
            assert result is arch_config_mapper_mock.apply.return_value

    class WhenTheTableNamesItsProfile:
        def then_that_profile_is_read(
            self, target, config_file_repository_mock, profile_repository_mock
        ):
            # Arrange
            found = ConfigTableProjection(file=FILE, table={"extends": "litestar"})
            config_file_repository_mock.find.return_value = found

            # Act
            target.apply(LoadConfigParams(start=FILE))

            # Assert
            profile_repository_mock.read.assert_called_once_with("litestar")

    class WhenNoTableIsFound:
        def then_it_raises_showing_how_to_add_one(
            self, target, config_file_repository_mock, arch_config_mapper_mock
        ):
            # Arrange
            config_file_repository_mock.find.return_value = None

            # Act & Assert
            with pytest.raises(
                ConfigError, match=r"No metatron config found[\s\S]*\[tool.metatron\]"
            ):
                target.apply(LoadConfigParams(start=Path("/nowhere")))
            arch_config_mapper_mock.apply.assert_not_called()
