import pytest

from metatron.scan.domain.transaction_scripts.evaluate_rules_ts.findings_mapper.layer_findings_converter import (  # noqa: E501
    LayerFindingsConverter,
)
from metatron.scan.test_utils import create_mock_arch_config, create_mock_source_tree
from metatron.shared.domain.ports.config_port import LayerRuleProjection
from metatron.shared.domain.ports.model_port import InstanceProjection

CONFIG = create_mock_arch_config(
    layers=(
        LayerRuleProjection(
            "domain-no-application", "domain", "application", "the domain depends on the app"
        ),
        LayerRuleProjection(
            "infrastructure-no-application", "infrastructure", "application", "infra depends"
        ),
    )
)
FILES = {
    "notes/application/actions/create_note/create_note_request_dto.py": "dto",
    "notes/application/actions/create_note/create_note_action.py": "action",
    "notes/domain/services/note_service.py": "service",
    "notes/infrastructure/repositories/note_repository.py": "repository",
    "application.py": "bootstrap",
}


@pytest.fixture
def target():
    return LayerFindingsConverter()


class GivenLayerFindingsConverter:
    class WhenTheDomainImportsTheApplicationLayer:
        def then_that_rule_warns_and_the_other_holds(self, target):
            # Arrange
            edge = (
                "notes/domain/services/note_service.py",
                "notes/application/actions/create_note/create_note_request_dto.py",
            )
            tree = create_mock_source_tree(FILES, [edge])

            # Act
            result = target.apply(CONFIG, tree)

            # Assert
            assert [(f.id, f.tone) for f in result] == [
                ("domain-no-application", "warn"),
                ("infrastructure-no-application", "good"),
            ]
            assert result[0].title == "1 import where the domain depends on the app"
            assert result[0].instances == (InstanceProjection(*edge),)

    class WhenTheApplicationImportsTheDomain:
        def then_every_rule_holds(self, target):
            # Arrange
            tree = create_mock_source_tree(
                FILES,
                [
                    (
                        "notes/application/actions/create_note/create_note_action.py",
                        "notes/domain/services/note_service.py",
                    )
                ],
            )

            # Act
            result = target.apply(CONFIG, tree)

            # Assert
            assert [f.tone for f in result] == ["good", "good"]

    class WhenAFileIsNamedLikeALayerButSitsOutsideOne:
        def then_its_file_name_does_not_put_it_in_the_layer(self, target):
            # Arrange
            tree = create_mock_source_tree(
                FILES, [("notes/domain/services/note_service.py", "application.py")]
            )

            # Act
            result = target.apply(CONFIG, tree)

            # Assert
            assert result[0].tone == "good"
