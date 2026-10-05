import pytest

from metatron.shared.utils.text_utils import count


class GivenCount:
    @pytest.mark.parametrize(
        ("n", "noun", "plural", "expected"),
        [
            (1, "call", None, "1 call"),
            (0, "call", None, "0 calls"),
            (2, "call", None, "2 calls"),
            (2, "directory", "directories", "2 directories"),
        ],
    )
    def then_it_agrees_with_the_number(self, n, noun, plural, expected):
        # Act & Assert
        assert count(n, noun, plural) == expected
