# Project State

## Project Reference

See: .planning/PROJECT.md (updated 2026-04-29)

**Core value:** Kodi users can install and stay up-to-date on sandwichfarm plugins by adding a single repository URL — without manually downloading ZIPs from GitHub
**Current focus:** Phase 1 — Bootstrap

## Current Position

Phase: 1 of 3 (Bootstrap)
Plan: 0 of TBD in current phase
Status: Ready to plan
Last activity: 2026-04-29 — Roadmap created; all 32 v1 requirements mapped across 3 phases

Progress: [░░░░░░░░░░] 0%

## Performance Metrics

**Velocity:**
- Total plans completed: 0
- Average duration: -
- Total execution time: 0 hours

**By Phase:**

| Phase | Plans | Total | Avg/Plan |
|-------|-------|-------|----------|
| - | - | - | - |

**Recent Trend:**
- Last 5 plans: -
- Trend: -

*Updated after each plan completion*

## Accumulated Context

### Decisions

Decisions are logged in PROJECT.md Key Decisions table.
Recent decisions affecting current work:

- [Init]: Checksum strategy — emit both SHA256 (primary, `verify="sha256"`) and MD5 (backward compat); confirmed by Kodi Repository.cpp source
- [Init]: Source-of-truth pattern — release asset fetch via `repository_dispatch`, not git submodules; keeps repos fully decoupled
- [Init]: Phase 1 is manual-first intentionally — GitHub Pages URL must be confirmed live before embedding in `addon.xml`

### Pending Todos

None yet.

### Blockers/Concerns

- [Phase 3 prep]: Before planning Phase 3, read `plugin.audio.subsonic/addon.xml` to confirm: `xbmc.python` version is 3.0.0 (not 2.x), declared addon id is exactly `plugin.audio.subsonic`, `<dir>` wrapper is used. A mismatch in id would require renaming the distribution directory.
- [Phase 2 impl]: GitHub Pages deploy latency (30-90s) means the CI smoke-test step needs a wait/retry loop, not a fixed sleep — needs a concrete implementation decision during Phase 2 planning.

## Session Continuity

Last session: 2026-04-29
Stopped at: Roadmap created; ready to plan Phase 1
Resume file: None
