from metatron.config.infrastructure.repositories.package_repository import PackageRepository


def make_package(path):
    path.mkdir(parents=True, exist_ok=True)
    (path / "__init__.py").write_text("")


class GivenPackageRepository:
    class WhenTheRootIsATopLevelPackage:
        def then_imports_resolve_from_the_directory_above_it(self, tmp_path):
            # Arrange
            make_package(tmp_path / "app")
            target = PackageRepository()

            # Act
            result = target.source_roots_for(tmp_path / "app")

            # Assert
            assert result == (tmp_path,)

    class WhenTheRootIsNestedInsidePackages:
        def then_imports_resolve_from_above_the_outermost_one(self, tmp_path):
            # Arrange
            make_package(tmp_path / "src" / "metatron")
            make_package(tmp_path / "src" / "metatron" / "scan")
            target = PackageRepository()

            # Act
            result = target.source_roots_for(tmp_path / "src" / "metatron" / "scan")

            # Assert
            assert result == (tmp_path / "src",)

    class WhenTheRootIsNotAPackage:
        def then_both_the_root_and_its_parent_are_tried(self, tmp_path):
            # Arrange
            (tmp_path / "src").mkdir()
            target = PackageRepository()

            # Act
            result = target.source_roots_for(tmp_path / "src")

            # Assert
            assert result == (tmp_path / "src", tmp_path)
