# Checklist

What's next for metatron-python. Tick an item when it lands on `main`. An item
that grows past a few commits becomes a spec in [`specs/`](specs/README.md),
and this list links to it. The numbers in brackets are the metatron-nestjs
spec each item ports.

## Next

- [ ] **Endpoints.** Read `@router.get("/x")` and its siblings, `APIRouter(prefix=…)`
  and `include_router` into `endpoints`. A route that will not bind is a
  diagnostic, as in nestjs spec 01. This also makes "GET handlers start with
  `Fetch`" checkable.
- [ ] **Test presence crossed with risk** (nestjs 06). Locate `__specs__/x_spec.py`,
  `tests/…/test_x.py` and `x_test.py`, and suppress the finding when too many
  specs go unclaimed.
- [ ] **Churn and hotspots** from `git log --numstat`.
- [ ] **The views.** Port the `atlas`, `layers`, `city` and `hotspots` templates
  and their adapters. `model.json` already uses nestjs key names where the two
  share a concept.

## Open

**Wiring** (nestjs 05, 07, 09)

- [ ] **Sockets from constructor hints and `Depends(…)`**: the class each
  parameter is filled by, so an import that is never injected stops counting
  as a dependency.
- [ ] **Ports followed through a binding**: a `Bind(Port, to=Impl)` in a module,
  or `app.dependency_overrides`, the way nestjs follows `useClass`.

**Change** (nestjs 03, 04, 10, 11)

- [ ] **`diff`**: the blast radius of a range, read from git objects.
- [ ] **Logical coupling**: co-change crossed with the import graph.
- [ ] **The workbench** and its change overlay.

**Config**

- [ ] **`module-depth`**, for an app whose bounded context is not the first
  path segment under `root`.
- [ ] **More profiles**, once there is a second Python layout to write one against.

**Testing**

- [ ] **A public pytest helper**, e.g. `metatron.check(".").assert_no_new_violations()`,
  so a project can gate in its own suite without reaching into the container.

## Parked

- [ ] **Type-only imports marked as such.** Edges under `if TYPE_CHECKING:` count
  as dependencies today, as nestjs counts `import type`. Marking them would let
  `circular` tell a runtime cycle from a type-only one.

## Done

- [x] Spec 01: the tool's own layout in the PD patterns, checked by itself.
- [x] Spec 02: config in `pyproject.toml` and the `fastapi` profile.
- [x] Spec 03: the scanner (files, `ast` imports, classification, coverage).
- [x] Spec 04: rules and findings, one violation per broken rule on `notes_api`.
- [x] Spec 05: `baseline` and `check`, and the gate as a test.
