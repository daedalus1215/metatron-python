from metatron.scan.domain.transaction_scripts.read_source_tree_ts.source_tree_mapper.file_classification_projection import (  # noqa: E501
    FileClassificationProjection,
)
from metatron.shared.domain.ports.config_port import ArchConfigProjection


class FileClassificationConverter:
    """A path's pattern: the first whose regex searches it, else the fallback.

    Order is the config's, so the shape of a name beats the folder it sits in.
    """

    def apply(self, path: str, config: ArchConfigProjection) -> FileClassificationProjection:
        tiers = [tier.name for tier in config.tiers]
        match = next((p for p in config.patterns if p.test.search(path)), None)
        if match is None:
            return FileClassificationProjection(
                pattern=config.fallback, tier=tiers.index(config.fallback_tier)
            )
        return FileClassificationProjection(pattern=match.id, tier=tiers.index(match.tier))
