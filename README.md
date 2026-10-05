# metatron-python

Point it at a Python (FastAPI) backend and get a measured model of its
architecture, plus a list of every place the code breaks its own rules. Then
hold the line: record today's violations and fail the build when a new one
appears.

A Python port of [`metatron-nestjs`](../metatron-nestjs), in the way
[`metatron-rust`](../metatron-rust) is a Rust one. The rules are the PD
engineering patterns' dependency matrix, the same layers and the same
"no same-level injection", written for Python file names. Nothing in the
output is written by hand: every file is one that exists, every edge is an
`import` a file actually makes, and every finding is assembled from what the
scan found.

---

## Start here

**1. Install it.**

```bash
uv tool install git+https://github.com/daedalus1215/metatron-python
# or, from a checkout
uv tool install --editable .
```

No runtime dependencies: the scanner is the standard library's `ast`.

**2. Add one table** to the `pyproject.toml` beside the code you want scanned:

```toml
[tool.metatron]
root = "app"
```

A standalone `metatron.toml` works too; its whole file is the table.

**3. Run it.**

```bash
metatron-py              # or: metatron-py ~/code/notes-api
```

```
metatron scan · notes_api

  coverage 22/22 (100.0%)
  22 files · 22 imports · 4 modules · 5 externals

  rules
    ! cross-domain                  1 cross-domain import bypasses the gateways
        users/service -> notes/domain/entities/note_entity.py
    ✓ dag                           Bounded contexts form a DAG
    ! no-same-level                 1 same-level import
        [transaction-script] notes/domain/transaction_scripts/archive_note_ts/… -> …/create_note_ts/…
    ! no-upward                     1 upward call
        a Transaction Script calls upward into a Service: …/create_note_transaction_script.py -> …/note_service.py
    ! domain-no-application         1 import where the domain layer depends on the application layer
    ✓ infrastructure-no-application No infrastructure/ file imports from application/
    ! action>transaction-script     Action reaches Transaction Script directly, skipping Service
        notes/application/routers/notes_router.py  ->  …/archive_note_transaction_script.py
    ! action>repository             Action reaches Repository directly, skipping Service and Transaction Script
    ! naming-domain-dto             Dto named in the domain layer
    ! circular                      1 import cycle between files
    · absent-patterns               22 configured patterns exist nowhere in the code

  8 violations (1 crit)

  -> .metatron/model.json
```

That is [`tests/fixtures/notes_api`](tests/fixtures/notes_api), a FastAPI app
in the PD layout that breaks each rule once on purpose.

---

## If it says coverage is low

Coverage is printed first because it says whether to trust the rest. When files
match no pattern, they are grouped by suffix:

```
  coverage 41/43 (95.3%)
  ...
  2 files matched no pattern. Add them to `add-patterns` in pyproject.toml:
    _exception.py            2x   e.g. notes/domain/not_found_exception.py
```

Say which layer each group belongs to, and re-run:

```toml
[tool.metatron]
root = "app"
add-patterns = [
    { id = "exception", tier = "Contract", test = '_exception\.py$' },
]
```

A tool that quietly files half your code under "other", then draws a confident
picture of it, is worse than one that fails.

## If it prints diagnostics

Anything the scan declined to interpret is listed, never dropped:

```
  2 scan diagnostics  !
    import-unresolved  1x
      notes/domain/x.py:3  'from app.missing import thing' names no file in the scanned tree
    parse-failed  1x
      notes/broken.py:7  invalid syntax
```

`import-unresolved` is a local import (relative, or starting with one of your
own top-level packages) that names no scanned file. `parse-failed` is a file
`ast` could not read. It still counts, but has no edges.

---

## Holding the line

```bash
metatron-py baseline     # writes arch.baseline.json beside the config
metatron-py check        # exit 0 clean, 1 new violations, 2 tool or config error
```

```
metatron check · notes_api

  new violations        2
    cross-domain          notes/domain/aggregators/notes_aggregator.py
                          -> users/domain/services/user_service.py
    no-upward             notes/domain/aggregators/notes_aggregator.py
                          -> users/domain/services/user_service.py

  known, unchanged      8

FAIL — 2 new violations. Fix it, or run `metatron-py baseline --update` to accept it.
```

Commit the baseline. It is metatron-nestjs's format: one entry per violation,
fingerprinted `sha1(rule|from|to)[:12]`. That lets `check` name the offender,
and it catches a swap (one fixed, one added), which a count per rule nets to
zero. Add a `note` to any entry to record why it is tolerated;
`baseline --update` keeps it. There is no timestamp, so an unchanged tree
re-records to the same bytes.

| flag | effect |
|---|---|
| `check --rule <id>` | gate on this rule only (repeatable); the rest is advisory |
| `check --allow-new <n>` | tolerate up to n new violations while ratcheting down |
| `check --no-fixed` | do not list violations fixed since the baseline |
| `check --json` | the comparison as JSON |
| `baseline --update` | rewrite the baseline, keeping its notes |

A fixed violation is reported, never removed automatically. A scan that
failed to read a file would otherwise quietly retire a real debt.

### The gate can be a test

As in metatron-rust, the check can run inside your own suite. This repository
does exactly that, with no baseline at all, in
[`tests/architecture_spec.py`](tests/architecture_spec.py):

```python
container = Container(app_modules)
model = container.get(ModelPort).build(container.get(ConfigPort).load(REPOSITORY))
assert [(v.rule, v.source, v.target) for v in model.violations] == []
```

---

## The rules

All of these come from the `fastapi` profile. Every one is config, not code.

| finding | what breaks it | gates |
|---|---|---|
| `a>b` | `flow` is `action → service → transaction-script → repository`. Skipping one station warns; skipping two or more is `crit`. Routers, webhooks and listeners count as actions | yes |
| `no-upward` | a `forbidden` direction: every "cannot inject" cell of the dependency matrix that points up a level | yes |
| `domain-no-application`, `infrastructure-no-application` | a file under `domain/` or `infrastructure/` importing one under `application/` | yes |
| `no-same-level` | a transaction script, service, aggregator, mapper, assembler, converter, comparator, predicate, dispatcher or remote caller importing another of its kind outside its own directory | yes |
| `cross-domain` | an import between bounded contexts that lands anywhere but an aggregator or a port | yes |
| `circular` | files that reach themselves through their imports | yes |
| `naming-domain-dto` | "dto" in a file name under `domain/` | yes |
| `dag` | bounded contexts depending on each other in a loop | no |
| `absent-patterns` | configured patterns no file has | no |

`service>repository` is in `allowed-skips`: the matrix lets a Domain Service
inject a Repository for a simple lookup. Spec 04 lists the three places these
rules deliberately part from metatron-nestjs.

File names follow the patterns in snake case, since a dot cannot appear in an
importable module name: `create_note_action.py`,
`create_note_transaction_script.py` in `create_note_ts/`, `note_repository.py`,
`note_to_projection_converter.py`, `create_note_command.py`,
`archive_note_params.py`, `note_projection.py`.

---

## Commands

```bash
metatron-py [path]                  scan (the default)
metatron-py scan [path]             build the model, write .metatron/model.json, print the findings
metatron-py baseline [path]         record today's violations as accepted
metatron-py baseline --update       rewrite it, keeping hand-written notes
metatron-py check [path]            fail if a violation appeared that the baseline does not accept
metatron-py --help
```

`python -m metatron` is the same CLI.

## Config

`[tool.metatron]` in `pyproject.toml`, or a standalone `metatron.toml`, found by
walking up from the path given. Keys are kebab-case; an unknown key is an
error that suggests the right one, so a camel-cased `addPatterns` copied from
an `arch.config.js` cannot silently be ignored.

| key | meaning |
|---|---|
| `extends` | base profile; `fastapi` is the default and the only one |
| `root` | scanned directory, relative to the config file |
| `name` | shown in output; defaults to the folder, climbing past `backend/`, `src/` and friends |
| `out-dir` | where `model.json` lands; default `.metatron` |
| `source-roots` | where absolute imports resolve from; default: above the outermost package holding `root` |
| `ignore` | regexes against root-relative paths; a match is not scanned, and an ignored directory is not walked |
| `tiers` | the layers, in the order a request travels |
| `patterns` | file → pattern, first match wins; replaces the profile's list |
| `add-patterns` | prepended to the patterns, to refine without restating |
| `fallback` | the pattern an unmatched file gets |
| `flow` | the intended call path; skipped stations are violations |
| `flow-aliases` | other patterns that count as the same station |
| `allowed-skips` | derived skip rules the architecture permits |
| `forbidden` | `{ from, to = [...], why }` pattern directions that must never import |
| `layers` | `{ id, from, to, why }` directory directions that must never import |
| `no-same-level` | patterns that must not import their own kind |
| `infra-modules` | top-level packages that are plumbing, not bounded contexts |
| `cross-domain-gateways` | the only patterns a cross-context import may land on |
| `naming` | `{ id, title, test, why }` file-name rules |

The profile is [`src/metatron/config/infrastructure/profiles/fastapi.toml`](src/metatron/config/infrastructure/profiles/fastapi.toml).

## What it can't see

- **Imports are not calls.** Every edge is an import, including ones under
  `if TYPE_CHECKING:` and inside functions. An import nothing calls still
  counts, and a call made through something injected without an import is
  invisible.
- **Strings are not imports.** `importlib.import_module(name)` and
  `__import__` are not read.
- **Filenames, not decorators.** It suits projects whose conventions live in
  file names. A codebase that carries its architecture in decorators or base
  classes needs a different front end.
- **Structure, not quality.** It knows where a transaction script sits and what
  it imports, never whether it is any good.

## Not yet

The views, the workbench, `diff`, churn, coupling and endpoint traces from
metatron-nestjs are tracked in [`CHECKLIST.md`](CHECKLIST.md). The model is
written with metatron-nestjs's key names wherever the two share a concept, so
its views can follow.

---

## Working on metatron-python

```bash
uv sync
uv run pytest            # specs live beside the code in __specs__/, plus tests/
uv run pytest --cov      # at least 80%
uv run ruff check src tests
uv run metatron-py check # it must pass its own rules
```

The tool is built in the shape it checks: bounded contexts `config`, `scan` and
`baseline`, each with `application/` actions, `domain/` services, transaction
scripts and converters, and `infrastructure/` repositories. They are wired by a
small constructor-injection container and talk to each other only through ports
in `shared/`. Read [`specs/01-own-layout.md`](specs/01-own-layout.md) first;
the specs are numbered by dependency.

MIT.
