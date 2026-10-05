---
title: Rules and findings
status: implemented
implemented: 2026-10-03
project: metatron-python
location: specs/04-rules-and-findings.md
created: 2026-10-03
tags: [analysis, rules, findings]
---

# 04 — Rules and findings

Turns a `SourceTreeProjection` and the config into findings, and the gating
ones into violations. Each finding has an `id`, a `tone` (`warn`, `good`,
`note`), a title, items to print, and `instances`: the `(from, to)` pairs a
baseline can fingerprint.

## The findings

| id | from | gates |
|---|---|---|
| `a>b` | `flow`: an import from station `a` to station `b`, two or more stations on. One station skipped is `warn`, two or more is `crit` | yes |
| `no-upward` | every `forbidden` pair | yes |
| `domain-no-application`, … | each `layers` rule: a file under a `from` directory importing one under a `to` directory | yes |
| `no-same-level` | an import between two files of one `no-same-level` pattern | yes |
| `cross-domain` | an import between bounded contexts landing on a pattern outside `cross-domain-gateways` | yes |
| `circular` | a strongly connected component of the file graph | yes |
| `naming-{id}` | each file a `naming` rule matches | yes |
| `dag` | cycles between bounded contexts | no (`gate = false`) |
| `absent-patterns` | configured patterns no file has | no (`note`) |

`cross-domain`, `no-same-level`, `no-upward`, `circular` and every layer rule
also report when they hold (`good`), so `scan` can say what was checked and
upheld rather than only what failed.

What the cross-context rules set aside: files at the top of the root
(`(root)`), the `infra-modules`, and imports to or from `spec`, `test-util`,
`migration`, `bootstrap` and `module` files. The wiring and the tests are
supposed to see everything.

## Where this differs from metatron-nestjs

- **Skip rules use the flow aliases.** metatron-nestjs derives `skipRules`
  from the stations, aliases included, but reports hits only for the exact pair
  `pairs(r.from, r.to)`, so a `controller` reaching a `repository` is drawn as a
  skip and never reported. Here a router reaching a repository is an
  `action>repository` hit.
- **`allowed-skips` removes a derived rule.** The dependency matrix lets a
  Domain Service inject a Repository, and a rule the architecture permits is
  noise.
- **A helper split is one directory, not one folder.** metatron-nestjs
  forgives a same-pattern import inside one three-segment folder. Under the PD
  layout every transaction script sits in `domain/transaction_scripts/`, so one
  transaction script importing another was always forgiven. Here only files in
  the same directory are a helper split.

## Violations

Each instance of a gating `warn` finding is one violation, fingerprinted
`sha1(rule|from|to)[:12]`. That is the same scheme as metatron-nestjs, so
`check` can name the offender and catch a swap. The same edge breaking two
rules is two violations; the same fingerprint twice is one.

## Acceptance

- A fixture that breaks each rule once produces exactly one violation per rule.
- A router importing a repository is `action>repository` (`crit`).
- A service importing a repository is nothing.
- Two transaction scripts in sibling `*_ts/` directories that import each other
  are `no-same-level` and `circular`.
