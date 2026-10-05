from typing import Protocol

import pytest

from metatron.shared.kernel.container import Container
from metatron.shared.kernel.module import Bind, Module


class Repository:
    pass


class TransactionScript:
    def __init__(self, repository: Repository) -> None:
        self.repository = repository


class GreeterPort(Protocol):
    def greet(self) -> str: ...


class Aggregator:
    def greet(self) -> str:
        return "hello"


class Service:
    def __init__(self, ts: TransactionScript, greeter: GreeterPort) -> None:
        self.ts = ts
        self.greeter = greeter


class Action:
    def __init__(self, service: Service) -> None:
        self.service = service


class WithDefault:
    def __init__(self, repository: Repository, label: str = "x") -> None:
        self.repository = repository
        self.label = label


class Chicken:
    def __init__(self, egg: "Egg") -> None:
        self.egg = egg


class Egg:
    def __init__(self, chicken: Chicken) -> None:
        self.chicken = chicken


class GivenContainer:
    class WhenAProviderInjectsAnother:
        def then_it_builds_the_graph_from_constructor_hints(self):
            # Arrange
            target = Container([Module(providers=[Repository, TransactionScript])])

            # Act
            result = target.get(TransactionScript)

            # Assert
            assert isinstance(result.repository, Repository)

        def then_each_implementation_is_built_once(self):
            # Arrange
            target = Container([Module(providers=[Repository, TransactionScript])])

            # Act
            result = target.get(TransactionScript)

            # Assert
            assert result.repository is target.get(Repository)

    class WhenAPortIsBoundInAnotherModule:
        def then_the_consumer_receives_the_bound_aggregator(self):
            # Arrange
            consumer = Module(providers=[Repository, TransactionScript, Service])
            provider = Module(providers=[Bind(GreeterPort, to=Aggregator)])
            target = Container([consumer, provider])

            # Act
            result = target.get(Service)

            # Assert
            assert result.greeter.greet() == "hello"
            assert result.greeter is target.get(Aggregator)

    class WhenActionsAreDeclared:
        def then_actions_returns_them_built_in_declaration_order(self):
            # Arrange
            target = Container(
                [
                    Module(providers=[Bind(GreeterPort, to=Aggregator)]),
                    Module(providers=[Repository, TransactionScript, Service], actions=[Action]),
                ]
            )

            # Act
            result = target.actions()

            # Assert
            assert [type(a) for a in result] == [Action]
            assert isinstance(result[0].service, Service)

    class WhenAParameterHasADefault:
        def then_the_default_is_kept(self):
            # Arrange
            target = Container([Module(providers=[Repository, WithDefault])])

            # Act
            result = target.get(WithDefault)

            # Assert
            assert result.label == "x"

    class WhenADependencyIsProvidedByNoModule:
        def then_it_names_the_missing_class_and_who_asked(self):
            # Arrange
            target = Container([Module(providers=[TransactionScript])])

            # Act & Assert
            expected = "no module provides Repository .*TransactionScript"
            with pytest.raises(LookupError, match=expected):
                target.get(TransactionScript)

    class WhenTwoProvidersInjectEachOther:
        def then_it_names_the_loop(self):
            # Arrange
            target = Container([Module(providers=[Chicken, Egg])])

            # Act & Assert
            with pytest.raises(LookupError, match="circular injection: Chicken -> Egg -> Chicken"):
                target.get(Chicken)
