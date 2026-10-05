from dataclasses import replace
from pathlib import Path

import pytest

from metatron.scan.application.actions.scan.scan_responder import ScanResponder
from metatron.scan.domain.services.scan_result_projection import ScanResultProjection
from metatron.scan.test_utils import (
    create_mock_arch_config,
    create_mock_arch_model,
    create_mock_source_tree,
)
from metatron.shared.domain.ports.model_port import (
    CoverageProjection,
    DiagnosticProjection,
    FindingProjection,
    InstanceProjection,
    ViolationProjection,
)

CWD = Path("/code/notes")
TREE = create_mock_source_tree({"notes/a_action.py": "action", "notes/b_service.py": "service"})


def result(**overrides):
    return ScanResultProjection(
        config=create_mock_arch_config(),
        model=create_mock_arch_model(**{"tree": TREE, **overrides}),
        model_path=CWD / ".metatron" / "model.json",
    )


@pytest.fixture
def target():
    return ScanResponder()


class GivenScanResponder:
    class WhenTheScanIsClean:
        def then_it_leads_with_coverage_and_ends_with_where_the_model_went(self, target):
            # Act
            result_text = target.apply(result(), CWD)

            # Assert
            lines = result_text.splitlines()
            assert lines[0] == "metatron scan · notes"
            assert lines[2] == "  coverage 2/2 (100.0%)"
            assert lines[3] == "  2 files · 0 imports · 1 module · 0 externals"
            assert lines[-1] == "  -> .metatron/model.json"
            assert "  0 violations" in lines

    class WhenAFindingWarns:
        def then_its_items_are_listed_under_it_up_to_five(self, target):
            # Arrange
            finding = FindingProjection(
                id="no-upward",
                tone="warn",
                title="7 upward calls",
                items=tuple(f"call {i}" for i in range(7)),
                instances=(InstanceProjection("a", "b"),),
            )
            violation = ViolationProjection("f", "no-upward", "a", "b", "crit")

            # Act
            text = target.apply(result(findings=(finding,), violations=(violation,)), CWD)

            # Assert
            assert "    ! no-upward                     7 upward calls" in text
            assert "        call 4\n        ... 2 more" in text
            assert "  1 violation (1 crit)" in text

    class WhenAWarningIsNotGated:
        def then_it_says_so(self, target):
            # Arrange
            finding = FindingProjection(id="dag", tone="warn", title="loop", gate=False)

            # Act
            text = target.apply(result(findings=(finding,)), CWD)

            # Assert
            assert "loop  (not gated)" in text

    class WhenTheScanHasDiagnostics:
        def then_they_are_grouped_by_kind_and_flagged(self, target):
            # Arrange
            diagnostic = DiagnosticProjection("parse-failed", "notes/x.py", 2, "invalid syntax")
            tree = replace(TREE, diagnostics=(diagnostic,))

            # Act
            text = target.apply(result(tree=tree), CWD)

            # Assert
            assert (
                "  1 scan diagnostic  !\n    parse-failed  1x\n      notes/x.py:2  invalid syntax"
            ) in text

    class WhenFilesMatchedNoPattern:
        def then_coverage_is_flagged_and_they_are_grouped_by_suffix(self, target):
            # Arrange
            coverage = CoverageProjection(
                files=4,
                classified=2,
                unclassified=("notes/a_exception.py", "notes/b_exception.py"),
                by_pattern={},
            )

            # Act
            text = target.apply(result(tree=replace(TREE, coverage=coverage)), CWD)

            # Assert
            assert "  coverage 2/4 (50.0%)  !!" in text
            assert (
                "2 files matched no pattern. Add them to `add-patterns` in pyproject.toml:" in text
            )
            assert "    _exception.py            2x   e.g. notes/a_exception.py" in text
