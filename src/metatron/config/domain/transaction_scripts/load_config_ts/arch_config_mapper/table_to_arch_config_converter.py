import re
from pathlib import Path
from typing import Any

from metatron.config.domain.transaction_scripts.load_config_ts.arch_config_mapper.project_name_projection import (  # noqa: E501
    ProjectNameProjection,
)
from metatron.shared.domain.ports.config_port import (
    ArchConfigProjection,
    ForbiddenProjection,
    LayerRuleProjection,
    NamingRuleProjection,
    PatternProjection,
    TierProjection,
)


class TableToArchConfigConverter:
    """A merged, validated table as the typed config a scan runs under.

    Paths resolve against the config file's directory; regexes are compiled.
    """

    def apply(
        self,
        table: dict[str, Any],
        config_file: Path,
        inferred_source_roots: tuple[Path, ...],
        name: ProjectNameProjection,
    ) -> ArchConfigProjection:
        directory = config_file.parent
        configured_roots = table.get("source-roots")
        return ArchConfigProjection(
            name=name.name,
            name_warning=name.warning,
            config_file=config_file,
            directory=directory,
            root=(directory / table["root"]).resolve(),
            source_roots=(
                tuple((directory / r).resolve() for r in configured_roots)
                if configured_roots is not None
                else inferred_source_roots
            ),
            out_dir=(directory / table.get("out-dir", ".metatron")).resolve(),
            ignore=tuple(re.compile(r) for r in table.get("ignore", [])),
            tiers=tuple(
                TierProjection(name=tier["name"], sub=tier.get("sub", ""))
                for tier in table["tiers"]
            ),
            patterns=tuple(
                PatternProjection(id=p["id"], tier=p["tier"], test=re.compile(p["test"]))
                for p in table["patterns"]
            ),
            fallback=table["fallback"]["id"],
            fallback_tier=table["fallback"]["tier"],
            flow=tuple(table.get("flow", [])),
            flow_aliases={k: tuple(v) for k, v in table.get("flow-aliases", {}).items()},
            allowed_skips=tuple(table.get("allowed-skips", [])),
            forbidden=tuple(
                ForbiddenProjection(source=rule["from"], target=target, why=rule.get("why", ""))
                for rule in table.get("forbidden", [])
                for target in ([rule["to"]] if isinstance(rule["to"], str) else rule["to"])
            ),
            layers=tuple(
                LayerRuleProjection(
                    id=rule["id"], source=rule["from"], target=rule["to"], why=rule.get("why", "")
                )
                for rule in table.get("layers", [])
            ),
            no_same_level=tuple(table.get("no-same-level", [])),
            infra_modules=tuple(table.get("infra-modules", [])),
            cross_domain_gateways=tuple(table.get("cross-domain-gateways", [])),
            naming=tuple(
                NamingRuleProjection(
                    id=rule["id"],
                    title=rule.get("title", rule["id"]),
                    test=re.compile(rule["test"]),
                    why=rule.get("why", ""),
                )
                for rule in table.get("naming", [])
            ),
        )
