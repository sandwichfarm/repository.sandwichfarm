# Requirements: repository.sandwichfarm

**Defined:** 2026-04-29
**Core Value:** Kodi users can install and stay up-to-date on `sandwichfarm` plugins (starting with `plugin.audio.subsonic`) by adding a single repository URL — without manually downloading ZIPs from GitHub.

## v1 Requirements

### Repository Addon (REPO)

- [ ] **REPO-01**: A wrapper addon `repository.sandwichfarm` exists with a hand-authored `addon.xml` declaring `extension point="xbmc.addon.repository"` and a `<dir>` wrapper element (required since Kodi Nexus 20.x)
- [ ] **REPO-02**: The repo addon's `<dir>` block declares three URLs: `<info>` (addons.xml), `<checksum verify="sha256">` (addons.xml.sha256), and `<datadir zip="true">` (base path for plugin ZIPs)
- [ ] **REPO-03**: The repo addon is packaged as `repository.sandwichfarm-X.Y.Z.zip` whose top-level directory is exactly `repository.sandwichfarm/`
- [ ] **REPO-04**: The repo addon ZIP is reachable at a stable, copy-paste-able HTTPS URL that end users can install via "install from zip"

### Index (IDX)

- [ ] **IDX-01**: An `addons.xml` index is published at the repo's base URL, wrapping each addon's `addon.xml` content in a single `<addons>` root, written as UTF-8 (no BOM) with `\n` line endings
- [ ] **IDX-02**: An `addons.xml.sha256` sidecar is published alongside `addons.xml` and is regenerated atomically with it (always written in the same generator run, never independently)
- [ ] **IDX-03**: An `addons.xml.md5` sidecar is also published for backward compatibility with older clients
- [ ] **IDX-04**: Each plugin ZIP is published at the canonical Kodi path `<base>/<addon.id>/<addon.id>-<version>.zip`, with the version in the filename matching the `addon.xml` version exactly
- [ ] **IDX-05**: Each plugin directory contains `icon.png` (512×512) and `fanart.jpg` (1920×1080) so the addon renders correctly in Kodi's browser
- [ ] **IDX-06**: Each plugin release has a `changelog-X.Y.Z.txt` whose filename version matches the ZIP version exactly

### Hosting (HOST)

- [ ] **HOST-01**: Static files are served over HTTPS from a free-tier host (GitHub Pages) with a stable base URL
- [ ] **HOST-02**: Generated artifacts live on a separate branch (`gh-pages`) so binary ZIPs do not pollute source-history of `main`
- [ ] **HOST-03**: The base URL, the `addons.xml` URL, the `addons.xml.sha256` URL, and the `<datadir>` URL all return HTTP 200 to a fresh client (no auth, no redirects to login)

### Publishing Pipeline (PUB)

- [ ] **PUB-01**: A `tools/generate.py` script (Python 3 stdlib only — `hashlib`, `zipfile`, `xml.etree.ElementTree`) reads a plugin manifest and produces `addons.xml`, `addons.xml.sha256`, `addons.xml.md5`, and per-plugin ZIPs in the canonical layout
- [ ] **PUB-02**: A `plugins.json` manifest declares each addon to publish (addon id + upstream GitHub repo); adding a new plugin is a one-line edit
- [ ] **PUB-03**: A GitHub Actions workflow rebuilds the index on `push` to `main`, on `workflow_dispatch`, and on `repository_dispatch` events from plugin repos
- [ ] **PUB-04**: The workflow fetches each plugin's release ZIP asset from its upstream GitHub repo (release-asset pattern, not git submodules) and repackages it into the canonical directory layout
- [ ] **PUB-05**: The workflow commits the regenerated `addons.xml`, both checksum sidecars, and any updated ZIPs back to `gh-pages` in a single commit (using `stefanzweifel/git-auto-commit-action@v5` or equivalent)
- [ ] **PUB-06**: The author can release a new plugin version by tagging in the plugin repo; no manual edits are required in `repository.sandwichfarm`

### Plugin Onboarding (PLUG)

- [ ] **PLUG-01**: `plugin.audio.subsonic` is listed in `plugins.json` and successfully published through the pipeline
- [ ] **PLUG-02**: A Kodi user who installs the repo addon can browse to `plugin.audio.subsonic` in Kodi's addon browser and install it without ever downloading a ZIP from GitHub
- [ ] **PLUG-03**: When a new version of `plugin.audio.subsonic` is released upstream, Kodi clients receive the update automatically within the next polling cycle (default ~24 hours)
- [ ] **PLUG-04**: The plugin repo's release workflow triggers a `repository_dispatch` event into `repository.sandwichfarm` so a tag in the plugin repo is sufficient to publish a new version

### End-User Documentation (DOCS)

- [ ] **DOCS-01**: A `README.md` (or top-level `INSTALL.md`) shows the one HTTPS URL users add as a Kodi source, in copy-pastable form
- [ ] **DOCS-02**: Step-by-step install instructions cover: enabling Unknown Sources, adding the source URL via File Manager, installing the repo ZIP, then installing plugins from the repository
- [ ] **DOCS-03**: Install instructions explicitly call out the difference between desktop Kodi and Android/Fire TV install paths where relevant
- [ ] **DOCS-04**: An "is it working?" verification step (e.g., screenshot or expected outcome) is provided so users can confirm install before reporting issues

### CI Validation (VAL)

- [ ] **VAL-01**: CI asserts every plugin ZIP has exactly one top-level directory matching its addon id (no flat layout, no double-nesting)
- [ ] **VAL-02**: CI asserts `addons.xml` is valid UTF-8 without BOM and uses `\n` line endings
- [ ] **VAL-03**: CI asserts `addons.xml.sha256` and `addons.xml.md5` exist after each publish and that their digests match the freshly written `addons.xml`
- [ ] **VAL-04**: CI asserts each version referenced in `addons.xml` has a corresponding ZIP at the canonical path (no missing artifacts)
- [ ] **VAL-05**: After deploy, CI smoke-tests that all three repo-addon endpoint URLs (`<info>`, `<checksum>`, `<datadir>`) return HTTP 200 to a fresh client; failure blocks the workflow

## v2 Requirements

Deferred. Tracked but not in current roadmap.

### Multi-Plugin Scale (SCALE)

- **SCALE-01**: Onboard a second plugin through the same pipeline, exercising the multi-addon path of `plugins.json` end-to-end
- **SCALE-02**: Per-Kodi-version `<dir minversion=…>` / `<dir maxversion=…>` branching, applied only if a plugin breaks compatibility between Kodi major versions

### Pre-release Channel (BETA)

- **BETA-01**: Optional pre-release / beta directory and `<dir>` block so users can opt into in-development plugin versions

### Performance (PERF)

- **PERF-01**: Pre-compressed `addons.xml.gz` published alongside `addons.xml` if a future Kodi major version requires it (Piers / 22+)

## Out of Scope

| Feature | Reason |
|---------|--------|
| Hosting third-party / non-`sandwichfarm` plugins | Trust + licensing scope; keeps the repo small and personal |
| Building the plugins themselves | Plugin source lives in its own repos (e.g., `plugin.audio.subsonic`); this project only *distributes* them |
| Web UI / browseable storefront beyond Kodi's built-in browser | Kodi's repo browser is the UX; redundant work otherwise |
| Telemetry, analytics, or login | Free, public, static repo — no server-side runtime |
| Signing against the official Kodi addon signing infrastructure | Not required for personal/unofficial repos |
| Custom HTTP cache-control headers (`X-Kodi-Recheck-After`) | GitHub Pages does not support custom response headers; Kodi's 24-hour default is acceptable |
| Bundling third-party paid content | Anti-feature — would draw the repo onto anti-piracy filter lists |

## Traceability

| Requirement | Phase | Status |
|-------------|-------|--------|
| REPO-01 | Phase 1 | Pending |
| REPO-02 | Phase 1 | Pending |
| REPO-03 | Phase 1 | Pending |
| REPO-04 | Phase 1 | Pending |
| IDX-01 | Phase 1 | Pending |
| IDX-02 | Phase 1 | Pending |
| IDX-03 | Phase 1 | Pending |
| IDX-04 | Phase 1 | Pending |
| IDX-05 | Phase 1 | Pending |
| IDX-06 | Phase 1 | Pending |
| HOST-01 | Phase 1 | Pending |
| HOST-02 | Phase 1 | Pending |
| HOST-03 | Phase 1 | Pending |
| PUB-01 | Phase 2 | Pending |
| PUB-02 | Phase 2 | Pending |
| PUB-03 | Phase 2 | Pending |
| PUB-04 | Phase 2 | Pending |
| PUB-05 | Phase 2 | Pending |
| PUB-06 | Phase 2 | Pending |
| PLUG-01 | Phase 1 | Pending |
| PLUG-02 | Phase 1 | Pending |
| PLUG-03 | Phase 3 | Pending |
| PLUG-04 | Phase 3 | Pending |
| DOCS-01 | Phase 3 | Pending |
| DOCS-02 | Phase 3 | Pending |
| DOCS-03 | Phase 3 | Pending |
| DOCS-04 | Phase 3 | Pending |
| VAL-01 | Phase 2 | Pending |
| VAL-02 | Phase 2 | Pending |
| VAL-03 | Phase 2 | Pending |
| VAL-04 | Phase 2 | Pending |
| VAL-05 | Phase 2 | Pending |

**Coverage:**
- v1 requirements: 32 total
- Mapped to phases: 32
- Unmapped: 0

---
*Requirements defined: 2026-04-29*
*Last updated: 2026-04-29 after roadmap creation — all 32 requirements mapped*
