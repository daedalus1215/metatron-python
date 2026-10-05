---
title: metatron-python specs — index and sequencing
status: implemented
project: metatron-python
location: specs/README.md
created: 2026-10-03
tags: [index, roadmap, python, fastapi, ddd]
---

# Specs

A Python port of [`metatron-nestjs`](../../metatron-nestjs). Point it at a
FastAPI backend and get a measured model of its architecture, checked against
the layer rules in the PD engineering patterns. Numbered by dependency, not by
importance.

| # | spec | kind | depends on |
|---|------|------|-----------|
| 01 | [The tool's own layout](01-own-layout.md) | foundation | — |
| 02 | [Config and the `fastapi` profile](02-config-and-profile.md) | foundation | 01 |
| 03 | [Scanner: files, imports, classification](03-scanner.md) | foundation | 02 |
| 04 | [Rules and findings](04-rules-and-findings.md) | analysis | 03 |
| 05 | [Baseline and `check`](05-baseline-and-check.md) | gating | 04 |

Later work, before it is a spec, is tracked in [`CHECKLIST.md`](../CHECKLIST.md).

## What carries over, and what does not

The rules carry over: a declared `flow` whose skipped stations are violations,
`forbidden` directions, no same-level injection, cross-context imports that may
land only on a gateway, and a baseline keyed by `rule|from|to` so `check` names
the offender and catches a swap.

The mechanics do not. The patterns wiki says the Python set is to be
"translations of intent, not literal ports", and the same applies here:

| metatron-nestjs | metatron-python | why |
|---|---|---|
| a brace-matching walker over TypeScript | the stdlib `ast` module | Python ships its own parser; there is nothing to guess |
| `arch.config.js` | `[tool.metatron]` in `pyproject.toml` | every Python backend already has the file |
| `create-note.action.ts` | `create_note_action.py` | a dot in a module name cannot be imported |
| `@Inject(TOKEN)` in a module file | a binding in a `*_module.py` | Python has no decorator DI of its own |
| `require`/`import` path specs | dotted module names and relative imports | resolved against the source roots |

## The thread running through all of them

The failure mode of an architecture tool is not crashing; it is drawing a
confident picture of something it did not understand. Each spec names its own
refusal:

- **02** prints coverage first, so a config that classifies nothing cannot pass
  for a clean architecture.
- **03** reports a file that does not parse, and an import that names no file,
  as diagnostics rather than dropping them.
- **04** keeps aggregate observations (`gate = false`) out of the gate.
- **05** never retires a violation on its own: a scan that failed to read a file
  would otherwise quietly forgive a real debt.
