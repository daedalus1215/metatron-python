import re

import pytest

from metatron.scan.domain.transaction_scripts.evaluate_rules_ts.findings_mapper.naming_findings_converter import (  # noqa: E501
    NamingFindingsConverter,
)
from metatron.scan.test_utils import create_mock_arch_config, create_mock_source_tree
from metatron.shared.domain.ports.config_port import NamingRuleProjection
from metatron.shared.domain.ports.model_port import InstanceProjection

DOMAIN_DTO = NamingRuleProjection(
    id="domain-dto",
    title="Dto named in the domain layer",
    test=re.compile(r"(^|/)domain/(.*/)?[^/]*dto[^/]*\.py$"),
    why="the domain says command, params and projection",
)
CONFIG = create_mock_arch_config(naming=(DOMAIN_DTO,))


@pytest.fixture
def target():
    return NamingFindingsConverter()


class GivenNamingFindingsConverter:
    class WhenTheDomainNamesADto:
        def then_each_such_file_is_an_instance(self, target):
            # Arrange
            tree = create_mock_source_tree(
                {
                    "notes/domain/services/create_note_dto.py": "dto",
                    "notes/application/actions/create_note_request_dto.py": "dto",
                }
            )

            # Act
            result = target.apply(CONFIG, tree)

            # Assert
            assert [(f.id, f.title) for f in result] == [
                ("naming-domain-dto", "Dto named in the domain layer")
            ]
            assert result[0].instances == (
                InstanceProjection("notes/domain/services/create_note_dto.py", ""),
            )

    class WhenNoFileBreaksARule:
        def then_there_is_no_finding(self, target):
            # Arrange
            tree = create_mock_source_tree({"notes/domain/create_note_command.py": "command"})

            # Act
            result = target.apply(CONFIG, tree)

            # Assert
            assert result == ()
