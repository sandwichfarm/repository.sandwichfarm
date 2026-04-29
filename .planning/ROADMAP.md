# Roadmap: repository.sandwichfarm

## Overview

Starting from an empty directory, three phases deliver the complete stated value: a Kodi user adds one URL, installs one ZIP, and receives automatic updates for all sandwichfarm plugins forever. Phase 1 proves the Kodi repository protocol works by doing everything manually — because the GitHub Pages URL must be live and confirmed before it can be embedded in `addon.xml`. Phase 2 converts the manual process into a validated CI/CD pipeline so the author never hand-edits the index again. Phase 3 wires the cross-repo trigger and writes the end-user documentation that completes the core value proposition.

## Phases

**Phase Numbering:**
- Integer phases (1, 2, 3): Planned milestone work
- Decimal phases (2.1, 2.2): Urgent insertions (marked with INSERTED)

Decimal phases appear between their surrounding integers in numeric order.

- [ ] **Phase 1: Bootstrap** - Author and publish the repo skeleton manually; prove Kodi recognises the repository
- [ ] **Phase 2: Automation** - CI/CD pipeline + validation suite; author can release without touching this repo
- [ ] **Phase 3: End-to-End** - Cross-repo trigger, auto-update verification, and end-user documentation

## Phase Details

### Phase 1: Bootstrap
**Goal**: A Kodi user can add the repository and install `plugin.audio.subsonic` — entirely from manually-generated artifacts
**Depends on**: Nothing (first phase)
**Requirements**: REPO-01, REPO-02, REPO-03, REPO-04, IDX-01, IDX-02, IDX-03, IDX-04, IDX-05, IDX-06, HOST-01, HOST-02, HOST-03, PLUG-01, PLUG-02
**Success Criteria** (what must be TRUE):
  1. GitHub Pages is live at a stable HTTPS base URL and all three repo-addon endpoint URLs (`<info>`, `<checksum>`, `<datadir>`) return HTTP 200 to a fresh client
  2. A Kodi user can install `repository.sandwichfarm-1.0.0.zip` via "install from zip" and see the repository listed in Kodi's addon browser
  3. A Kodi user who has the repo installed can browse to `plugin.audio.subsonic` in the addon browser and install it without downloading a ZIP from GitHub
  4. The published `addons.xml` is valid UTF-8 without BOM, uses `\n` line endings, and includes a matching `addons.xml.sha256` and `addons.xml.md5` sidecar
  5. Each plugin directory contains the correctly-sized `icon.png`, `fanart.jpg`, and a `changelog-X.Y.Z.txt` whose version matches the published ZIP exactly
**Plans**: 3 plans
Plans:
- [ ] 01-01-PLAN.md — Repo skeleton on main: hand-author addon.xml with locked URLs, generate placeholder artwork, write plugins.json and .gitignore
- [ ] 01-02-PLAN.md — Generator + plugin packaging: author tools/generate.py, clone plugin source to vendor/, run generator locally, verify all staging artifacts
- [ ] 01-03-PLAN.md — Publish to gh-pages + smoke tests + Kodi human verification + write SETUP.md

### Phase 2: Automation
**Goal**: The author can release a new plugin version by tagging in the plugin repo; CI produces, validates, and deploys all artifacts without manual steps
**Depends on**: Phase 1
**Requirements**: PUB-01, PUB-02, PUB-03, PUB-04, PUB-05, PUB-06, VAL-01, VAL-02, VAL-03, VAL-04, VAL-05
**Success Criteria** (what must be TRUE):
  1. Pushing to `main` (or triggering `workflow_dispatch`) causes GitHub Actions to fetch plugin release assets, regenerate `addons.xml` plus both checksum sidecars, and commit the result to `gh-pages` in a single automated commit
  2. CI explicitly asserts every plugin ZIP has exactly one top-level directory matching its addon id, `addons.xml` is BOM-free with `\n` endings, and both checksum files match the freshly written index
  3. CI smoke-tests all three repo-addon endpoint URLs for HTTP 200 after deploy; a failing URL blocks the workflow and the old artifacts remain live
  4. Adding a second plugin to the repository requires only a one-line edit to `plugins.json` — no other file changes needed
**Plans**: TBD

### Phase 3: End-to-End
**Goal**: The complete stated core value is live — a Kodi user adds one URL and receives automatic updates; the release cycle from tag to Kodi update is fully automated and documented
**Depends on**: Phase 2
**Requirements**: PLUG-03, PLUG-04, DOCS-01, DOCS-02, DOCS-03, DOCS-04
**Success Criteria** (what must be TRUE):
  1. A tag pushed to `plugin.audio.subsonic` triggers a `repository_dispatch` event that causes `repository.sandwichfarm`'s pipeline to run automatically — no manual action in this repo required
  2. A Kodi client that already has `plugin.audio.subsonic` installed receives the updated version within the next polling cycle (default ~24 hours) after a new tag is pushed upstream
  3. The `README.md` contains a single copy-pasteable HTTPS URL and step-by-step install instructions that cover enabling Unknown Sources, adding the source via File Manager, installing the repo ZIP, and installing plugins from the repo
  4. Install instructions explicitly cover Android/Fire TV path differences and include a verification step so users can confirm the install worked before reporting issues
**Plans**: TBD

## Progress

**Execution Order:**
Phases execute in numeric order: 1 → 2 → 3

| Phase | Plans Complete | Status | Completed |
|-------|----------------|--------|-----------|
| 1. Bootstrap | 0/3 | Not started | - |
| 2. Automation | 0/TBD | Not started | - |
| 3. End-to-End | 0/TBD | Not started | - |
