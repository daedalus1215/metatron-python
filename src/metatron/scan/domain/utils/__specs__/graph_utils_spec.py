from metatron.scan.domain.utils.graph_utils import cycles


class GivenCycles:
    class WhenTheGraphIsAcyclic:
        def then_there_are_none(self):
            # Act
            result = cycles([("a", "b"), ("b", "c"), ("a", "c")])

            # Assert
            assert result == ()

    class WhenTwoNodesImportEachOther:
        def then_they_are_one_cycle(self):
            # Act
            result = cycles([("b", "a"), ("a", "b"), ("a", "c")])

            # Assert
            assert result == (("a", "b"),)

    class WhenThereAreSeparateLoops:
        def then_each_is_reported_once_in_sorted_order(self):
            # Act
            result = cycles([("x", "y"), ("y", "z"), ("z", "x"), ("b", "a"), ("a", "b")])

            # Assert
            assert result == (("a", "b"), ("x", "y", "z"))

    class WhenANodeImportsItself:
        def then_it_is_not_a_cycle(self):
            # Act
            result = cycles([("a", "a")])

            # Assert
            assert result == ()

    class WhenTheLoopIsThousandsDeep:
        def then_it_is_found_without_recursion(self):
            # Arrange
            nodes = [f"n{i:05}" for i in range(5000)]
            edges = list(zip(nodes, nodes[1:] + nodes[:1], strict=True))

            # Act
            result = cycles(edges)

            # Assert
            assert result == (tuple(nodes),)
