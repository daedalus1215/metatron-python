---
title: Baseline and check
status: implemented
implemented: 2026-10-03
project: metatron-python
location: specs/05-baseline-and-check.md
created: 2026-10-03
tags: [gating, baseline, ci]
---

# 05 — Baseline and `check`

metatron-nestjs's ratchet, ported rather than redesigned: record today's
violations as accepted, then fail when one appears that is not on the list.

```bash
metatron-py baseline            # writes arch.baseline.json beside the config
metatron-py baseline --update   # rewrites it, keeping hand-written notes
metatron-py check               # 0 clean, 1 new violations, 2 tool or config error
```

## The file

`arch.baseline.json` sits beside the config file, not in `out-dir`: output is
generated and usually ignored by git, and a ratchet nobody commits cannot hold
a line. The name and the format are metatron-nestjs's, so a team that runs both
reads one kind of file.

```json
{
  "version": 1,
  "project": "notes",
  "violations": {
    "a3f19c4b2e01": {
      "rule": "action>repository",
      "from": "notes/application/actions/create_note/create_note_action.py",
      "to": "notes/infrastructure/repositories/note_repository.py",
      "note": "legacy, pre-dates the service"
    }
  }
}
```

One difference: there is no `generatedAt`. Re-recording an unchanged tree
writes the same bytes, so the file only shows up in a diff when the debt
changes.

## check

```
metatron check · notes

  new violations        1
    action>repository     notes/application/actions/create_note/create_note_action.py
                          -> notes/infrastructure/repositories/note_repository.py

  fixed since baseline  2

  known, unchanged      42

FAIL — 1 new violation. Fix it, or run `metatron-py baseline --update` to accept it.
```

| flag | effect |
|---|---|
| `--rule <id>` | gate on this rule only (repeatable); the rest is reported as advisory |
| `--allow-new <n>` | tolerate up to n new violations, to ratchet down over time |
| `--no-fixed` | do not list violations fixed since the baseline |
| `--json` | the comparison as JSON, for tooling |

## Refusals

- **A fixed violation is reported, never removed.** A scan that fails to parse a
  file would otherwise quietly retire a real debt, which would later come back
  as "new" with no history.
- **`baseline` will not overwrite.** An existing file needs `--update`, so the
  hand-written notes, the only record of why each violation is tolerated, are
  never lost by accident. A note whose violation is gone is dropped, and the
  output says so.
- **No baseline is an error (exit 2), not a pass.**
- **Aggregate findings never gate.** `dag` is printed by `baseline` as "not
  gated", so a rule cannot sit outside the gate unnoticed.

## The gate is a test

As in metatron-rust, the check can run inside the project's own test suite.
metatron-python's own `tests/architecture_spec.py` builds this repository's
model through `ModelPort` and fails on any violation at all; its committed
`arch.baseline.json` accepts nothing.

## Acceptance

- `baseline` then `check` on an unchanged tree passes.
- A new violation fails with exit 1 and names the file pair. A swap (one fixed,
  one added) still fails.
- `--update` keeps a note whose violation remains and reports one that it drops.
- `--rule` and `--allow-new` behave as above. `--json` parses.
