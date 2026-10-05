"""The gate is a test: metatron-python holds itself to its own rules, with no baseline."""

from pathlib import Path

import pytest

from metatron.app_module import app_modules
from metatron.shared.domain.ports.config_port import ConfigPort
from metatron.shared.domain.ports.model_port import ModelPort
from metatron.shared.kernel.container import Container

REPOSITORY = Path(__file__).resolve().parents[1]


@pytest.fixture(scope="module")
def model():
    container = Container(app_modules)
    return container.get(ModelPort).build(container.get(ConfigPort).load(REPOSITORY))


class GivenThisRepository:
    class WhenItIsScannedUnderItsOwnConfig:
        def then_it_breaks_none_of_its_rules(self, model):
            # Assert
            assert [(v.rule, v.source, v.target) for v in model.violations] == []

        def then_every_file_is_classified(self, model):
            # Assert
            assert model.tree.coverage.unclassified == ()

        def then_nothing_was_declined(self, model):
            # Assert
            assert model.tree.diagnostics == ()
