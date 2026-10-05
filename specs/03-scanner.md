---
title: "Scanner: files, imports, classification"
status: implemented
implemented: 2026-10-03
project: metatron-python
location: specs/03-scanner.md
created: 2026-10-03
tags: [foundation, scanner, ast]
---

# 03 — Scanner: files, imports, classification

Turns the tree under `root` into a `SourceTreeProjection`: every `.py` file
with its pattern and tier, every import that lands on another scanned file, and
everything the scanner declined to interpret.

## Files

Every `*.py` under `root` whose root-relative path matches no `ignore` regex.
Paths in the model are root-relative and use `/`.

| field | meaning |
|---|---|
| `module` | the bounded context: the first path segment, or `(root)` for a file at the top |
| `folder` | up to three segments deep, as in metatron-nestjs; same-pattern imports inside one folder are a helper split, not a violation |
| `pattern`, `tier` | the first pattern whose regex `search`es the path, or the fallback |
| `loc` | lines |

## Imports

Read with `ast`, from the whole file. That includes imports inside functions and
under `if TYPE_CHECKING:`, because metatron-nestjs counts type-only imports too.

| written | tried, in order |
|---|---|
| `import a.b` | `a/b.py`, `a/b/__init__.py` |
| `from a.b import c` | `a/b/c.py`, `a/b/c/__init__.py` (a submodule), then `a/b.py`, `a/b/__init__.py` |
| `from . import c` | `c.py` or `c/__init__.py` beside the importer, then the package's `__init__.py` |
| `from ..x import c` | as above, one package up |

An absolute name resolves through each source root. The scanned root sits at a
dotted prefix below a source root (`app`, `metatron`, or nothing), and a name
under that prefix maps onto the scanned tree.

Each import ends up one of three ways:

- **an edge** to the scanned file it names. Edges are deduplicated by
  `(from, to)`, keeping the first line.
- **external**: the head of the name is not a package at any source root. It is
  counted under that head (`fastapi`, `sqlalchemy`, `os`).
- **`import-unresolved`**: the head is local, or the import is relative, but no
  scanned file matches. A diagnostic, never dropped.

## Refusals

- A file `ast` cannot parse is `parse-failed`, with the line. It is still
  classified and counted. It has no edges, and coverage does not pretend
  otherwise.
- `import-unresolved` covers the case of scanning a subtree too. "Names no file
  in the scanned tree" is literally true there.
- A dynamic `importlib.import_module(name)` is not read. Neither is
  `__import__`. Wiring that hides in strings is invisible, as in metatron-nestjs.

## Coverage

Printed first, before anything else the scan says:

```
coverage 119/121 (98.3%)
  2 files matched no pattern:
    _exception.py   2x   e.g. notes/domain/not_found_exception.py
```

Unmatched files are grouped by their last `_suffix.py`, so the fix is one
`add-patterns` line per group.

## Acceptance

- A fixture with relative, absolute, submodule, `TYPE_CHECKING` and in-function
  imports produces exactly the expected edges.
- A file with a syntax error yields one `parse-failed` and no crash.
- `import fastapi` counts as an external, while `from app.missing import x` is
  `import-unresolved`.
