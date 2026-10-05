from metatron.shared.domain.ports.config_port import ArchConfigProjection
from metatron.shared.domain.ports.model_port import (
    FindingProjection,
    InstanceProjection,
    SourceTreeProjection,
)


class NamingFindingsConverter:
    """`naming-{id}`: every file a naming rule matches is named against the convention."""

    def apply(
        self, config: ArchConfigProjection, tree: SourceTreeProjection
    ) -> tuple[FindingProjection, ...]:
        findings = []
        for rule in config.naming:
            hits = tuple(file.path for file in tree.files if rule.test.search(file.path))
            if hits:
                findings.append(
                    FindingProjection(
                        id=f"naming-{rule.id}",
                        tone="warn",
                        title=rule.title,
                        detail=rule.why,
                        items=hits,
                        instances=tuple(InstanceProjection(path, "") for path in hits),
                    )
                )
        return tuple(findings)
