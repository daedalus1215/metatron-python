from metatron.config.domain.transaction_scripts.load_config_ts.arch_config_mapper.table_merge_converter import (  # noqa: E501
    TableMergeConverter,
)

PROFILE = {
    "root": "app",
    "flow": ["action", "service"],
    "patterns": [{"id": "service", "tier": "Service", "test": "_service\\.py$"}],
}
EXCEPTION = {"id": "exception", "tier": "Contract", "test": "_exception\\.py$"}


class GivenTableMergeConverter:
    class WhenTheProjectSetsAKey:
        def then_it_replaces_the_profiles_value_wholesale(self):
            # Arrange
            target = TableMergeConverter()

            # Act
            result = target.apply(PROFILE, {"flow": ["action"]})

            # Assert
            assert result["flow"] == ["action"]
            assert result["root"] == "app"

    class WhenTheProjectAddsPatterns:
        def then_they_are_tried_before_the_profiles(self):
            # Arrange
            target = TableMergeConverter()

            # Act
            result = target.apply(PROFILE, {"add-patterns": [EXCEPTION]})

            # Assert
            assert [p["id"] for p in result["patterns"]] == ["exception", "service"]
            assert "add-patterns" not in result

    class WhenTheProjectReplacesAndAddsPatterns:
        def then_the_additions_go_before_its_own_list(self):
            # Arrange
            own = {"id": "action", "tier": "Entry", "test": "_action\\.py$"}
            target = TableMergeConverter()

            # Act
            result = target.apply(PROFILE, {"patterns": [own], "add-patterns": [EXCEPTION]})

            # Assert
            assert [p["id"] for p in result["patterns"]] == ["exception", "action"]

    class WhenTheProjectNamesItsProfile:
        def then_extends_does_not_reach_the_merged_table(self):
            # Arrange
            target = TableMergeConverter()

            # Act
            result = target.apply(PROFILE, {"extends": "fastapi"})

            # Assert
            assert "extends" not in result

    class WhenMerging:
        def then_neither_input_is_changed(self):
            # Arrange
            profile = {**PROFILE, "patterns": list(PROFILE["patterns"])}
            project = {"add-patterns": [EXCEPTION]}
            target = TableMergeConverter()

            # Act
            target.apply(profile, project)

            # Assert
            assert len(profile["patterns"]) == 1
            assert project == {"add-patterns": [EXCEPTION]}
