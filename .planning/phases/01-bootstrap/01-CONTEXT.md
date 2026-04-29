# Phase 1: Bootstrap - Context

**Gathered:** 2026-04-29
**Status:** Ready for planning

<domain>
## Phase Boundary

Phase 1 delivers a Kodi-recognisable, manually-published repository: a real Kodi user can add the source URL, install `repository.sandwichfarm-1.0.0.zip`, and install `plugin.audio.subsonic` from Kodi's addon browser without ever downloading a ZIP from GitHub. Everything is generated on the maintainer's laptop and pushed by hand — no CI in this phase. Phase 1 stops at "Kodi sees the repo and the plugin installs"; auto-update wiring (`repository_dispatch`), CI/validation, and end-user docs are explicit non-goals here.

</domain>

<decisions>
## Implementation Decisions

### Repo Addon Identity
- Addon id is `repository.sandwichfarm` (matches GitHub repo name and PROJECT.md).
- Initial version is `1.0.0` — first public release, semver from day one.
- Provider-name is `sandwichfarm`. Email field left blank or pointing at the GitHub profile.
- Repo addon ships with simple text-based 512×512 `icon.png` (wordmark) and a neutral 1920×1080 `fanart.jpg` placeholder. Real art deferred to a later milestone.

### Hosting Layout
- Hosted on GitHub Pages, project-page form: `https://sandwichfarm.github.io/repository.sandwichfarm/`. Avoids burning the user-page slot.
- Source for Pages: `gh-pages` branch, root `/`. `main` stays source-only; `gh-pages` is fully generated output.
- No custom domain in v1. `*.github.io/...` URL is the canonical URL users copy-paste.
- Repo-addon ZIP lives at the repo root: `…/repository.sandwichfarm-1.0.0.zip`. Single canonical URL — no version subdir indirection.

### First Manual Publish — Plugin Source
- Plugin source for the first publish is fetched by cloning `sandwichfarm/plugin.audio.subsonic` locally and zipping the working tree at HEAD with a one-off invocation of the generator script.
- Initial plugin version published is whatever upstream `addon.xml` declares — currently **3.1.0** (verified). No artificial bump.
- Plugin ZIP and all generated artifacts are committed to the `gh-pages` branch only. `main` never carries binaries.
- A minimal `tools/generate.py` is authored in Phase 1 — locally runnable, Python 3 stdlib only. Phase 2 will wrap this exact script in CI rather than rewrite from scratch.

### Claude's Discretion
- Exact wordmark / fanart aesthetic for the repo addon's placeholder art.
- Internal directory layout under `gh-pages` beyond the canonical `<id>/<id>-<ver>.zip` path (Kodi only cares about that one path; everything else is for human convenience).
- Specific phrasing of the in-`addon.xml` `<summary>` / `<description>` for `repository.sandwichfarm`.
- Exact shape of `plugins.json` (Phase 2 may iterate on the schema; Phase 1 only needs to stub it).

</decisions>

<code_context>
## Existing Code Insights

### Reusable Assets
- The upstream plugin `sandwichfarm/plugin.audio.subsonic` already ships a valid `addon.xml` with id `plugin.audio.subsonic`, version `3.1.0`, `<requires><import addon="xbmc.python" version="3.0.0"/></requires>`, declared `<icon>` and `<fanart>` assets, and the `<extension point="xbmc.python.pluginsource">` block — no upstream changes are required for Phase 1.
- The `drinfernoo/_repo_generator.py` pattern (Python 3 stdlib only — `hashlib`, `zipfile`, `xml.etree.ElementTree`) is the canonical generator shape; adapt rather than reinvent.

### Established Patterns
- Empty repo, no codebase yet — Phase 1 establishes the conventions all later phases follow.
- Branch separation (`main` for source, `gh-pages` for generated output) is a load-bearing convention introduced here.

### Integration Points
- The repo-addon `addon.xml` hard-codes three URLs (`<info>`, `<checksum>`, `<datadir>`) that point at the GitHub Pages base URL. These URLs cannot be changed without users reinstalling the repo addon, so they must be locked in before the first ZIP is published — they are the strictest integration contract in the project.

</code_context>

<specifics>
## Specific Ideas

- Use SHA-256 as the primary checksum (`<checksum verify="sha256">` → `addons.xml.sha256`); also emit `addons.xml.md5` for compatibility. Both files MUST be regenerated atomically in the same generator run (silent-update bug otherwise).
- The wrapper ZIP's top-level directory MUST be exactly `repository.sandwichfarm/` (not flat, not double-nested). CI will assert this in Phase 2; Phase 1 must already produce ZIPs that pass the future check.
- Use the `<dir>` wrapper inside the repo-addon `addon.xml` (required since Kodi Nexus 20.x); flat-format would silently break Kodi 20+.
- Write `addons.xml` as UTF-8 without BOM, `\n` line endings — Kodi parses silently fail on BOM.
- File `changelog-3.1.0.txt` filename version MUST match the published ZIP version exactly.

</specifics>

<deferred>
## Deferred Ideas

- GitHub Actions workflow / `repository_dispatch` cross-repo trigger — Phase 2/3.
- CI validation suite (ZIP nesting check, BOM check, checksum match check, smoke-tests) — Phase 2.
- End-user install README with Android / Fire TV paths and verification step — Phase 3.
- Multi-Kodi-version `<dir minversion>` branching — out of v1 scope (only if a plugin breaks compatibility).
- Real wordmark / fanart artwork beyond the placeholder — out of scope for now.

</deferred>
