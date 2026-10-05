"""Spec 04's acceptance: a FastAPI app in the PD layout that breaks each gating rule once."""

from pathlib import Path

import pytest

from metatron.app_module import app_modules
from metatron.shared.domain.ports.config_port import ConfigPort
from metatron.shared.domain.ports.model_port import ModelPort
from metatron.shared.kernel.container import Container

NOTES_API = Path(__file__).resolve().parent / "fixtures" / "notes_api"
NOTES = "notes/domain"


@pytest.fixture(scope="module")
def model():
    container = Container(app_modules)
    return container.get(ModelPort).build(container.get(ConfigPort).load(NOTES_API))


def violation_of(model, rule):
    found = [v for v in model.violations if v.rule == rule]
    assert len(found) == 1, f"{rule}: {found}"
    return found[0]


class GivenTheNotesApi:
    class WhenItIsScanned:
        def then_every_file_is_classified(self, model):
            # Assert
            assert model.tree.coverage.percent == 100.0

        def then_each_gating_rule_is_broken_exactly_once(self, model):
            # Assert
            assert sorted(v.rule for v in model.violations) == [
                "action>repository",
                "action>transaction-script",
                "circular",
                "cross-domain",
                "domain-no-application",
                "naming-domain-dto",
                "no-same-level",
                "no-upward",
            ]

        def then_a_router_is_an_action_station(self, model):
            # Act
            result = violation_of(model, "action>transaction-script")

            # Assert
            assert result.source == "notes/application/routers/notes_router.py"

        def then_an_action_reaching_a_repository_is_critical(self, model):
            # Act
            result = violation_of(model, "action>repository")

            # Assert
            assert result.severity == "crit"

        def then_a_service_reaching_a_repository_is_allowed(self, model):
            # Arrange
            edge = (
                f"{NOTES}/services/note_service.py",
                "notes/infrastructure/repositories/note_repository.py",
            )

            # Assert
            assert not [v for v in model.violations if (v.source, v.target) == edge]

        def then_a_context_may_land_on_a_port_but_not_an_entity(self, model):
            # Act
            result = violation_of(model, "cross-domain")

            # Assert
            assert (result.source, result.target) == (
                "users/domain/services/user_service.py",
                f"{NOTES}/entities/note_entity.py",
            )

        def then_sibling_transaction_scripts_are_same_level(self, model):
            # Act
            result = violation_of(model, "no-same-level")

            # Assert
            assert result.source.endswith("archive_note_ts/archive_note_transaction_script.py")
