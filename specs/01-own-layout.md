---
title: The tool's own layout
status: draft
project: metatron-python
location: specs/01-own-layout.md
created: 2026-10-03
tags: [foundation, layout, ddd]
---

# 01 — The tool's own layout

metatron-python is built in the shape it checks. Its code follows the PD
engineering patterns (`patterns/nestjs`), translated into Python. It is also its
own first fixture: `metatron-py check` run on this repository must pass with no
baseline.

## Bounded contexts

```
src/metatron/
├── main.py                 bootstrap: builds the container, parses argv, runs one action
├── app_module.py           every context's module, in one list
├── shared/                 the shared kernel — not a bounded context
│   ├── kernel/             the container, Module and Bind
│   ├── domain/ports/       ports and the projections that cross them
│   └── test_utils/         create_apply_mock and friends
├── config/                 find and load [tool.metatron]; merge the profile
├── scan/                   source tree -> files, imports, findings: the model
└── baseline/               arch.baseline.json: write it, check against it
```

A context talks to another only through a port. The consumer depends on a
`Protocol` in `shared/domain/ports/`. The provider implements it as an
aggregator, and its own module binds the two:

```python
# config/config_module.py
config_module = Module(
    providers=[Bind(ConfigPort, to=ConfigAggregator), *transaction_script_registry, ...],
)
```

No context imports another context's classes. The only cross-context edges land
on `shared/`, which is listed in `infra-modules`.

## Inside a context

```
{context}/
├── {context}_module.py
├── registries/             action_registry.py, transaction_script_registry.py, repository_registry.py
├── application/
│   └── actions/{name}/
│       ├── {name}_action.py         one CLI command
│       ├── {name}_request_dto.py    its arguments, declared and parsed
│       └── {name}_responder.py      its terminal output
├── domain/
│   ├── services/{context}_service.py   (+ *_command.py beside it)
│   ├── aggregators/{context}_aggregator.py
│   └── transaction_scripts/{name}_ts/
│       ├── {name}_transaction_script.py
│       ├── {name}_params.py
│       └── converters, mappers, predicates it alone uses, colocated
└── infrastructure/
    └── repositories/{name}_repository.py
```

## Translations

| NestJS | here | note |
|---|---|---|
| `@Injectable()` + constructor types | constructor type hints | the container reads `__init__` annotations |
| `@Module({ providers })` | `Module(providers=[...])` | `shared/kernel/module.py` |
| `{ provide: TOKEN, useClass }` | `Bind(Port, to=Impl)` | the port's `Protocol` is the token |
| an HTTP Action | a CLI Action | `name`, `help`, `apply(request) -> int` exit code |
| Swagger + DTO | `{name}_request_dto.py` | declares its argparse arguments and parses them |
| Responder | `{name}_responder.py` | returns the text; the action prints it |
| `type X = {...}` projection | `@dataclass(frozen=True)` | immutable, no framework coupling |
| `__specs__/x.spec.ts` | `__specs__/x_spec.py` | pytest collects `*_spec.py` |
| `describe('given: …')` | `class GivenX:` / `class WhenY:` / `def then_z` | pytest's `python_classes` / `python_functions` |
| `createApplyMock<T>()` | `create_apply_mock(T)` | `create_autospec(T, instance=True)` |
| `let target` / `fooMock` in `beforeEach` | fixtures named `target` / `foo_mock` | module-level; each `then_` asks for the ones it asserts on |

The dependency matrix in `dependency-hierarchy.md` applies unchanged:
Actions inject Services; Services inject Transaction Scripts and ports;
Transaction Scripts inject Repositories, Mappers and Converters; nothing injects
its own level.

## Zero runtime dependencies

`ast`, `tomllib`, `argparse`, `hashlib` and `json` are all the tool needs. A
linter that drags a dependency tree into the project it inspects is one more
thing to pin.

## Acceptance

- `uv run pytest` passes; `uv run pytest --cov` reports at least 80%.
- `uv run metatron-py check` on this repository exits 0 against a committed
  baseline that accepts nothing, and `tests/architecture_spec.py` fails on any
  violation at all.
