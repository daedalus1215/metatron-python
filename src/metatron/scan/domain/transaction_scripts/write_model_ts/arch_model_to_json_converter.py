from typing import Any

from metatron.shared.domain.ports.model_port import ArchModelProjection


class ArchModelToJsonConverter:
    """The model as `model.json`: metatron-nestjs's key names wherever the two share a concept.

    No timestamp: the same tree scanned twice writes the same bytes.
    """

    def apply(self, model: ArchModelProjection) -> dict[str, Any]:
        tree, coverage = model.tree, model.tree.coverage
        modules: dict[str, int] = {}
        for file in tree.files:
            modules[file.module] = modules.get(file.module, 0) + 1
        return {
            "project": model.project,
            "root": model.root,
            "tiers": [{"i": i, "name": t.name, "sub": t.sub} for i, t in enumerate(model.tiers)],
            "flow": list(model.flow),
            "skipRules": [
                {
                    "id": r.id,
                    "from": r.source,
                    "to": r.target,
                    "sev": r.severity,
                    "jump": r.jump,
                    "why": r.why,
                }
                for r in model.skip_rules
            ],
            "stats": {
                "files": len(tree.files),
                "edges": len(tree.edges),
                "externals": len(tree.externals),
                "modules": len(modules),
            },
            "coverage": {
                "files": coverage.files,
                "classified": coverage.classified,
                "unclassifiedCount": len(coverage.unclassified),
                "unclassifiedPct": round(100 - coverage.percent, 1),
                "samples": list(coverage.unclassified),
                "byPattern": dict(coverage.by_pattern),
            },
            "modules": [
                {"id": module, "files": files}
                for module, files in sorted(modules.items(), key=lambda m: (-m[1], m[0]))
            ],
            "fileNodes": [
                {
                    "f": f.path,
                    "m": f.module,
                    "d": f.folder,
                    "p": f.pattern,
                    "t": f.tier,
                    "loc": f.loc,
                }
                for f in tree.files
            ],
            "imports": [{"from": e.source, "to": e.target, "line": e.line} for e in tree.edges],
            "externals": dict(tree.externals),
            "findings": [
                {
                    "id": f.id,
                    "tone": f.tone,
                    "title": f.title,
                    "detail": f.detail,
                    "items": list(f.items),
                    "instances": [{"from": i.source, "to": i.target} for i in f.instances],
                    "gate": f.gate,
                }
                for f in model.findings
            ],
            "violations": [
                {
                    "fingerprint": v.fingerprint,
                    "rule": v.rule,
                    "from": v.source,
                    "to": v.target,
                    "sev": v.severity,
                }
                for v in model.violations
            ],
            "diagnostics": [
                {"kind": d.kind, "file": d.file, "line": d.line, "detail": d.detail}
                for d in tree.diagnostics
            ],
        }
