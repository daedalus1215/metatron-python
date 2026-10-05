import json

import pytest

from metatron.scan.domain.transaction_scripts.write_model_ts.arch_model_to_json_converter import (  # noqa: E501
    ArchModelToJsonConverter,
)
from metatron.scan.test_utils import create_mock_arch_model, create_mock_source_tree
from metatron.shared.domain.ports.model_port import (
    CoverageProjection,
    DiagnosticProjection,
    FindingProjection,
    InstanceProjection,
    SkipRuleProjection,
    ViolationProjection,
)

TREE = create_mock_source_tree(
    {"notes/a_action.py": "action", "notes/r_repository.py": "repository", "main.py": "other"},
    [("notes/a_action.py", "notes/r_repository.py")],
)
MODEL = create_mock_arch_model(
    tree=type(TREE)(
        files=TREE.files,
        edges=TREE.edges,
        externals={"fastapi": 2},
        diagnostics=(DiagnosticProjection("parse-failed", "main.py", 3, "invalid syntax"),),
        coverage=CoverageProjection(3, 2, ("main.py",), {"action": 1, "other": 1, "repository": 1}),
    ),
    skip_rules=(SkipRuleProjection("action>repository", "action", "repository", "crit", 2, "w"),),
    findings=(
        FindingProjection(
            id="action>repository",
            tone="warn",
            title="w",
            instances=(InstanceProjection("notes/a_action.py", "notes/r_repository.py"),),
        ),
    ),
    violations=(
        ViolationProjection(
            "abc123", "action>repository", "notes/a_action.py", "notes/r_repository.py", "crit"
        ),
    ),
)


@pytest.fixture
def target():
    return ArchModelToJsonConverter()


class GivenArchModelToJsonConverter:
    class WhenConverting:
        def then_it_is_plain_json(self, target):
            # Act
            result = target.apply(MODEL)

            # Assert
            assert json.loads(json.dumps(result)) == result

        def then_it_uses_metatron_nestjs_key_names(self, target):
            # Act
            result = target.apply(MODEL)

            # Assert
            assert result["skipRules"][0]["from"] == "action"
            assert result["coverage"]["unclassifiedPct"] == 33.3
            assert result["violations"] == [
                {
                    "fingerprint": "abc123",
                    "rule": "action>repository",
                    "from": "notes/a_action.py",
                    "to": "notes/r_repository.py",
                    "sev": "crit",
                }
            ]

        def then_modules_are_counted_largest_first(self, target):
            # Act
            result = target.apply(MODEL)

            # Assert
            assert result["modules"] == [{"id": "notes", "files": 2}, {"id": "(root)", "files": 1}]

        def then_imports_externals_and_diagnostics_are_kept(self, target):
            # Act
            result = target.apply(MODEL)

            # Assert
            assert result["imports"] == [
                {"from": "notes/a_action.py", "to": "notes/r_repository.py", "line": 1}
            ]
            assert result["externals"] == {"fastapi": 2}
            assert result["diagnostics"][0]["kind"] == "parse-failed"

        def then_the_same_model_converts_to_the_same_document(self, target):
            # Act & Assert
            assert target.apply(MODEL) == target.apply(MODEL)
