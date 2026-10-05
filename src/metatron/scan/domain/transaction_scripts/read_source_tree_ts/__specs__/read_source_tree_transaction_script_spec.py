import pytest

from metatron.scan.domain.transaction_scripts.read_source_tree_ts.read_source_tree_params import (
    ReadSourceTreeParams,
)
from metatron.scan.domain.transaction_scripts.read_source_tree_ts.read_source_tree_transaction_script import (  # noqa: E501
    ReadSourceTreeTS,
)
from metatron.scan.domain.transaction_scripts.read_source_tree_ts.source_text_projection import (
    SourceTextProjection,
)
from metatron.scan.domain.transaction_scripts.read_source_tree_ts.source_tree_mapper.source_tree_mapper import (  # noqa: E501
    SourceTreeMapper,
)
from metatron.scan.infrastructure.repositories.source_file_repository import (
    SourceFileRepository,
)
from metatron.scan.test_utils import create_mock_arch_config
from metatron.shared.domain.ports.config_port import ConfigError
from metatron.shared.test_utils.test_utils import create_apply_mock

CONFIG = create_mock_arch_config()
SOURCES = (SourceTextProjection(path="main.py", text=""),)
LOCAL = frozenset({"app"})


@pytest.fixture
def source_file_repository_mock():
    mock = create_apply_mock(SourceFileRepository)
    mock.read_tree.return_value = SOURCES
    mock.local_top_level_names.return_value = LOCAL
    return mock


@pytest.fixture
def source_tree_mapper_mock():
    return create_apply_mock(SourceTreeMapper)


@pytest.fixture
def target(source_file_repository_mock, source_tree_mapper_mock):
    return ReadSourceTreeTS(source_file_repository_mock, source_tree_mapper_mock)


class GivenReadSourceTreeTS:
    class WhenTheRootHoldsPython:
        def then_it_maps_what_the_repository_read(
            self, target, source_file_repository_mock, source_tree_mapper_mock
        ):
            # Act
            result = target.apply(ReadSourceTreeParams(config=CONFIG))

            # Assert
            source_file_repository_mock.read_tree.assert_called_once_with(
                CONFIG.root, CONFIG.ignore
            )
            source_file_repository_mock.local_top_level_names.assert_called_once_with(
                CONFIG.source_roots
            )
            source_tree_mapper_mock.apply.assert_called_once_with(SOURCES, CONFIG, LOCAL)
            assert result is source_tree_mapper_mock.apply.return_value

    class WhenTheRootHoldsNoPython:
        def then_it_raises_rather_than_reporting_an_empty_architecture(
            self, target, source_file_repository_mock, source_tree_mapper_mock
        ):
            # Arrange
            source_file_repository_mock.read_tree.return_value = ()

            # Act & Assert
            with pytest.raises(ConfigError, match="no .py files under /code/notes/app"):
                target.apply(ReadSourceTreeParams(config=CONFIG))
            source_tree_mapper_mock.apply.assert_not_called()
