"""What the cross-context rules set aside: the wiring and the tests see everything."""

SET_ASIDE_PATTERNS = frozenset({"spec", "test-util", "migration", "bootstrap", "module"})

# Files at the top of the root belong to no context.
ROOT_MODULE = "(root)"
