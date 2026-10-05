import os
import posixpath
import re
from collections import defaultdict
from pathlib import Path

from metatron.scan.domain.services.scan_result_projection import ScanResultProjection
from metatron.scan.domain.utils.text_utils import count
from metatron.shared.domain.ports.model_port import (
    ArchModelProjection,
    CoverageProjection,
    FindingProjection,
)

MARK = {"good": "✓", "warn": "!", "note": "·"}
SHOWN = 5


class ScanResponder:
    """What `metatron-py scan` prints. Coverage comes first: it says whether to trust the rest."""

    def apply(self, result: ScanResultProjection, cwd: Path) -> str:
        model = result.model
        lines = [
            f"metatron scan · {model.project}",
            "",
            self._coverage(model.tree.coverage),
            self._stats(model),
            *self._diagnostics(model),
            "",
            "  rules",
            *(line for finding in model.findings for line in self._finding(finding)),
            "",
            f"  {self._violations(model)}",
            *self._unclassified(model.tree.coverage, self._shown(result.config.config_file, cwd)),
            "",
            f"  -> {self._shown(result.model_path, cwd)}",
        ]
        return "\n".join(lines)

    def _coverage(self, coverage: CoverageProjection) -> str:
        missed = 100 - coverage.percent
        flag = "  !!" if missed > 25 else "  !" if missed > 10 else ""
        return f"  coverage {coverage.classified}/{coverage.files} ({coverage.percent}%){flag}"

    def _stats(self, model: ArchModelProjection) -> str:
        tree = model.tree
        modules = len({file.module for file in tree.files})
        return (
            f"  {count(len(tree.files), 'file')} · {count(len(tree.edges), 'import')}"
            f" · {count(modules, 'module')} · {count(len(tree.externals), 'external')}"
        )

    def _diagnostics(self, model: ArchModelProjection) -> list[str]:
        diagnostics = model.tree.diagnostics
        if not diagnostics:
            return []
        by_kind = defaultdict(list)
        for diagnostic in diagnostics:
            by_kind[diagnostic.kind].append(diagnostic)
        lines = [f"  {count(len(diagnostics), 'scan diagnostic')}  !"]
        for kind, found in sorted(by_kind.items(), key=lambda k: (-len(k[1]), k[0])):
            lines.append(f"    {kind}  {len(found)}x")
            lines += [f"      {d.file}:{d.line}  {d.detail}" for d in found[:3]]
            lines += [f"      ... {len(found) - 3} more"] if len(found) > 3 else []
        return lines

    def _finding(self, finding: FindingProjection) -> list[str]:
        ungated = "  (not gated)" if finding.tone == "warn" and not finding.gate else ""
        lines = [f"    {MARK.get(finding.tone, '?')} {finding.id:<30}{finding.title}{ungated}"]
        if finding.tone == "warn":
            lines += [f"        {item}" for item in finding.items[:SHOWN]]
            hidden = len(finding.items) - SHOWN
            lines += [f"        ... {hidden} more"] if hidden > 0 else []
        return lines

    def _violations(self, model: ArchModelProjection) -> str:
        critical = sum(1 for v in model.violations if v.severity == "crit")
        return count(len(model.violations), "violation") + (
            f" ({critical} crit)" if critical else ""
        )

    def _unclassified(self, coverage: CoverageProjection, config_file: str) -> list[str]:
        if not coverage.unclassified:
            return []
        groups: dict[str, list[str]] = defaultdict(list)
        for path in coverage.unclassified:
            name = posixpath.basename(path)
            suffix = re.search(r"_[a-z0-9]+\.py$", name)
            groups[suffix.group(0) if suffix else name].append(path)
        return [
            "",
            f"  {count(len(coverage.unclassified), 'file')} matched no pattern."
            f" Add them to `add-patterns` in {config_file}:",
            *(
                f"    {suffix:<24} {len(paths)}x   e.g. {paths[0]}"
                for suffix, paths in sorted(groups.items(), key=lambda g: (-len(g[1]), g[0]))
            ),
        ]

    def _shown(self, path: Path, cwd: Path) -> str:
        relative = os.path.relpath(path, cwd)
        return str(path) if relative.startswith("..") else relative
