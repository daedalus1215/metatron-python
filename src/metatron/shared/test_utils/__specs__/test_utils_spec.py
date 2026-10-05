import pytest

from metatron.shared.test_utils.test_utils import create_apply_mock


class SomeTS:
    def apply(self, value: int) -> str:
        return str(value)


class GivenCreateApplyMock:
    class WhenTheMockIsCalledWithTheRightArguments:
        def then_it_records_the_call(self):
            # Arrange
            target = create_apply_mock(SomeTS)
            target.apply.return_value = "42"

            # Act
            result = target.apply(42)

            # Assert
            target.apply.assert_called_once_with(42)
            assert result == "42"

    class WhenTheMockIsCalledWithTheWrongArguments:
        def then_it_raises_like_the_real_signature_would(self):
            # Arrange
            target = create_apply_mock(SomeTS)

            # Act & Assert
            with pytest.raises(TypeError):
                target.apply(1, 2)

    class WhenAMethodIsReplaced:
        def then_the_stub_is_used(self):
            # Arrange
            target = create_apply_mock(SomeTS, apply=lambda value: "stub")

            # Act
            result = target.apply(1)

            # Assert
            assert result == "stub"
