"""The installed ways in: `python -m metatron` and the `metatron-py` script."""

import subprocess
import sys


class GivenTheEntryPoints:
    class WhenRunAsAModule:
        def then_it_is_the_same_cli(self):
            # Act
            result = subprocess.run(
                [sys.executable, "-m", "metatron", "--help"],
                capture_output=True,
                text=True,
                check=False,
            )

            # Assert
            assert result.returncode == 0
            assert "usage: metatron-py" in result.stdout
