import pytest

from metatron.main import main


@pytest.fixture
def project(tmp_path):
    (tmp_path / "pyproject.toml").write_text('[tool.metatron]\nroot = "app"\n')
    (tmp_path / "app").mkdir()
    (tmp_path / "app" / "__init__.py").write_text("")
    (tmp_path / "app" / "main.py").write_text("import fastapi\n")
    return tmp_path


class GivenMain:
    class WhenTheScanCommandIsGiven:
        def then_it_runs_the_scan_and_exits_zero(self, project, capsys):
            # Act
            result = main(["scan", str(project)])

            # Assert
            assert result == 0
            assert "coverage 2/2 (100.0%)" in capsys.readouterr().out

    class WhenOnlyAPathIsGiven:
        def then_it_means_scan(self, project, capsys):
            # Act
            result = main([str(project)])

            # Assert
            assert result == 0
            assert capsys.readouterr().out.startswith("metatron scan · ")

    class WhenThereIsNoConfig:
        def then_it_says_how_to_add_one_and_exits_two(self, tmp_path, capsys):
            # Act
            result = main(["scan", str(tmp_path)])

            # Assert
            assert result == 2
            assert "[tool.metatron]" in capsys.readouterr().err

    class WhenAskedForHelp:
        def then_it_lists_the_commands(self, capsys):
            # Act & Assert
            with pytest.raises(SystemExit) as exited:
                main(["--help"])
            assert exited.value.code == 0
            assert "scan" in capsys.readouterr().out
