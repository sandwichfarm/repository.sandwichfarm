# Feature Research

**Domain:** Kodi addon repository (self-hosted static distribution endpoint)
**Researched:** 2026-04-29
**Confidence:** HIGH (core protocol), MEDIUM (differentiators), LOW (anti-feature details)

---

## Preamble: Two Feature Surfaces

This project has two distinct feature surfaces that must be kept separate:

- **End-user surface** — What a Kodi user experiences when they install and use the repo
- **Author surface** — What the repo maintainer does to publish and update addons

Both must be designed. The end-user surface is mostly driven by the Kodi protocol (non-negotiable). The author surface is where most design decisions live.

---

## Table Stakes (Kodi protocol-required)

These are required by the Kodi update/install protocol. Missing any one = Kodi cannot recognize the repo or detect updates. **These are not conventions — Kodi source code (Repository.cpp) enforces them.**

### End-User Side (What Kodi Fetches)

| Feature | Why Required | Complexity | Notes |
|---------|--------------|------------|-------|
| `addons.xml` at repo base URL | Kodi fetches this to discover all addons and their current versions | TRIVIAL | Must be XML wrapping each addon's `addon.xml` content inside a root `<addons>` tag |
| `addons.xml.md5` at repo base URL | Kodi reads this to skip a full re-download when nothing changed | TRIVIAL | MD5 hex digest of `addons.xml` content; depends on `addons.xml` existing first |
| Versioned ZIP at canonical path | Kodi downloads this to install or update the addon | TRIVIAL | Path: `<base>/<addon.id>/<addon.id>-<version>.zip`; zip root must be `<addon.id>/` |
| `icon.png` alongside each addon | Kodi displays this in the addon browser | TRIVIAL | 512×512 px; served at `<base>/<addon.id>/icon.png` |
| `fanart.jpg` alongside each addon | Kodi displays this as background art | TRIVIAL | 1920×1080 px; served at `<base>/<addon.id>/fanart.jpg` |
| `changelog-X.Y.Z.txt` alongside each addon | Kodi shows this in the addon info dialog | TRIVIAL | Version in filename must match the ZIP version exactly; served at `<base>/<addon.id>/changelog-X.Y.Z.txt` |

### The Wrapper "Repository" Addon ZIP (Author Produces Once, User Installs Once)

This is the ZIP the end-user downloads and installs to wire Kodi to the repo. It contains its own mini-addon that declares the repository's URLs.

| Feature | Why Required | Complexity | Notes |
|---------|--------------|------------|-------|
| `addon.xml` with `extension point="xbmc.addon.repository"` | Without this extension point Kodi does not recognize the ZIP as a repository addon | TRIVIAL | The `id` attribute must match the ZIP filename prefix (e.g., `repository.sandwichfarm`) |
| `<dir>` element inside the extension | Wraps all endpoint URLs for one Kodi-version target | TRIVIAL | Can have multiple `<dir>` blocks for version branching |
| `<info>` URL inside `<dir>` | URL to `addons.xml` (or `addons.xml.gz`) — Kodi fetches this on every check | TRIVIAL | Must be publicly reachable HTTPS URL |
| `<checksum verify="sha256">` URL inside `<dir>` | URL to the checksum sidecar — Kodi compares to skip full re-fetch | TRIVIAL | The `verify` attribute names the hash algorithm; `sha256` preferred; `md5` works but is deprecated with a Kodi source warning |
| `<datadir zip="true">` URL inside `<dir>` | Base URL where Kodi constructs addon ZIP paths (`<datadir>/<id>/<id>-<ver>.zip`) | TRIVIAL | `zip="true"` tells Kodi addons are distributed as ZIPs |
| `<requires><import addon="xbmc.addon" version="12.0.0"/>` | Declares minimum Kodi compatibility | TRIVIAL | Version 12.0.0 is the safe floor for all current Kodi releases |
| Wrapper ZIP named `repository.<name>-<version>.zip` | Kodi install-from-zip flow expects this naming | TRIVIAL | Kodi enforces `repository.<name>-<version>.zip` filename convention |

### Versioning (Protocol Enforced)

| Rule | Why It Matters | Complexity | Notes |
|------|----------------|------------|-------|
| `MAJOR.MINOR.PATCH` three-component version in `addon.xml` | Kodi parses version as three integers for comparison | TRIVIAL | No pre-release suffixes (no `-beta`, `-rc`) in the version attribute; these break comparison |
| Version must strictly increment to trigger update | Kodi compares installed version vs. repo version; same or lower = no update offered | TRIVIAL | Kodi selects highest version across all repos; no downgrade possible without manual removal |
| Version in `addon.xml` must match the ZIP filename version | Kodi constructs the download URL from `addon.xml` version; mismatch = 404 | TRIVIAL | Single source of truth: `addon.xml` version drives everything |

---

## Table Stakes (Strong Convention — Not Protocol-Enforced but Expected by Users)

| Feature | Why Expected | Complexity | Notes |
|---------|--------------|------------|-------|
| Clear human-readable install instructions | Kodi's install-from-zip flow is non-obvious for new users; no guide = no installs | LOW | Covers: enable Unknown Sources, File Manager add-source, install from zip, install from repo. Steps differ slightly between Kodi versions |
| `README.md` or landing page with the repo ZIP URL | Users need one copy-pasteable URL to get started | TRIVIAL | GitHub Pages gives a clean URL; the install flow starts here |
| HTTPS-only URLs in `addon.xml` | Kodi logs a warning for plain HTTP; some Kodi builds refuse HTTP repos | TRIVIAL | GitHub Pages and Cloudflare Pages provide HTTPS at no cost |
| `addon.xml` inside the repo addon must have a human-readable `<summary>` and `<description>` | Kodi shows these in the repo info dialog | TRIVIAL | At minimum English; more languages optional |

---

## Differentiators (Nice to Have for a Personal Repo)

### End-User Side

| Feature | Value Proposition | Complexity | Notes |
|---------|-------------------|------------|-------|
| Multi-Kodi-version directory branches | Serve different addon builds to Matrix (19.x), Nexus (20.x), Omega (21.x), Piers (22.x) without users doing anything | MEDIUM | Uses `<dir minversion="X" maxversion="Y">` blocks in `addon.xml`; requires separate `addons.xml` and ZIPs per branch directory |
| `artdir` separate from `datadir` | Serve artwork from a CDN or separate path for performance | LOW | `<artdir>` element; defaults to `datadir` if omitted; rarely needed for a small personal repo |
| Pre-compressed `addons.xml.gz` | Reduces transfer size; Kodi requests gzip by default | LOW | Pre-gzip and set `compressed="true"` if server does not negotiate gzip; GitHub Pages does negotiate gzip so pre-compression is optional |
| `X-Kodi-Recheck-After` HTTP response header | Tells Kodi clients how long to cache before rechecking (1h–1 week range); reduces unnecessary fetches | LOW | Static hosts like GitHub Pages do not send this header; Kodi defaults to 24 hours; acceptable for a personal repo |

### Author Side

| Feature | Value Proposition | Complexity | Notes |
|---------|-------------------|------------|-------|
| Automated `addons.xml` rebuild on tag push | Pushing a version tag regenerates the index without manual editing | MEDIUM | GitHub Actions: checkout addon repo at tag, run `create_repository.py` or equivalent, commit updated `addons.xml` + `addons.xml.md5` + ZIP to repo |
| `kodi-addon-checker` validation in CI | Catches addon.xml errors, missing artwork, broken XML before release | LOW | Official GitHub Action: `xbmc/action-kodi-addon-checker@v1.1`; takes `kodi-version` and optional `addon-id` inputs |
| Multiple addons in one repo | Scale to N plugins without changing the repo structure or user's install step | LOW | `addons.xml` is a flat aggregate; `create_repository.py` accepts multiple source directories; each addon gets its own subdirectory |
| Separate `beta` or `pre-release` directory branch | Let willing testers opt into pre-release builds by installing a second repo addon | MEDIUM | Requires a second `addon.xml` for the beta repo pointing at a `/beta/` directory; separate `addons.xml` with higher version numbers |
| Changelog auto-generated from Git tags/commits | `changelog-X.Y.Z.txt` written automatically from commit messages | LOW | Simple shell or Python script extracting `git log` between tags |

---

## Anti-Features (Deliberately Not Building)

| Anti-Feature | Why It Seems Appealing | Why Not / What to Do Instead |
|--------------|----------------------|------------------------------|
| Bundling third-party addon ZIPs | Lets users install popular addons from one place | Out of scope (PROJECT.md constraint); creates licensing and trust liability; the repo is scoped to sandwichfarm-authored code only |
| Telemetry / download counting | Understand how many users have installed | Static hosting has no server-side logging; adding tracking scripts to addon code violates Kodi addon rules (banned addon behavior); use GitHub Insights for repo traffic instead |
| Analytics beacons inside addon code | Behavioral insights | Kodi addon rules ban this; creates privacy risk for users; treat it as a hard no |
| Hardcoded paid/subscription credentials | Gate content behind a service the repo operator doesn't own | Core piracy repo pattern; violates both Kodi rules and copyright law |
| Fork-bombing (re-hosting someone else's addon without permission) | Increase catalog size | Legal exposure; reputation damage; content can change upstream without notice |
| Signed addons via official Kodi signing infrastructure | Appear "official" | Out of scope (PROJECT.md constraint); the signing pipeline requires official repo submission, which has its own review process; HTTPS distribution + Unknown Sources is the correct path for personal repos |
| In-repo web storefront / SPA | Pretty browseable UI | Kodi's built-in addon browser is the UX; a web UI duplicates work and adds maintenance; Kodi renders icon/fanart/description natively |
| Mirror list / CDN integration | Faster downloads globally | Complexity not justified for a personal single-author repo; GitHub Pages CDN (Fastly) is sufficient |
| Version downgrade support | Let users pin to older versions | Kodi does not support downgrade from the UI; implementing it requires out-of-band manual ZIP installation anyway |

---

## Feature Dependencies

```
[addons.xml] ──requires──> [each addon's addon.xml exists and is valid]
[addons.xml.md5] ──requires──> [addons.xml]
[changelog-X.Y.Z.txt] ──requires──> [version in addon.xml matches X.Y.Z]
[versioned ZIP at canonical path] ──requires──> [version in addon.xml matches filename]

[repository addon ZIP] ──requires──> [addons.xml URL is reachable]
[repository addon ZIP] ──requires──> [checksum URL is reachable]
[repository addon ZIP] ──requires──> [datadir URL resolves ZIP paths correctly]

[end-user install flow] ──requires──> [Unknown Sources enabled in Kodi Settings]
[end-user install flow] ──requires──> [File Manager source added pointing at repo base URL]
[install from repo] ──requires──> [repository addon ZIP installed first]

[automated addons.xml rebuild] ──requires──> [addons.xml generator script]
[automated addons.xml rebuild] ──requires──> [CI reads addon repos at tagged commits]
[kodi-addon-checker CI] ──enhances──> [automated addons.xml rebuild] (validation gate before deploy)

[multi-version branches] ──requires──> [separate addons.xml per branch directory]
[multi-version branches] ──requires──> [minversion/maxversion on <dir> elements]
[multi-version branches] ──conflicts──> [single flat addons.xml approach]

[pre-release channel] ──requires──> [second repository addon ZIP for beta URL]
[pre-release channel] ──requires──> [separate beta directory with its own addons.xml]
```

### Dependency Notes

- **addons.xml depends on addon.xml validity:** `create_repository.py` and equivalents read each addon's `addon.xml` to assemble `addons.xml`. Malformed `addon.xml` breaks the whole index.
- **ZIP filename must match addon.xml version:** Kodi constructs the download URL as `<datadir>/<id>/<id>-<version>.zip`. If the ZIP file on disk does not match, install fails with a 404. Version is the single source of truth.
- **addons.xml.md5 depends on addons.xml:** Must be regenerated every time `addons.xml` changes. Stale checksum causes Kodi to think the index is corrupt or re-fetch unnecessarily.
- **Multi-version branches conflict with single flat addons.xml:** Once you introduce version branching, each branch needs its own directory tree and `addons.xml`. Cannot mix both patterns.
- **Unknown Sources must be enabled before install-from-zip:** This is a one-time user action. All non-official-repo addon installation flows require it. Documentation must lead with this step.

---

## MVP Definition

### Launch With (v1)

Minimum needed for a Kodi user to install `plugin.audio.subsonic` via this repo and receive auto-updates.

- [ ] `addons.xml` aggregating `plugin.audio.subsonic` metadata — without this Kodi cannot see the addon
- [ ] `addons.xml.md5` — Kodi skips update check if checksum matches; missing it causes repeated full fetches
- [ ] `plugin.audio.subsonic/plugin.audio.subsonic-X.Y.Z.zip` at the canonical path — install target
- [ ] `plugin.audio.subsonic/icon.png` (512×512) and `plugin.audio.subsonic/fanart.jpg` (1920×1080) — Kodi renders these in the addon browser
- [ ] `plugin.audio.subsonic/changelog-X.Y.Z.txt` — expected by the info dialog
- [ ] `repository.sandwichfarm/addon.xml` with `xbmc.addon.repository` extension, correct `<info>`, `<checksum>`, `<datadir>` URLs — the repo registration artifact
- [ ] `repository.sandwichfarm-X.Y.Z.zip` — the installable wrapper users install first
- [ ] `repository.sandwichfarm/icon.png` and `repository.sandwichfarm/fanart.jpg` — Kodi shows these for the repo entry itself
- [ ] Human-readable install documentation covering Unknown Sources → File Manager add-source → install from zip → install from repository

### Add After Validation (v1.x)

- [ ] `kodi-addon-checker` in CI — add once the basic publish flow is proven; catches regressions on future addons
- [ ] Automated `addons.xml` rebuild on tag push (GitHub Actions) — add once the structure is validated manually; reduces friction for second and subsequent addon releases
- [ ] Second addon in the repo — validates that the multi-addon structure scales as intended

### Future Consideration (v2+)

- [ ] Multi-Kodi-version directory branches (`minversion`/`maxversion`) — defer until there is evidence that Matrix vs. Omega compatibility is actually a problem for a specific addon
- [ ] Pre-release / beta channel — defer until there is an active user base worth beta-testing with
- [ ] Pre-compressed `addons.xml.gz` — defer; GitHub Pages gzip negotiation is sufficient

---

## Feature Prioritization Matrix

| Feature | User Value | Implementation Cost | Priority |
|---------|------------|---------------------|----------|
| `addons.xml` + `addons.xml.md5` | HIGH | LOW | P1 |
| Versioned ZIP at canonical path | HIGH | LOW | P1 |
| `icon.png` / `fanart.jpg` per addon | HIGH | LOW | P1 |
| `changelog-X.Y.Z.txt` per addon | MEDIUM | LOW | P1 |
| Repository wrapper addon ZIP | HIGH | LOW | P1 |
| End-user install documentation | HIGH | LOW | P1 |
| Automated addons.xml rebuild in CI | HIGH (author) | MEDIUM | P2 |
| `kodi-addon-checker` CI validation | MEDIUM (author) | LOW | P2 |
| Multi-addon support | HIGH (author, future) | LOW | P2 |
| HTTPS-only URLs | HIGH | LOW | P1 |
| Multi-Kodi-version branches | LOW (now) | MEDIUM | P3 |
| Pre-release channel | LOW (now) | MEDIUM | P3 |
| Pre-compressed addons.xml.gz | LOW | LOW | P3 |

---

## Reference Implementations Observed

| Repo | Approach | Notable |
|------|----------|---------|
| `drinfernoo/repository.example` | GitHub Pages + `_repo_generator.py` | Canonical personal repo template; shows `minversion`/`maxversion` multi-dir pattern |
| `dot-Justin/kodi-repo` | GitHub Actions + Python tools | GitHub Actions auto-regenerates `addons.xml` + `.md5` on push |
| `chadparry/kodi-repository.chad.parry.org` | `create_repository.py` CLI | Accepts local folders, ZIPs, or Git URLs; produces ZIPs + `addons.xml` + `.md5`; widely forked |
| `ping/instant-kodi-repo` | Travis CI → GitHub Pages | Full automation but uses Travis (legacy); pattern still valid with GitHub Actions |
| `repository.xbmc.org` (official) | Mirror CDN + SHA256 + gzip | Shows `artdir`, `hashes`, `verify="sha256"` attributes; reference for what mature repos use |
| `i96751414/repository.github` | Dynamic HTTP server reading GitHub releases | Non-static approach; not suitable for this project but shows the "serve ZIPs from GitHub releases" pattern |

---

## Sources

- [Add-on repositories — Official Kodi Wiki](https://kodi.wiki/view/Add-on_repositories)
- [Addon.xml — Official Kodi Wiki](https://kodi.wiki/view/Addon.xml)
- [repository.xbmc.org/addon.xml — Kodi source](https://github.com/xbmc/xbmc/blob/master/addons/repository.xbmc.org/addon.xml)
- [Repository.cpp — Kodi source (fetch/hash/version logic)](https://github.com/xbmc/xbmc/blob/master/xbmc/addons/Repository.cpp)
- [xbmc/action-kodi-addon-checker — GitHub Action](https://github.com/xbmc/action-kodi-addon-checker)
- [xbmc/addon-check — kodi-addon-checker tool](https://github.com/xbmc/addon-check)
- [drinfernoo/repository.example — GitHub Pages template](https://github.com/drinfernoo/repository.example)
- [chadparry create_repository.py](https://github.com/chadparry/kodi-repository.chad.parry.org/blob/master/tools/create_repository.py)
- [dot-Justin/kodi-repo](https://github.com/dot-Justin/kodi-repo/tree/main)
- [ping/instant-kodi-repo](https://github.com/ping/instant-kodi-repo)
- [felixmosh/kodi-addon-release](https://github.com/felixmosh/kodi-addon-release)
- [Enable unknown sources — dimkroon.net guide](https://dimkroon.net/en/guides/enable-unknown-sources.html)
- [Install from zip — dimkroon.net guide](https://dimkroon.net/en/guides/install-from-zip.html)
- [TechNadu: Install Kodi Addons from ZIP Files 2026](https://www.technadu.com/install-kodi-addons-from-zip-files/188438/)

---

*Feature research for: Kodi addon repository (repository.sandwichfarm)*
*Researched: 2026-04-29*
