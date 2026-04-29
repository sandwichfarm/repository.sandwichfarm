# Architecture Research

**Domain:** Kodi addon repository — static distribution endpoint
**Researched:** 2026-04-29
**Confidence:** HIGH (Kodi's protocol is stable and well-documented in source; behavior verified against Repository.cpp)

---

## Standard Architecture

### System Overview

```
┌──────────────────────────────────────────────────────────────────────┐
│  SOURCE LAYER (external, per-plugin repos)                           │
│  ┌─────────────────────────┐                                         │
│  │  github.com/sandwichfarm│                                         │
│  │  /plugin.audio.subsonic │  (+ future plugins, each in own repo)  │
│  │  → tags/releases/ZIPs   │                                         │
│  └────────────┬────────────┘                                         │
└───────────────┼──────────────────────────────────────────────────────┘
                │ trigger (release event / repository_dispatch / cron)
                ▼
┌──────────────────────────────────────────────────────────────────────┐
│  PUBLISHER LAYER (this repo: repository.sandwichfarm)                │
│  ┌──────────────────────────────────────────────────────────────┐    │
│  │  GitHub Actions workflow                                      │    │
│  │  1. Fetch plugin source or release ZIP from upstream repo    │    │
│  │  2. Package addon ZIP:  addon.id/addon.id-x.y.z.zip         │    │
│  │  3. Copy icon.png / fanart.jpg / changelog-x.y.z.txt        │    │
│  │  4. Assemble addons.xml  (concatenate all addon.xml entries) │    │
│  │  5. Write addons.xml.md5  (any string, must change on edit)  │    │
│  │  6. Build repo-addon ZIP: repository.sandwichfarm-x.y.z.zip │    │
│  │  7. Commit/push to gh-pages branch → GitHub Pages deploys   │    │
│  └──────────────────────────────────────────────────────────────┘    │
└───────────────┬──────────────────────────────────────────────────────┘
                │ static files served over HTTPS
                ▼
┌──────────────────────────────────────────────────────────────────────┐
│  HOST LAYER (GitHub Pages / Cloudflare Pages / S3)                   │
│                                                                      │
│  https://sandwichfarm.github.io/repository.sandwichfarm/            │
│  ├── addons.xml                ← Kodi fetches this (gzip accepted)   │
│  ├── addons.xml.md5            ← Kodi checks this first             │
│  ├── repository.sandwichfarm/ ← repo-addon directory                │
│  │   ├── addon.xml                                                   │
│  │   ├── icon.png                                                    │
│  │   └── repository.sandwichfarm-1.0.0.zip   ← user installs once  │
│  └── plugin.audio.subsonic/                                          │
│      ├── addon.xml             ← copy of plugin's addon.xml         │
│      ├── icon.png                                                    │
│      ├── fanart.jpg                                                  │
│      ├── changelog-2.1.0.txt                                         │
│      └── plugin.audio.subsonic-2.1.0.zip     ← what Kodi downloads  │
└───────────────┬──────────────────────────────────────────────────────┘
                │ Kodi polls addons.xml.md5 every ~24h
                ▼
┌──────────────────────────────────────────────────────────────────────┐
│  KODI CLIENT LAYER                                                   │
│  ┌─────────────────────────────────┐                                 │
│  │  repository.sandwichfarm addon  │  (installed once via ZIP)       │
│  │  addon.xml points at:           │                                 │
│  │    info     → .../addons.xml    │                                 │
│  │    checksum → .../addons.xml.md5│                                 │
│  │    datadir  → .../             │                                 │
│  └────────────┬────────────────────┘                                 │
│               │ auto-update poll                                      │
│               ▼                                                       │
│  ┌─────────────────────────────────┐                                 │
│  │  Kodi addon manager             │                                 │
│  │  - fetches checksum, compares   │                                 │
│  │  - on change: fetches addons.xml│                                 │
│  │  - downloads updated plugin ZIP │                                 │
│  └─────────────────────────────────┘                                 │
└──────────────────────────────────────────────────────────────────────┘
```

---

## The Two Layers Kodi Sees

### Layer 1: The Repository Addon (user installs once)

This is a ZIP named `repository.<name>-<version>.zip` that contains:

```
repository.sandwichfarm/
├── addon.xml          ← type="xbmc.addon.repository", declares endpoints
├── icon.png           ← shown in Kodi's addon browser
└── fanart.jpg         ← optional background art
```

The `addon.xml` for this addon uses the `xbmc.addon.repository` extension point:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<addon id="repository.sandwichfarm"
       name="Sandwichfarm Repository"
       version="1.0.0"
       provider-name="sandwichfarm">
  <extension point="xbmc.addon.repository" name="Sandwichfarm Repository">
    <dir>
      <info compressed="false">https://sandwichfarm.github.io/repository.sandwichfarm/addons.xml</info>
      <checksum>https://sandwichfarm.github.io/repository.sandwichfarm/addons.xml.md5</checksum>
      <datadir zip="true">https://sandwichfarm.github.io/repository.sandwichfarm/</datadir>
      <hashes>false</hashes>
    </dir>
  </extension>
  <extension point="xbmc.python.module" library="." />
  <extension point="xbmc.addon.metadata">
    <summary lang="en_GB">Sandwichfarm Kodi Repository</summary>
    <platform>all</platform>
  </extension>
</addon>
```

The `<dir>` element wrapper is required in Kodi Nexus (v20) and later. The flat approach (info/checksum/datadir directly under the extension point) was removed in Nexus.

### Layer 2: The Index / Files Endpoint (what Kodi polls)

The static site the repo-addon points at. It is not an addon — it is a set of files at predictable paths.

**Key file:** `addons.xml` — concatenation of every plugin's `addon.xml` wrapped in `<addons>`:

```xml
<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<addons>
  <!-- full content of repository.sandwichfarm/addon.xml -->
  <addon id="repository.sandwichfarm" ...>...</addon>
  <!-- full content of plugin.audio.subsonic/addon.xml -->
  <addon id="plugin.audio.subsonic" ...>...</addon>
</addons>
```

**Key file:** `addons.xml.md5` — a string Kodi checks before fetching `addons.xml`. It does not have to be an actual MD5; it just must change whenever `addons.xml` changes. An MD5 of the file contents is the standard approach.

---

## How Kodi Polls for Updates

Source: `Repository.cpp` in xbmc/xbmc.

**Sequence (every ~24 hours by default):**

1. Kodi fetches `checksum` URL → gets current `addons.xml.md5` value
2. Compares to its stored value from last check
3. If unchanged → skip; if changed → fetch full `addons.xml`
4. Kodi parses `addons.xml`, compares versions to installed addons
5. For each addon with a newer version: downloads `<datadir>/<addon.id>/<addon.id>-<version>.zip`
6. Before downloading a ZIP, Kodi may issue a HEAD request and compare `Content-MD5` header to stored hash (if `hashes` is enabled)

**Update interval:** Default 24 hours. Can be overridden by `X-Kodi-Recheck-After` HTTP response header (values clamped between 1 hour and 7 days). GitHub Pages does not set this header, so the default 24-hour poll applies.

**User-triggered check:** Users can force an immediate check via Kodi's add-on manager ("Check for updates"). This is how you test during development.

**Implication:** The `addons.xml.md5` is the gating mechanism. If it does not change, Kodi never re-fetches the index. Every time you publish a new plugin version you must regenerate both `addons.xml` AND `addons.xml.md5`.

---

## Static Site File/Directory Layout

This is what the HOST layer must serve. All paths are relative to the `<datadir>` URL.

```
<repo-root>/                              ← datadir URL points here
├── addons.xml                            ← master index
├── addons.xml.md5                        ← change-sentinel string
├── repository.sandwichfarm/             ← repo-addon files
│   ├── addon.xml                         ← copy of repo-addon's addon.xml
│   ├── icon.png                          ← 512×512 PNG
│   ├── fanart.jpg                        ← 1920×1080 JPG (optional)
│   └── repository.sandwichfarm-1.0.0.zip ← what user installs
└── plugin.audio.subsonic/               ← one dir per plugin
    ├── addon.xml                         ← copy of plugin's addon.xml
    ├── icon.png
    ├── fanart.jpg
    ├── changelog-2.1.0.txt              ← shown in Kodi's changelog view
    └── plugin.audio.subsonic-2.1.0.zip  ← what Kodi downloads on install/update
```

**URL Kodi uses to fetch a plugin ZIP:**
`<datadir>/<addon.id>/<addon.id>-<version>.zip`

This is constructed automatically from the `<datadir>` value in the repo-addon's `addon.xml` plus the `id` and `version` from `addons.xml`. You do not configure it per-plugin; the layout is the convention.

**Optional `addons.xml.gz`:** The official Kodi repo serves a gzip-compressed version at `addons.xml.gz`. Kodi sends `Accept-Encoding: gzip` and will use a pre-compressed file if the `<info>` URL ends in `.gz`. For a personal repo on GitHub Pages, serving plain `addons.xml` is fine; Kodi falls back to uncompressed without issue.

---

## Component Boundaries

| Component | Role | Lives In | Outputs |
|-----------|------|----------|---------|
| **Source Plugin** | The actual Kodi addon code | `github.com/sandwichfarm/plugin.audio.subsonic` (external repo) | Tagged release, optionally a release ZIP asset |
| **Publisher** | Builds the index + packages ZIPs | `repository.sandwichfarm` GitHub Actions | `addons.xml`, `addons.xml.md5`, plugin ZIPs |
| **Host** | Serves static files over HTTPS | GitHub Pages (branch: `gh-pages` or root of `main`) | HTTPS URLs Kodi hits |
| **Repo Addon** | Kodi-side stub that wires a Kodi install to this host | `repository.sandwichfarm/addon.xml` inside this repo | A ZIP the user installs once |
| **Kodi Client** | Consumes the index, downloads/installs addons | User's Kodi instance | Not applicable |

**What talks to what:**

```
Source Plugin repo  ──(release event)──►  Publisher (GH Actions)
Publisher           ──(git push)────────►  Host (GitHub Pages)
Host                ◄──(HTTP GET)─────────  Kodi Client (poll)
Repo Addon          ──(installed by user)►  Kodi Client (config)
Repo Addon          ──(points at)────────►  Host endpoints
```

---

## Source-of-Truth Options for Plugin Source

Three patterns exist in the wild. Assessment for a single-author, external-repo setup:

### Option A: Git Submodule (source in this repo)

The publisher repo pulls each plugin source via `git submodule`. The generator script packages ZIPs from the submodule's files.

**Pros:** All source is version-locked here; fully offline build; no GitHub API dependency.

**Cons:** Must update submodule pointer on every plugin release (an extra manual step or automation in the plugin repo). The plugin repo's source must live under the submodule path in the publisher repo, creating coupling.

**Fit:** Medium. Standard recommendation for multi-plugin repos, but adds submodule management overhead.

### Option B: Release Asset Fetch (recommended for this project)

The pipeline in this repo fetches the plugin's source or pre-built ZIP from the plugin repo's GitHub release assets. The plugin repo tags a release, which triggers (via `repository_dispatch` or a scheduled workflow) this publisher repo to fetch and repackage.

**Pros:**
- Plugin repos remain fully independent — no coupling to this repo
- The plugin's maintainer just tags a release; publishing is automatic
- Scales cleanly to N plugins by adding entries to a manifest file
- No submodule pointer bookkeeping

**Cons:** Requires GitHub API access (token) at build time. Build fails if upstream GitHub is unavailable (unlikely but possible).

**Fit:** HIGH for this project. Matches the stated goal: "Building the plugins themselves lives in their own repos; this project only distributes them."

**Trigger mechanism:** Use `repository_dispatch` in the plugin repo's release workflow to fire a webhook into this repo's Actions, or configure a manual `workflow_dispatch` + cron as fallback.

### Option C: ZIP Vendoring (commit pre-built ZIPs)

Manually download ZIPs from plugin releases and commit them to this repo.

**Pros:** Zero build-time external dependencies; trivially simple.

**Cons:** Git history bloat from binary files. Completely manual process — defeats the "auto-update" requirement. Every plugin release requires manual steps.

**Fit:** LOW. Explicitly violates the stated requirement for auto-update on release.

**Verdict: Use Option B (release asset fetch).** Single-author shop, all plugins are on GitHub, automation is a stated requirement.

---

## Build Pipeline Architecture

### Trigger → Build → Publish

```
plugin.audio.subsonic repo
  └─ Release published (git tag v2.1.0)
       └─ Plugin's GH Actions workflow runs
            └─ Dispatches repository_dispatch to repository.sandwichfarm
                  (event: plugin_released, payload: {id, version, repo})

repository.sandwichfarm GH Actions
  └─ On: repository_dispatch (plugin_released)
       OR: workflow_dispatch (manual)
       OR: push to main (for repo-addon changes)
  └─ Steps:
       1. Checkout this repo (publisher)
       2. For each plugin in plugins.json:
            a. Fetch release ZIP from GitHub releases API
            b. Unpack, repack as <id>/<id>-<version>.zip
            c. Copy addon.xml, icon.png, fanart.jpg, changelog
       3. Generate addons.xml from all collected addon.xml files
       4. Generate addons.xml.md5 (md5sum of addons.xml)
       5. Build repository.sandwichfarm ZIP
       6. Commit generated artifacts to gh-pages branch
       7. GitHub Pages serves the result
```

### Plugin Registry (plugins.json)

A manifest file in this repo declares which plugins to include:

```json
[
  {
    "id": "plugin.audio.subsonic",
    "repo": "sandwichfarm/plugin.audio.subsonic",
    "asset_pattern": "{id}-{version}.zip"
  }
]
```

Adding a new plugin = adding one entry. The pipeline picks it up on next run.

---

## Update Flow: New plugin.audio.subsonic Release

```
1.  Author tags v2.1.0 in plugin.audio.subsonic repo
2.  Plugin repo's GH Actions creates a GitHub Release
    → uploads plugin.audio.subsonic-2.1.0.zip as release asset
3.  Plugin repo workflow fires repository_dispatch to repository.sandwichfarm
4.  Publisher GH Actions triggers:
    a. Downloads plugin.audio.subsonic-2.1.0.zip from release assets
    b. Extracts addon.xml → reads <addon id="..." version="2.1.0">
    c. Repacks ZIP into plugin.audio.subsonic/plugin.audio.subsonic-2.1.0.zip
    d. Copies addon.xml, icon.png → plugin.audio.subsonic/ dir
    e. Regenerates addons.xml (updated version entry)
    f. Regenerates addons.xml.md5 (new hash)
    g. Pushes to gh-pages → GitHub Pages updates
5.  Within 24h (or on user-triggered check), Kodi:
    a. Fetches addons.xml.md5 → detects change
    b. Fetches addons.xml → sees version 2.1.0 > installed 2.0.0
    c. Downloads plugin.audio.subsonic-2.1.0.zip from datadir
    d. Updates the addon
```

End-to-end latency from tag to Kodi seeing the update: ~2 minutes for build/deploy + up to 24 hours for Kodi's next poll. Development testing skips the poll wait via "Check for updates" in Kodi's UI.

---

## Recommended Project Structure

```
repository.sandwichfarm/        ← this repo (publisher + repo-addon source)
├── .github/
│   └── workflows/
│       └── publish.yml         ← main pipeline (trigger → build → deploy)
├── repository.sandwichfarm/    ← repo-addon source (committed)
│   ├── addon.xml               ← xbmc.addon.repository pointing at GH Pages URL
│   ├── icon.png
│   └── fanart.jpg
├── plugins.json                ← registry: which external plugin repos to include
├── tools/
│   └── generate.py             ← assembles addons.xml, packages ZIPs
├── .planning/                  ← project planning (not deployed)
└── [gh-pages branch]           ← generated output (do not hand-edit)
    ├── addons.xml
    ├── addons.xml.md5
    ├── repository.sandwichfarm/
    │   ├── addon.xml
    │   ├── icon.png
    │   └── repository.sandwichfarm-1.0.0.zip
    └── plugin.audio.subsonic/
        ├── addon.xml
        ├── icon.png
        ├── fanart.jpg
        ├── changelog-2.1.0.txt
        └── plugin.audio.subsonic-2.1.0.zip
```

**Rationale:**
- `repository.sandwichfarm/` committed to `main`: repo-addon source is hand-authored, versioned normally
- `plugins.json` in `main`: the machine-readable plugin registry, the only file that needs editing to onboard a new plugin
- `gh-pages` branch: entirely generated output; never hand-edited; re-created on each successful build
- `tools/generate.py`: the publisher logic, kept local so it can be run manually during development

---

## Suggested Build Order

Dependencies between components drive this order:

1. **Repo Addon (`repository.sandwichfarm/addon.xml`)** — must be authored first because it declares the HTTPS endpoint URLs. You cannot build anything else until you know where the host will live (GitHub Pages URL). This also validates Kodi can see the repository at all.

2. **Host (GitHub Pages setup)** — configure the repo and Pages settings so the HTTPS URL in the repo-addon's `addon.xml` is live. Verify with a placeholder `addons.xml`.

3. **Publisher Pipeline (GitHub Actions + `generate.py` + `plugins.json`)** — build the automation that fetches plugin sources and assembles the index. Test manually (run `generate.py` locally, push to gh-pages, verify Kodi sees the index).

4. **Plugin Onboarding (`plugin.audio.subsonic`)** — add the first plugin to `plugins.json`, run the pipeline, verify the full end-to-end flow: install repo addon → browse repo in Kodi → install plugin → release new version → Kodi auto-updates.

5. **Cross-repo trigger** — add `repository_dispatch` to `plugin.audio.subsonic`'s release workflow and wire it to this repo. This is the last step because it requires the pipeline to be proven working first.

---

## Single-Plugin vs. N-Plugin Design

**Design for N from day one.** The overhead is minimal and the payoff is high:

| Decision | Single-plugin shortcut | N-plugin design | Cost of shortcut |
|----------|----------------------|-----------------|-----------------|
| Plugin registry | Hard-code plugin ID in script | `plugins.json` manifest | Rewrite when plugin 2 ships |
| addons.xml generation | Hand-edit file | Script iterates manifest | Hand-edits break on every release |
| Publisher pipeline | Special-case fetch URL | Loop over manifest entries | Refactor under pressure |
| Repo-addon `addon.xml` | Hard-coded version bump | Versioned normally | No real difference |

The `plugins.json` + loop approach adds ~10 lines of code and saves a rewrite later. The stated requirement — "make adding a new plugin a low-friction, repeatable process" — implies N-plugin design is the correct shape even at day one.

---

## Architectural Patterns

### Pattern 1: Separate `main` and `gh-pages` branches

**What:** Source lives on `main`; generated output is force-pushed to `gh-pages`. GitHub Pages serves `gh-pages`.

**When to use:** Always, for a publisher repo. Generated ZIPs and XML are binary/auto-generated and do not belong in the source history.

**Trade-offs:** History of `gh-pages` is not meaningful (ephemeral); `main` history stays clean. Slightly more complex Actions setup (need to push to a different branch). Worth it.

### Pattern 2: `plugins.json` as the single source of truth for plugin registry

**What:** One JSON file declares which upstream repos are included. The pipeline reads it; humans edit only this file to add/remove plugins.

**When to use:** Always for external-repo-fetch pattern.

**Trade-offs:** Requires the pipeline to handle fetching, error cases, and version pinning. Simple JSON is more maintainable than configuration inside the workflow YAML itself.

### Pattern 3: Idempotent publisher script

**What:** `generate.py` can be run locally and produces the same output as CI. No state is kept between runs other than what's in the git history.

**When to use:** Always. You need to be able to test locally before pushing.

**Trade-offs:** Requires GitHub token available locally for API fetches (use a `.env` or env var; do not commit).

---

## Anti-Patterns

### Anti-Pattern 1: Committing generated ZIPs to `main`

**What people do:** Commit `plugin.audio.subsonic-2.1.0.zip` directly to the main branch.

**Why it's wrong:** Git history bloats rapidly with binary files. Each release doubles the stored size. PRs become noisy. `git clone` becomes slow.

**Do this instead:** Generate ZIPs in CI; push only to `gh-pages`; treat `gh-pages` as a deployment artifact, not a source branch.

### Anti-Pattern 2: Manually editing `addons.xml`

**What people do:** Edit `addons.xml` by hand to add a new version line.

**Why it's wrong:** Error-prone, forgetting to update `addons.xml.md5` is a common mistake (Kodi never sees the update). Breaks the automation requirement.

**Do this instead:** `generate.py` always rewrites the full `addons.xml` from scratch by parsing each plugin's `addon.xml`. The MD5 is always regenerated in the same script.

### Anti-Pattern 3: Putting the repo-addon ZIP at an unstable URL

**What people do:** The user-facing install URL changes when they rename branches or repos.

**Why it's wrong:** Every documentation page and user instruction becomes stale. Users with existing installs cannot find the repo-addon ZIP.

**Do this instead:** Use a custom domain (Cloudflare Pages or GitHub Pages custom domain) or commit to a stable GitHub username/repo name before publishing the install URL widely.

### Anti-Pattern 4: Flat directory (not using `<dir>` wrapper)

**What people do:** Use the pre-Nexus flat format with `<info>`, `<checksum>`, `<datadir>` directly under `<extension point="xbmc.addon.repository">`.

**Why it's wrong:** Kodi Nexus (v20) removed support for this format. `plugin.audio.subsonic` targets current Kodi; users will have Nexus or Omega.

**Do this instead:** Always use the `<dir>` wrapper element.

---

## Integration Points

### External Services

| Service | Integration Pattern | Notes |
|---------|---------------------|-------|
| GitHub Releases API | GH Actions fetches release ZIP via `gh release download` or API | Requires `GITHUB_TOKEN`; public repos use the default Actions token |
| GitHub Pages | Push to `gh-pages` branch; Pages auto-deploys | Free; HTTPS included; latency ~1-2 min post-push |
| plugin.audio.subsonic repo | `repository_dispatch` event from plugin's release workflow | Requires a Personal Access Token stored as a secret in this repo |

### Internal Boundaries

| Boundary | Communication | Notes |
|----------|---------------|-------|
| `main` → `gh-pages` | GH Actions force-push | Never manually edit `gh-pages` |
| `plugins.json` → `generate.py` | File read at build time | JSON schema should be validated in CI |
| repo-addon `addon.xml` → host URL | Hard-coded HTTPS URL | Changing this URL requires bumping repo-addon version to force Kodi refresh |
| `generate.py` → GitHub API | REST API or `gh` CLI | Rate limit: 5000 req/hr for authenticated requests; not a concern for this use case |

---

## Scaling Considerations

| Scale | Architecture Adjustments |
|-------|--------------------------|
| 1 plugin (now) | Exactly as described above — no changes needed |
| 2-10 plugins | Add entries to `plugins.json`; pipeline scales with no structural changes |
| 10+ plugins | Build time increases (more API fetches); consider caching release assets in Actions; still no architectural change |
| High download traffic | GitHub Pages CDN handles it; no change needed until hitting Pages limits (100GB/month soft cap) |
| Pages bandwidth limit hit | Mirror to Cloudflare Pages or R2 (free tier); update `datadir` URL in repo-addon and bump version |

---

## Sources

- [Add-on repositories — Official Kodi Wiki](https://kodi.wiki/view/Add-on_repositories) (MEDIUM confidence — wiki, official)
- [Addon.xml — Official Kodi Wiki](https://kodi.wiki/view/Addon.xml) (MEDIUM confidence — wiki, official)
- [Repository.cpp — xbmc/xbmc (source of truth for polling behavior)](https://github.com/xbmc/xbmc/blob/master/xbmc/addons/Repository.cpp) (HIGH confidence — Kodi source code)
- [repository.xbmc.org/addon.xml — official repo-addon reference](https://github.com/xbmc/xbmc/blob/master/addons/repository.xbmc.org/addon.xml) (HIGH confidence — official reference implementation)
- [drinfernoo/repository.example — canonical community example](https://github.com/drinfernoo/repository.example) (MEDIUM confidence — widely cited community template)
- [JonathanHolvey/kodi-repo-updater — webhook-driven cross-repo pattern](https://github.com/JonathanHolvey/kodi-repo-updater) (MEDIUM confidence — demonstrates release-event trigger pattern)
- [dot-Justin/kodi-repo — GH Actions live example](https://github.com/dot-Justin/kodi-repo) (MEDIUM confidence — modern GH Actions example)

---

*Architecture research for: Kodi addon repository (static distribution endpoint)*
*Researched: 2026-04-29*
