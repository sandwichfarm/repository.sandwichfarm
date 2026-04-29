# Project Research Summary

**Project:** repository.sandwichfarm
**Domain:** Kodi addon repository — static distribution endpoint
**Researched:** 2026-04-29
**Confidence:** MEDIUM-HIGH

## Executive Summary

A Kodi addon repository is a static file server that speaks a small, well-documented protocol: an `addons.xml` index, a checksum sidecar, and versioned ZIP archives at canonical paths. There is no runtime, no database, and no server-side logic — GitHub Pages is the right host and the community pattern is universally consistent. The "repository" addon itself is a tiny hand-authored ZIP users install once to wire their Kodi instance to the index; after that, Kodi polls for updates automatically every ~24 hours. The entire system is well understood and reproducible from existing reference implementations.

The recommended approach is: author the repo-addon `addon.xml` by hand (once), write a `generate.py` script adapted from drinfernoo's `_repo_generator.py`, maintain a `plugins.json` manifest of which upstream GitHub repos to include, and run the pipeline on a `gh-pages` branch via GitHub Actions. Plugin source stays authoritative in its own repo (`plugin.audio.subsonic`); the publisher fetches release ZIP assets on each new tag via `repository_dispatch` rather than embedding the source as a git submodule. This keeps the two repos fully decoupled and eliminates submodule pointer bookkeeping.

The dominant risk is silent failure: Kodi gives no user-visible error when `addons.xml.md5` is stale, the ZIP has wrong directory nesting, or a version number was not bumped — it simply does nothing. The mitigation is a CI validation suite that runs after every generation: check ZIP structure, verify no BOM in `addons.xml`, confirm HTTP 200 on all three repo-addon endpoint URLs, and assert both checksum files were regenerated atomically with the index. Building this validation into Phase 2 (automation) rather than Phase 1 (manual bootstrap) is intentional — Phase 1 proves Kodi recognises the repo before any automation is layered on.

---

## Conflict Resolutions

Two conflicts were identified across the research files. Both are resolved here; downstream documents should follow these decisions.

### Checksum Format: MD5 vs SHA-256

**Conflict:**
- STACK.md: "MD5 is community standard; SHA256 is a minor enhancement worth adding."
- FEATURES.md: SHA256 is preferred; Kodi source (Repository.cpp) logs MD5 as broken.
- ARCHITECTURE.md: poll sequence diagram uses `addons.xml.md5`.
- PITFALLS.md: Omega may require SHA-256 + `addons.xml.gz`.

**Resolution: Emit both. Configure the repo addon with `<checksum verify="sha256">` pointing at `addons.xml.sha256`; also produce `addons.xml.md5` for backward compatibility.**

One-sentence rationale: Kodi's own source code (Repository.cpp) logs MD5 as deprecated and FEATURES research confirms SHA-256 is the correct modern value for the `verify` attribute, so SHA-256 is the primary checksum — but generating `addons.xml.md5` alongside costs nothing and covers any edge-case older clients.

Practical implication for `generate.py`: write both files after every index regeneration. The `<checksum>` URL in `repository.sandwichfarm/addon.xml` must point at `addons.xml.sha256` with `verify="sha256"`.

### Source-of-Truth Pattern: Submodule vs Release Asset Fetch

**Conflict:**
- STACK.md: leans toward git submodule.
- ARCHITECTURE.md: recommends release asset fetch via `repository_dispatch`.

**Resolution: Primary — release asset fetch via `repository_dispatch`. Alternative — git submodule.**

Rationale: The stated project constraint is that plugins "live in their own repos; this project only distributes them." A submodule coupling contradicts that boundary and adds pointer-update bookkeeping on every plugin release. Release asset fetch matches the architecture trigger diagram, requires no extra commit to the publisher repo on each plugin release, and scales cleanly to N plugins via `plugins.json`. The submodule approach is a valid fallback only if offline builds or GitHub API unavailability become a requirement.

---

## Key Findings

### Recommended Stack

GitHub Pages + Python stdlib + GitHub Actions is the unanimous community pattern for personal Kodi repos. No paid services, no external dependencies beyond Python's standard library. The generator script is a single file (`tools/generate.py`) derived from drinfernoo's `_repo_generator.py`, with SHA-256 support added. The only GitHub Action needed beyond checkout/setup-python is `stefanzweifel/git-auto-commit-action` for committing generated artifacts back to the `gh-pages` branch.

**Core technologies:**
- **GitHub Pages (free tier):** HTTPS static hosting with Fastly CDN — the de-facto host for every personal Kodi repo; zero cost, native Actions integration
- **Python 3.x (stdlib only):** Generator runtime; `hashlib`, `zipfile`, `xml.etree.ElementTree` — no pip installs needed in CI
- **GitHub Actions:** CI/CD triggered on `push`, `repository_dispatch` (from plugin repo on release), and `workflow_dispatch` (manual)
- **`stefanzweifel/git-auto-commit-action`:** Commits regenerated `addons.xml`, `addons.xml.md5`, `addons.xml.sha256` back to `gh-pages` without hand-rolling git config
- **`kodi-addon-checker` (0.0.36, June 2025):** Validates individual plugin `addon.xml` before publishing; runs in plugin CI, not repo CI

**Version targets:** Kodi 21 Omega (current stable, Python 3.12) is primary; Nexus (20.x) backward-compatible with identical format. Piers (22.x) is Alpha 3 — do not target yet.

### Expected Features

**Must have (Kodi protocol-required):**
- `addons.xml` at repo base URL — Kodi cannot discover addons without it
- `addons.xml.sha256` (primary) + `addons.xml.md5` (compatibility) at repo base URL
- Versioned ZIP at `<base>/<addon.id>/<addon.id>-<version>.zip` — exact path Kodi constructs
- `icon.png` (512x512) and `fanart.jpg` (1920x1080) per addon
- `changelog-X.Y.Z.txt` per addon (filename version must match ZIP version exactly)
- `repository.sandwichfarm/addon.xml` with `xbmc.addon.repository` extension using `<dir>` wrapper (required since Nexus 20.x)
- `repository.sandwichfarm-X.Y.Z.zip` — the wrapper ZIP users install once
- End-user install documentation covering Unknown Sources + File Manager + install-from-zip with Android/FireTV path differences explicitly called out

**Should have (author workflow automation):**
- Automated `addons.xml` rebuild on tag push via GitHub Actions
- `kodi-addon-checker` CI gate in plugin repos before publishing
- `plugins.json` manifest so adding a second plugin requires only a one-line edit
- `repository_dispatch` cross-repo trigger from plugin release workflow
- CI smoke tests: ZIP structure assertion, no-BOM check, HTTP 200 on all three repo-addon endpoint URLs

**Defer to v2+:**
- Multi-Kodi-version directory branches (`minversion`/`maxversion`) — only needed if a plugin breaks between Nexus and Omega
- Pre-release / beta channel
- Pre-compressed `addons.xml.gz` — GitHub Pages negotiates gzip automatically
- `X-Kodi-Recheck-After` header — GitHub Pages does not support custom headers; 24-hour default is fine

### Architecture Approach

The system has three layers: Source (external plugin repos on GitHub), Publisher (this repo's GitHub Actions pipeline), and Host (GitHub Pages `gh-pages` branch). The publisher fetches release ZIP assets from the plugin repo on each `repository_dispatch` event, repackages them into the canonical directory layout, regenerates `addons.xml` plus both checksum sidecars, and force-pushes to `gh-pages`. Source and generated output are kept on separate branches (`main` vs `gh-pages`) so binary ZIPs never pollute source history.

**Major components:**
1. **Repo Addon (`repository.sandwichfarm/addon.xml`)** — hand-authored once; declares the three endpoint URLs (`<info>`, `<checksum verify="sha256">`, `<datadir>`); uses `<dir>` wrapper; changing these URLs requires rebuilding the ZIP and users reinstalling it
2. **Publisher pipeline (`tools/generate.py` + `.github/workflows/publish.yml`)** — fetches plugin release assets from GitHub API, assembles ZIP layout, writes `addons.xml` + both checksum files; reads `plugins.json` manifest for the plugin list
3. **Plugin registry (`plugins.json`)** — single machine-readable file mapping addon IDs to upstream repos; one-line edit to onboard a new plugin
4. **Host (GitHub Pages `gh-pages` branch)** — entirely generated output, never hand-edited; serves the static file tree Kodi polls

### Critical Pitfalls

1. **ZIP nesting wrong** — running `zip` from the wrong working directory produces double-nesting (`addon_id/addon_id/addon.xml`) which Kodi rejects with "invalid structure." Prevention: always zip from the directory *containing* the addon folder; add CI assertion that `unzip -l` first entry is `<addon_id>/addon.xml`.

2. **Stale or mismatched checksum files** — if `addons.xml.md5` / `addons.xml.sha256` are not regenerated atomically with `addons.xml`, Kodi sees no change and silently skips the update; users are stuck on old versions with no error. Prevention: regenerate both checksum files in the same script step immediately after writing `addons.xml`; commit all three in the same git commit.

3. **Version not bumped in `addon.xml`** — Kodi compares version strings; if identical to installed version, no update is offered regardless of ZIP content. Prevention: make version bump a mandatory CI gate in the plugin repo; consider `felixmosh/kodi-addon-release` to automate bump + tag + changelog.

4. **Repository addon URLs stale or wrong** — if any of the three `<dir>` URLs are unreachable, Kodi shows "Could not connect to repository" and every addon fails silently. Prevention: CI smoke-tests all three URLs for HTTP 200 after every deploy; treat these URLs as load-bearing configuration.

5. **BOM bytes or CRLF in `addons.xml`** — Kodi's XML parser fails silently on UTF-8 BOM; the repo appears to install but the addon list is empty. Prevention: write `addons.xml` with explicit `encoding='utf-8'` (not `utf-8-sig`), `newline='\n'`; add a byte-level CI assertion.

---

## Implications for Roadmap

### Phase 1: Bootstrap Repo Skeleton + First Manual Publish

**Rationale:** The GitHub Pages URL must be known before it can be coded into `addon.xml`. The repo-addon must be authored first (it declares the URLs), then GitHub Pages confirmed live, then a minimal `addons.xml` deployed so Kodi can actually see the repository. This phase is intentionally manual — running `generate.py` locally and pushing by hand — to prove the protocol works before automation is layered on. The build order from ARCHITECTURE.md drives this sequence directly.

**Delivers:** A Kodi-recognisable repository: users can add the source URL, install `repository.sandwichfarm-1.0.0.zip`, and see the repo listed in Kodi's addon browser. `plugin.audio.subsonic` is installable (ZIP produced manually). This is the "does Kodi see us?" validation.

**Addresses from FEATURES.md:** All Kodi protocol-required table stakes — `addons.xml`, both checksum files, versioned ZIP, artwork, changelog, repo-addon ZIP with `<dir>` wrapper, HTTPS-only URLs.

**Avoids from PITFALLS.md:** Pitfall 5 (datadir URL mismatch) by validating URL layout before CI exists; Pitfall 7 (stale repo-addon URLs) by confirming all three endpoint URLs return HTTP 200 before announcing the repo.

### Phase 2: Automate the Publishing Pipeline

**Rationale:** Once Phase 1 proves the protocol, the manual process is a liability — one missed checksum regeneration breaks updates for all users indefinitely. This phase converts the manual steps into a GitHub Actions workflow triggered by `push`, `workflow_dispatch`, and `repository_dispatch`. It also adds the CI validation suite that prevents the silent-failure class of pitfalls identified in research.

**Delivers:** Author can release a new plugin version by tagging in `plugin.audio.subsonic` — no manual steps in this repo. CI produces and validates the full artifact set on each run. `plugins.json` manifest is in place so a second plugin can be onboarded with a one-line edit.

**Uses from STACK.md:** `actions/checkout@v4`, `actions/setup-python@v5`, `stefanzweifel/git-auto-commit-action@v5`; `generate.py` adapted from drinfernoo's `_repo_generator.py` with SHA-256 support added.

**Avoids from PITFALLS.md:** Pitfalls 1 (ZIP nesting), 2 (stale checksums), 4 (BOM/CRLF), and the full "looks done but isn't" checklist — all addressed by CI assertions baked into this phase.

### Phase 3: Onboard `plugin.audio.subsonic` End-to-End + User Docs

**Rationale:** Phase 2 delivers a working pipeline; Phase 3 delivers the core stated value — a Kodi user discovering, installing, and auto-updating `plugin.audio.subsonic` through the repo without touching a ZIP file manually. This phase also wires the `repository_dispatch` cross-repo trigger from `plugin.audio.subsonic`'s release workflow and writes the definitive end-user install guide.

**Delivers:** The complete value proposition from PROJECT.md: "Kodi users can install and stay up-to-date on sandwichfarm plugins by adding a single repository URL to Kodi." Documentation is complete enough that a new Kodi user on Android/FireTV can follow it without getting stuck. Full release cycle tested: tag in plugin repo → Kodi auto-updates within 24h.

**Addresses from FEATURES.md:** `repository_dispatch` cross-repo automation; `kodi-addon-checker` gate in plugin CI; end-user documentation with Android/FireTV-specific steps; changelog file automation; install verification step.

**Avoids from PITFALLS.md:** Pitfall 3 (version not bumped — enforced in plugin CI); UX pitfalls (Unknown Sources step as Step 0, FireTV path differences, install verification step at end of guide).

### Phase 4 (Optional): Multi-Plugin Scale + Version Branching

**Rationale:** Defer until a second plugin exists or there is evidence that Nexus vs. Omega compatibility is a real problem for existing users. The `plugins.json` + loop design from Phase 2 means adding a second plugin is a one-line change. Multi-Kodi-version directory branches are the only structural addition; only introduce them if a specific addon requires it.

**Delivers:** A second (or Nth) addon distributed through the repo; optionally a Kodi-version branching structure if a plugin breaks compatibility between versions.

**Addresses from FEATURES.md:** Multi-addon support via `plugins.json` (already designed in); multi-Kodi-version `<dir minversion>` / `<dir maxversion>` branching; pre-release channel.

### Phase Ordering Rationale

- Phase 1 before Phase 2: you cannot automate URLs you have not confirmed work; manual first-publish validates the protocol without CI complexity masking errors.
- Phase 2 before Phase 3: the `repository_dispatch` cross-repo trigger in Phase 3 requires the publisher pipeline to exist and be proven reliable.
- Phase 4 deferred: `plugins.json` N-plugin design is already in place from Phase 2; no architectural work needed until a second plugin exists.
- Flat single-directory layout (no per-version branches) for Phases 1-3: targeting Nexus/Omega; version branching adds complexity with no user benefit until an incompatible version exists.

### Research Flags

**Phases with standard patterns (skip research-phase):**
- **Phase 1:** Kodi repository protocol fully documented in Repository.cpp and community examples; addon.xml schema is stable. No research needed.
- **Phase 2:** GitHub Actions + Python stdlib + `git-auto-commit-action` is a well-documented pattern verified directly in dot-Justin/kodi-repo.

**Phases that benefit from a focused spike before planning:**
- **Phase 3 (`repository_dispatch` wiring):** The cross-repo authentication setup (PAT scope, secret storage, payload shape) is straightforward but warrants a 30-minute implementation spike; JonathanHolvey/kodi-repo-updater covers the pattern.
- **Phase 3 (`plugin.audio.subsonic` addon.xml audit):** Verify the existing `addon.xml` in that repo declares `xbmc.python version="3.0.0"` (not 2.x) and uses the `<dir>` wrapper — one file read resolves this, no deep research needed.

---

## Confidence Assessment

| Area | Confidence | Notes |
|------|------------|-------|
| Stack | MEDIUM-HIGH | Kodi Wiki blocked during research; compensated with xbmc/xbmc source code (HIGH) and cross-verified community examples (MEDIUM); no remaining gaps on the decisions made |
| Features | HIGH | Protocol features verified directly against Repository.cpp source; convention features cross-verified across multiple repos |
| Architecture | HIGH | Polling sequence and file layout verified against Repository.cpp; component boundaries and trigger pattern cross-verified against JonathanHolvey/kodi-repo-updater and dot-Justin/kodi-repo |
| Pitfalls | MEDIUM-HIGH | ZIP nesting, BOM, stale MD5 verified in Kodi forum threads and source; xbmc.python version mapping verified against xbmc/addon-check source |

**Overall confidence:** MEDIUM-HIGH

### Gaps to Address

- **`plugin.audio.subsonic` current `addon.xml` state:** Research did not inspect the actual file. Before Phase 3 implementation, read `addon.xml` to confirm: (a) `xbmc.python` version is `3.0.0`, not 2.x; (b) `<dir>` wrapper is used; (c) declared addon `id` is exactly `plugin.audio.subsonic`. A mismatch in (c) would require renaming the distribution directory.
- **`addons.xml.gz` requirement for Omega/Piers:** PITFALLS.md flags Omega may require `addons.xml.gz`; STACK.md and ARCHITECTURE.md confirm plain `addons.xml` works because GitHub Pages negotiates gzip automatically. Risk is LOW for Phases 1-3 but monitor if Piers stable changes this. Pre-compressing costs one line in `generate.py` if needed.
- **GitHub Pages deploy latency in CI smoke tests:** Pages can take 30-90 seconds to go live after a push. The CI smoke test step must include a wait/retry loop or Pages API deployment status check rather than a fixed sleep — needs a concrete implementation decision in Phase 2 planning.

---

## Sources

### Primary (HIGH confidence)
- https://github.com/xbmc/xbmc/blob/master/xbmc/addons/Repository.cpp — polling sequence, hash algorithm handling (MD5 deprecation warning, SHA256 support), checksum gating logic
- https://github.com/xbmc/xbmc/blob/master/addons/repository.xbmc.org/addon.xml — official reference repo-addon showing `<checksum verify="sha256">` and `<dir>` wrapper
- https://github.com/xbmc/xbmc/blob/master/addons/xbmc.python/addon.xml — xbmc.python 3.0.2 version mapping
- https://pypi.org/project/kodi-addon-checker/ — version 0.0.36, June 2025, Python 3.8-3.13
- https://docs.github.com/en/pages/getting-started-with-github-pages/github-pages-limits — 100 GB/month soft bandwidth, 1 GB size limit

### Secondary (MEDIUM confidence)
- https://github.com/drinfernoo/repository.example — canonical community repo template; `_repo_generator.py` source; widely forked
- https://github.com/dot-Justin/kodi-repo — GitHub Actions workflow verified (checkout@v4, setup-python@v5, git-auto-commit); modern example
- https://github.com/JonathanHolvey/kodi-repo-updater — demonstrates cross-repo release event trigger pattern
- https://github.com/chadparry/kodi-repository.chad.parry.org — `create_repository.py`; copyright 2016-2022; maintenance status unclear post-2022
- https://kodi.wiki/view/Add-on_repositories — official wiki (cross-verified against source code)
- https://github.com/xbmc/addon-check/blob/master/kodi_addon_checker/check_dependencies.py — xbmc.python version validation logic
- https://forum.kodi.tv/showthread.php?tid=196459 — addons.xml.md5 / checksum behaviour confirmation
- https://github.com/xbmc/xbmc/issues/16104 — addons.xml.gz SHA256 check failure (Omega relevance)

### Tertiary (LOW confidence)
- https://troypoint.com/kodi-22-piers/ — Kodi 22 Piers Alpha 3 Python 3.14.3 (third-party; cross-verified via kodi.tv Alpha 3 release notes)
- https://community.cloudflare.com/t/static-site-deployments-causing-prolonged-404s-to-users/558247 — Cloudflare Pages 404 caching behaviour (community thread; not officially documented)

---
*Research completed: 2026-04-29*
*Ready for roadmap: yes*
