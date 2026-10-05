---
title: Config and the fastapi profile
status: draft
project: metatron-python
location: specs/02-config-and-profile.md
created: 2026-10-03
tags: [foundation, config]
---

# 02 — Config and the `fastapi` profile

## Where it lives

`[tool.metatron]` in the `pyproject.toml` beside the code, or a standalone
`metatron.toml` whose whole file is the table. Found by walking up from the
path given on the command line. The first directory holding either one with a
metatron table wins. A `pyproject.toml` with no `[tool.metatron]` is passed over.

```toml
[tool.metatron]
root = "app"
```

That is the whole config for a project that follows the patterns.

## Keys

Kebab-case, as `pyproject.toml` tools write them.

| key | meaning |
|---|---|
| `extends` | base profile. `fastapi`, the default, is the only one. |
| `root` | scanned directory, relative to the config file |
| `name` | shown in output. Defaults to the folder, climbing past `backend/`, `src/` and friends |
| `out-dir` | where `model.json` lands. Default `.metatron` |
| `source-roots` | where absolute imports resolve from. Default: the directory above the outermost package that holds `root` |
| `ignore` | regexes; a path matching any one is not scanned |
| `tiers` | the architectural layers, in the order a request travels |
| `patterns` | file → pattern, first match wins. Replaces the profile's list |
| `add-patterns` | prepended to the profile's patterns, to refine without restating |
| `fallback` | the pattern an unmatched file gets |
| `flow` | the intended call path; skipping a station is a violation |
| `flow-aliases` | other patterns that count as the same station |
| `allowed-skips` | skip rules the architecture permits (`service>repository`) |
| `forbidden` | pattern pairs that must never import that direction |
| `layers` | directory pairs that must never import that direction |
| `no-same-level` | patterns that must not import their own kind |
| `infra-modules` | top-level packages that are plumbing, not bounded contexts |
| `cross-domain-gateways` | the only patterns a cross-context import may land on |
| `naming` | file-name rules; every match is a violation |

Any other key is an error that lists the known ones. A camel-cased
`addPatterns` copied from an `arch.config.js` would otherwise be ignored, and
the scan would run on defaults while looking configured.

## The profile

`config/infrastructure/profiles/fastapi.toml` holds the defaults. It is the
dependency matrix of `dependency-hierarchy.md` written down as data:

- **flow** `action → service → transaction-script → repository`, with routers,
  webhooks and listeners as actions, and remote callers and dispatchers as
  repositories.
- **allowed-skips** `service>repository`: the matrix lets a Domain Service
  inject a Repository for a simple lookup.
- **forbidden**: every "cannot inject" cell of the matrix that points up or
  sideways across levels, e.g. a converter importing a repository.
- **layers**: `domain-no-application` and `infrastructure-no-application`, the
  two directions the matrix forbids between folders.
- **no-same-level**: every pattern the matrix lists under rule 1.
- **naming**: `domain-dto`, since the domain never says "Dto".

## Refusals

- A pattern that names a tier not in `tiers`, a regex that does not compile, and
  a rule that names a pattern not in `patterns` are all errors. A rule that
  names nothing never fires, and a gate that cannot fire passes everything.
- A missing `root` is an error that says the path is relative to the config.
- A `name` that does not loosely match the folder is a warning: the config was
  probably copied from another project.

## Acceptance

- `[tool.metatron]` with only `root` loads the full profile.
- `add-patterns` lands before the profile's patterns; `patterns` replaces them.
- `addPatterns`, an unknown tier, a bad regex and a flow station with no
  pattern each fail with a message that names the problem.
