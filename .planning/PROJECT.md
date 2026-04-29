# repository.sandwichfarm

## What This Is

A Kodi addon repository that hosts and distributes the user's personal Kodi plugins to end users. End users install a small "repository" addon once, then Kodi can browse, install, and auto-update any plugin published here. The first plugin to ship through it is [plugin.audio.subsonic](https://github.com/sandwichfarm/plugin.audio.subsonic), with capacity for additional plugins over time.

## Core Value

Kodi users can install and stay up-to-date on `sandwichfarm` plugins (starting with `plugin.audio.subsonic`) by adding a single repository URL to Kodi — without manually downloading ZIPs from GitHub.

## Requirements

### Validated

(None yet — ship to validate)

### Active

- [ ] Host an `addons.xml` index that Kodi recognizes as a valid repository
- [ ] Publish a "repository" addon ZIP that users install once to wire Kodi to the index
- [ ] Distribute `plugin.audio.subsonic` through the repository (versioned ZIPs + metadata)
- [ ] Provide a clear install path for end users (one URL, copy-paste-able instructions)
- [ ] Make adding a new plugin to the repo a low-friction, repeatable process
- [ ] Auto-update workflow: pushing a new plugin version updates the index and ZIPs without manual hand-curation

### Out of Scope

- Hosting third-party plugins (someone else's code) — scope is `sandwichfarm`-authored plugins only
- Building the plugins themselves — those live in their own repos (e.g. `plugin.audio.subsonic`); this project only *distributes* them
- A web UI / browseable storefront beyond what Kodi itself renders — Kodi's built-in repo browser is the UX
- Paid / licensed distribution, telemetry, analytics — this is a free, public, static repo
- Signed addon distribution against the official Kodi addon signing infrastructure — out of scope unless required

## Context

- **Kodi addon ecosystem:** Kodi supports user-defined repositories via a small "repository" addon (`repository.<name>`) that points at an HTTP(S) base URL serving `addons.xml` and `addons.xml.md5`. Each addon lives at `<base>/<addon.id>/<addon.id>-<version>.zip` and may have an `icon.png`/`fanart.jpg`/`changelog-<version>.txt` alongside.
- **Existing asset:** [`plugin.audio.subsonic`](https://github.com/sandwichfarm/plugin.audio.subsonic) is the seed plugin. Its `addon.xml` already declares its id, version, and dependencies — the repository must surface these without modification.
- **Hosting realities:** Static hosting (GitHub Pages, GitHub raw, Cloudflare Pages, S3, etc.) is the standard pattern — no server runtime required. Choice of host affects HTTPS, custom domain, and update latency.
- **User type:** End-user installation flow on Kodi is finicky (custom sources, file manager add-source, then "install from zip"). Documentation matters at least as much as the artifacts.
- **Author workflow:** The author intends to add more plugins over time; the repo's build/publish process must scale beyond a single hand-edited `addons.xml`.

## Constraints

- **Compatibility**: Must work with current and recent Kodi versions (Nexus / Omega / Piers — at minimum the version `plugin.audio.subsonic` already targets in its `addon.xml`).
- **Tech stack**: Whatever produces a valid `addons.xml` + ZIP layout; must run on free-tier static hosting and be reproducible in CI.
- **Cost**: Free or near-free to host indefinitely (GitHub Pages / Cloudflare Pages tier is fine).
- **Security**: Distribute unsigned ZIPs over HTTPS; users will need to enable "unknown sources" in Kodi (standard for non-official repos), and we should not require it to be off.
- **Maintenance**: One-person maintenance — automation must minimise manual steps when releasing.

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Greenfield, no existing repo files | Directory is empty at init | — Pending |
| Repository scope = sandwichfarm-authored plugins only | Avoids licensing / trust questions for third-party code | — Pending |
| Publishing automation over manual `addons.xml` edits | Single maintainer; need to scale to N plugins | — Pending |

## Evolution

This document evolves at phase transitions and milestone boundaries.

**After each phase transition** (via `/gsd:transition`):
1. Requirements invalidated? → Move to Out of Scope with reason
2. Requirements validated? → Move to Validated with phase reference
3. New requirements emerged? → Add to Active
4. Decisions to log? → Add to Key Decisions
5. "What This Is" still accurate? → Update if drifted

**After each milestone** (via `/gsd:complete-milestone`):
1. Full review of all sections
2. Core Value check — still the right priority?
3. Audit Out of Scope — reasons still valid?
4. Update Context with current state

---
*Last updated: 2026-04-29 after initialization*
