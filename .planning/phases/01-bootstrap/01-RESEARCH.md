# Phase 1: Bootstrap - Research

**Researched:** 2026-04-29
**Domain:** Kodi addon repository — manual first-publish on GitHub Pages
**Confidence:** HIGH (core protocol verified against xbmc/xbmc source; file layout and ZIP rules cross-verified against multiple live repos and official wiki)

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

- Addon id: `repository.sandwichfarm`, version `1.0.0`, provider-name `sandwichfarm`
- Hosting: GitHub Pages, project-page form, source = `gh-pages` branch root. `main` stays source-only; `gh-pages` is fully generated output.
- Base URL: `https://sandwichfarm.github.io/repository.sandwichfarm/`
- No custom domain in v1.
- Repo-addon ZIP lives at the repo root: `…/repository.sandwichfarm-1.0.0.zip`. Single canonical URL, no version-subdir indirection.
- Checksum: SHA-256 primary (`<checksum verify="sha256">` pointing at `addons.xml.sha256`); MD5 emitted alongside (`addons.xml.md5`) for backward compatibility. Both regenerated atomically in the same generator run.
- Plugin source for first publish: clone `sandwichfarm/plugin.audio.subsonic` locally and zip from HEAD. Published version follows upstream `addon.xml` (currently `3.1.0`). No artificial bump.
- Plugin ZIP and all generated artifacts committed to `gh-pages` branch only. `main` never carries binaries.
- `tools/generate.py` authored in Phase 1 — locally runnable, Python 3 stdlib only (`hashlib`, `zipfile`, `xml.etree.ElementTree`).
- `<dir>` wrapper element in repo addon `addon.xml` (required for Kodi Nexus 20+).
- `addons.xml`: UTF-8, no BOM, `\n` line endings.
- `changelog-3.1.0.txt` filename version MUST match published ZIP version exactly.

### Claude's Discretion

- Exact wordmark / fanart aesthetic for the repo addon's placeholder art.
- Internal directory layout under `gh-pages` beyond the canonical `<id>/<id>-<ver>.zip` path.
- Specific phrasing of the in-`addon.xml` `<summary>` / `<description>` for `repository.sandwichfarm`.
- Exact shape of `plugins.json` (Phase 2 may iterate; Phase 1 only needs to stub it).

### Deferred Ideas (OUT OF SCOPE)

- GitHub Actions workflow / `repository_dispatch` cross-repo trigger — Phase 2/3.
- CI validation suite (ZIP nesting check, BOM check, checksum match check, smoke-tests) — Phase 2.
- End-user install README with Android / Fire TV paths and verification step — Phase 3.
- Multi-Kodi-version `<dir minversion>` branching — out of v1 scope.
- Real wordmark / fanart artwork beyond placeholder — out of scope for now.
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| REPO-01 | Wrapper addon `repository.sandwichfarm` with hand-authored `addon.xml` declaring `xbmc.addon.repository` extension and `<dir>` wrapper | Section: Repo Addon addon.xml Exact Shape |
| REPO-02 | `<dir>` block declares `<info>`, `<checksum verify="sha256">`, and `<datadir zip="true">` URLs | Section: Repo Addon addon.xml Exact Shape |
| REPO-03 | Repo addon packaged as `repository.sandwichfarm-1.0.0.zip` with top-level directory exactly `repository.sandwichfarm/` | Section: ZIP Packaging |
| REPO-04 | Repo addon ZIP reachable at stable HTTPS URL | Section: GitHub Pages Setup |
| IDX-01 | `addons.xml` published at base URL, UTF-8 no BOM, `\n` endings | Section: Generator Script Shape; Pitfall: BOM/CRLF |
| IDX-02 | `addons.xml.sha256` regenerated atomically with `addons.xml` | Section: Generator Script Shape |
| IDX-03 | `addons.xml.md5` published alongside for backward compat | Section: Generator Script Shape |
| IDX-04 | Plugin ZIP at canonical path `<base>/<addon.id>/<addon.id>-<version>.zip` | Section: gh-pages File Layout |
| IDX-05 | Per-plugin `icon.png` (512×512) and `fanart.jpg` (1920×1080) | Section: Artwork |
| IDX-06 | `changelog-3.1.0.txt` filename version matches ZIP version | Section: gh-pages File Layout |
| HOST-01 | Static HTTPS from GitHub Pages | Section: GitHub Pages Setup |
| HOST-02 | Generated artifacts on `gh-pages` branch, not `main` | Section: GitHub Pages Setup |
| HOST-03 | All three endpoint URLs return HTTP 200 to fresh client | Section: Smoke Test Procedure |
| PLUG-01 | `plugin.audio.subsonic` listed in `plugins.json` and published | Section: Generator Script Shape |
| PLUG-02 | Kodi user who installs repo addon can install `plugin.audio.subsonic` from browser | Section: Smoke Test Procedure |
</phase_requirements>

<research_summary>
## Summary

This phase establishes the minimal artifacts a Kodi user needs to add `repository.sandwichfarm` as a source and install `plugin.audio.subsonic` — all produced locally and pushed by hand. The Kodi repository protocol is static-file-based and fully deterministic: three URLs in the repo-addon's `addon.xml` (info, checksum, datadir) drive everything. The file layout, XML schema, and ZIP packaging rules are verified against `xbmc/xbmc/Repository.cpp` and multiple live community repositories.

The critical ordering constraint: the GitHub Pages URL must be confirmed live before it is hard-coded into `repository.sandwichfarm/addon.xml` and the repo-addon ZIP is built. Changing these three URLs after the ZIP is published requires users to reinstall the repo addon — it is the strictest integration contract in the project. Everything else (the generator script, the plugin ZIP, the index files) can be regenerated and replaced without user action.

The dominant Phase 1 risks are all in the silent-failure class: ZIP with wrong directory nesting, BOM bytes in `addons.xml`, checksum files not regenerated atomically, or a GitHub Pages 404 that Kodi silently ignores. Each risk has a concrete manual verification step that can be run before declaring Phase 1 complete.

**Primary recommendation:** Create the `gh-pages` branch and confirm the base URL returns HTTP 200 first. Then author `repository.sandwichfarm/addon.xml` with the locked-in URLs. Then run `tools/generate.py` locally to produce all artifacts. Then push to `gh-pages` and run the smoke test sequence. Do not build the ZIP before the URL is confirmed live.
</research_summary>

<standard_stack>
## Standard Stack

### Core

| Tool / Library | Version | Purpose | Why Standard |
|----------------|---------|---------|--------------|
| Python 3 stdlib | 3.x (any) | Generator runtime | `hashlib`, `zipfile`, `xml.etree.ElementTree` — zero external deps; the canonical choice for all community Kodi generator scripts |
| GitHub Pages | free tier | Static HTTPS hosting | De-facto host for personal Kodi repos; Fastly CDN; auto-HTTPS; 1 GB storage / 100 GB/month bandwidth soft limits |
| `zipfile.ZipFile` (stdlib) | built-in | ZIP creation with correct arcname | Allows explicit control of arcname so top-level directory is always `<addon_id>/` |
| `hashlib` (stdlib) | built-in | SHA-256 and MD5 generation | Both digests from one import |
| `xml.etree.ElementTree` (stdlib) | built-in | Parse plugin `addon.xml`, assemble `addons.xml` | No pip installs in CI or locally |
| ImageMagick 7 | 7.1.2-15 (installed) | Placeholder artwork generation (one-time) | `magick` on PATH; confirmed installed; generates 512×512 PNG and 1920×1080 JPEG from command line |

### Supporting (Phase 1 only)

| Tool | Purpose | When to Use |
|------|---------|-------------|
| `git` | Branch management, pushing to `gh-pages` | Creating and populating the `gh-pages` branch |
| `gh` CLI | GitHub repo creation, Pages settings via API | Configuring Pages source without UI if preferred |
| `curl` | Manual smoke tests | Verifying HTTP 200 on all three endpoint URLs |
| `unzip -l` | ZIP structure verification | Checking top-level directory is exactly `repository.sandwichfarm/` |

### Alternatives Considered

| Standard Choice | Alternative | Tradeoff |
|-----------------|-------------|----------|
| Python stdlib only | Pillow for artwork | Pillow is installed (12.1.1) and could generate placeholder art programmatically, but artwork is a one-time manual task — ImageMagick is simpler for one-shot image creation; Pillow would be valid if pre-installing dependencies in generate.py is acceptable |
| `zipfile.ZipFile` with explicit arcname | `subprocess zip` CLI | Both work; `zipfile` avoids shell quoting pitfalls and works identically on Windows/Linux/macOS |
| drinfernoo `_repo_generator.py` shape | chadparry `create_repository.py` | chadparry last updated 2022 and adds GitPython dep; drinfernoo pattern is simpler and stdlib-only |

**Installation (nothing to install — stdlib only):**

```bash
python3 --version   # any 3.x works
magick --version    # ImageMagick 7 — confirmed present for artwork generation
```
</standard_stack>

<architecture_patterns>
## Architecture Patterns

### Exact `gh-pages` Branch File Layout

All paths are relative to the root of the `gh-pages` branch. This is what GitHub Pages serves at `https://sandwichfarm.github.io/repository.sandwichfarm/`.

```
gh-pages branch root/
├── .nojekyll                                         # REQUIRED — prevents Jekyll from mangling binary ZIPs
├── addons.xml                                        # IDX-01: master index (UTF-8, no BOM, \n endings)
├── addons.xml.sha256                                 # IDX-02: sha256 hex digest of addons.xml
├── addons.xml.md5                                    # IDX-03: md5 hex digest of addons.xml
├── repository.sandwichfarm-1.0.0.zip                # REPO-03/04: user installs this once
├── repository.sandwichfarm/                          # repo-addon loose files (served for Kodi's artdir)
│   ├── addon.xml                                     # repo-addon metadata (copy, not the source)
│   ├── icon.png                                      # 512×512 repo icon
│   └── fanart.jpg                                    # 1920×1080 repo fanart
└── plugin.audio.subsonic/                            # IDX-04/05/06: one dir per plugin
    ├── addon.xml                                     # copy of plugin's addon.xml (Kodi reads this)
    ├── icon.png                                      # 512×512
    ├── fanart.jpg                                    # 1920×1080
    ├── changelog-3.1.0.txt                           # IDX-06: filename version MUST match ZIP version
    └── plugin.audio.subsonic-3.1.0.zip              # IDX-04: what Kodi downloads on install/update
```

**Kodi URL construction:** `<datadir>/<addon.id>/<addon.id>-<version>.zip`. With `<datadir>https://sandwichfarm.github.io/repository.sandwichfarm/</datadir>` (trailing slash), Kodi constructs `https://sandwichfarm.github.io/repository.sandwichfarm/plugin.audio.subsonic/plugin.audio.subsonic-3.1.0.zip`. This matches the layout above.

**Does Kodi need `index.html`?** No. Kodi fetches specific file paths (`addons.xml`, `addons.xml.sha256`, ZIP paths) — it does not browse directories. No `index.html` is required.

**Does `.nojekyll` matter?** YES. Without it, GitHub Pages runs Jekyll which silently strips files beginning with an underscore and can interfere with binary file serving. A `.nojekyll` file at the branch root bypasses Jekyll entirely. This is REQUIRED for serving ZIPs correctly. Source: GitHub Pages documentation, verified by multiple community reports. [MEDIUM confidence — behavior is well-documented but rarely flagged in Kodi-specific guides]

**Is the unpacked `addon.xml` needed alongside the ZIP?** YES. Kodi reads the loose `addon.xml` for display metadata (icon, description) and constructs the ZIP download URL from the version attribute it finds there. Both the ZIP and the loose `addon.xml` must be at the same `<addon_id>/` path.

### `main` Branch Layout (source only)

```
main branch root/
├── CLAUDE.md
├── .planning/                                        # planning artifacts only
├── repository.sandwichfarm/                          # repo-addon source (hand-authored)
│   ├── addon.xml                                     # THE source of truth for repo addon
│   ├── icon.png
│   └── fanart.jpg
├── plugins.json                                      # plugin registry stub
└── tools/
    └── generate.py                                   # local generator (stdlib only)
```

`main` never carries binaries. `gh-pages` is entirely generated output.

### Pattern: Exact `repository.sandwichfarm/addon.xml` Shape

This is the hand-authored source file on `main`. It declares the three load-bearing URLs and must be written before the repo-addon ZIP is built.

```xml
<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<addon id="repository.sandwichfarm"
       name="Sandwichfarm Repository"
       version="1.0.0"
       provider-name="sandwichfarm">
  <requires>
    <import addon="xbmc.addon" version="12.0.0"/>
  </requires>
  <extension point="xbmc.addon.repository" name="Sandwichfarm Repository">
    <dir>
      <info compressed="false">https://sandwichfarm.github.io/repository.sandwichfarm/addons.xml</info>
      <checksum verify="sha256">https://sandwichfarm.github.io/repository.sandwichfarm/addons.xml.sha256</checksum>
      <datadir zip="true">https://sandwichfarm.github.io/repository.sandwichfarm/</datadir>
    </dir>
  </extension>
  <extension point="xbmc.addon.metadata">
    <summary lang="en_GB">Sandwichfarm's personal Kodi addon repository</summary>
    <description lang="en_GB">Personal repository hosting sandwichfarm-authored Kodi plugins, starting with plugin.audio.subsonic.</description>
    <platform>all</platform>
    <assets>
      <icon>icon.png</icon>
      <fanart>fanart.jpg</fanart>
    </assets>
  </extension>
</addon>
```

**Exact attribute decisions (with sources):**

| Attribute / Element | Value | Rationale | Source |
|--------------------|-------|-----------|--------|
| `<checksum verify="sha256">` | Points at `addons.xml.sha256` | `verify="sha256"` is the modern value; the official `repository.xbmc.org/addon.xml` uses this exact form | xbmc/xbmc — repository.xbmc.org/addon.xml [HIGH] |
| `<datadir zip="true">` | Trailing slash: `…/repository.sandwichfarm/` | Kodi appends `<addon_id>/<addon_id>-<ver>.zip`; trailing slash on `<datadir>` avoids double-slash construction | Verified against Repository.cpp and five live repos [HIGH] |
| `<info compressed="false">` | Points at `addons.xml` (not `.gz`) | `compressed="false"` tells Kodi not to gunzip the response; GitHub Pages negotiates gzip transparently so the file on disk is plain XML | Community pattern, confirmed by drinfernoo template [MEDIUM] |
| `<requires><import addon="xbmc.addon" version="12.0.0"/>` | Floor version 12.0.0 | Safe minimum covering all current Kodi releases (Nexus 20+, Omega 21+); seen in sualfred's repo | Multiple live repos [MEDIUM] |
| No `<hashes>` element | Omitted | The `<hashes>` element controls per-ZIP hash verification (separate from the index checksum). Omitting it means Kodi does not attempt to verify individual ZIP digests. Acceptable for a personal repo. The official repo uses `<hashes>sha256</hashes>` — can be added in Phase 2. | repository.xbmc.org/addon.xml [HIGH] |

**What the official `repository.xbmc.org/addon.xml` looks like (verified live):**

```xml
<dir>
  <info>https://mirrors.kodi.tv/addons/piers/addons.xml.gz</info>
  <checksum verify="sha256">https://mirrors.kodi.tv/addons/piers/addons.xml.gz?sha256</checksum>
  <datadir>https://mirrors.kodi.tv/addons/piers</datadir>
  <artdir>https://mirrors.kodi.tv/addons/piers</artdir>
  <hashes>sha256</hashes>
</dir>
```

Key differences from our version: official uses `addons.xml.gz` (gzip); we use plain `addons.xml`. Official uses `<artdir>` (separate art CDN); we omit it (Kodi defaults `artdir` to `datadir`). Official includes `<hashes>sha256</hashes>` for per-ZIP verification; we omit for simplicity in Phase 1.

### Anti-Patterns to Avoid

- **Flat `<info>/<checksum>/<datadir>` directly under `<extension point="xbmc.addon.repository">` without `<dir>` wrapper:** Kodi Nexus 20+ removed support for the pre-Nexus flat format. The linuxserver/libreelec-addons GitHub issue #50 documents exactly this failure mode. All new repos MUST use the `<dir>` wrapper.
- **MD5 only, no SHA-256:** The Kodi source (Repository.cpp) logs MD5 as deprecated and "will only guard against unintentional data corruption." Using `verify="sha256"` is the correct modern form.
- **Trailing slash absent from `<datadir>`:** If `<datadir>` lacks a trailing slash, Kodi constructs `…/repository.sandwichfarmaddon.id/…` (double path). Always include the trailing slash.
- **Committing ZIPs to `main`:** Git history bloat from binary files. Use `gh-pages` branch exclusively for generated artifacts.
- **`raw.githubusercontent.com` URLs in `<datadir>`:** Aggressive CDN caching; a freshly pushed ZIP may not be visible for minutes to hours; no custom domain; rate-limit risk. Use GitHub Pages URLs exclusively.
</architecture_patterns>

<dont_hand_roll>
## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| ZIP `arcname` prefix | Custom path-string manipulation | `zipfile.ZipFile.write(src, arcname=addon_id + '/' + rel_path)` | The arcname argument explicitly sets the in-ZIP path; no working-directory tricks needed; platform-independent |
| SHA-256 and MD5 simultaneously | Two separate passes over the file | `hashlib.sha256(data)` and `hashlib.md5(data)` on the same `data = open(..., 'rb').read()` | One read, two digests; avoids race between file write and hash read |
| XML assembly of `addons.xml` | String concatenation | `xml.etree.ElementTree.parse()` to read each `addon.xml`, then extract the `<addon>` element and write all into a new `<addons>` root | Handles encoding, escaping, declaration correctly; matches the drinfernoo/chadparry generator pattern |
| Artwork generation | Python script (generate.py) | `magick` CLI one-shot (one-time task, not in generate.py) | generate.py must be stdlib-only; artwork is a commit-once asset; no need to regenerate programmatically |
| GitHub Pages branch setup | Manual git operations | `git checkout --orphan gh-pages && git rm -rf .` | Orphan branch avoids carrying main's history into the Pages branch |

**Key insight:** The entire generator is fewer than 100 lines of Python stdlib. Resist adding dependencies — the Phase 2 CI will run this exact script and any dependency becomes a CI setup step.
</dont_hand_roll>

<common_pitfalls>
## Common Pitfalls

### Pitfall 1: ZIP nesting — wrong working directory produces wrong top-level path

**What goes wrong:** Kodi unpacks the ZIP and expects `addon.xml` at `repository.sandwichfarm/addon.xml`. If `generate.py` zips from inside the addon directory, the ZIP has a flat layout (no top-level folder). If it zips from two levels above, it double-nests (`repository.sandwichfarm/repository.sandwichfarm/addon.xml`).

**Why it happens:** Developers use `zip -r` or `os.walk()` from the wrong directory. The `zipfile.ZipFile.write(src)` call uses the `src` path as the arcname by default — so `zip.write("repository.sandwichfarm/addon.xml")` produces the correct layout, but `zip.write("addon.xml")` from inside the directory produces flat.

**How to avoid:** Always use explicit arcname in `zipfile.ZipFile.write()`:

```python
# Source: chadparry/create_repository.py pattern + drinfernoo/_repo_generator.py analysis
import zipfile, os

addon_id = "repository.sandwichfarm"
addon_src_dir = "repository.sandwichfarm"  # relative to repo root on main branch
output_zip = "repository.sandwichfarm-1.0.0.zip"

with zipfile.ZipFile(output_zip, "w", compression=zipfile.ZIP_DEFLATED) as zf:
    for root, dirs, files in os.walk(addon_src_dir):
        # Exclude dev artifacts
        dirs[:] = [d for d in dirs if d not in {".git", "__pycache__", ".mypy_cache"}]
        for fname in files:
            if fname.endswith(".pyc"):
                continue
            full_path = os.path.join(root, fname)
            # arcname: replace addon_src_dir prefix with addon_id (same, but explicit)
            arcname = os.path.join(addon_id, os.path.relpath(full_path, addon_src_dir))
            zf.write(full_path, arcname)
```

**Warning signs:** `unzip -l repository.sandwichfarm-1.0.0.zip | head -5` shows either `addon.xml` at root (flat — no directory) or `repository.sandwichfarm/repository.sandwichfarm/addon.xml` (double-nested). Correct output shows `repository.sandwichfarm/addon.xml` as the first entry.

---

### Pitfall 2: Checksum files not regenerated atomically — Kodi sees no update

**What goes wrong:** `addons.xml` is updated but `addons.xml.sha256` (or `addons.xml.md5`) still contains the old digest. Kodi fetches the checksum first; if it matches what it cached, it skips re-fetching `addons.xml` entirely. Users never see the new version. Kodi logs: `"checksum not changed"`.

**Why it happens:** Regenerating the checksums in a separate script step, separate commit, or forgetting to run the generator after editing `addons.xml` manually.

**How to avoid:** Always write both checksum files inside the same function call, immediately after writing `addons.xml`, in the same generator run. In `tools/generate.py`:

```python
# Source: drinfernoo/_repo_generator.py pattern — adapted for SHA-256 primary
import hashlib

def write_index_and_checksums(addons_xml_content: str, output_dir: str) -> None:
    xml_bytes = addons_xml_content.encode("utf-8")
    
    xml_path = os.path.join(output_dir, "addons.xml")
    with open(xml_path, "w", encoding="utf-8", newline="\n") as f:
        f.write(addons_xml_content)
    
    sha256_digest = hashlib.sha256(xml_bytes).hexdigest()
    with open(os.path.join(output_dir, "addons.xml.sha256"), "w", encoding="utf-8", newline="\n") as f:
        f.write(sha256_digest + "\n")
    
    md5_digest = hashlib.md5(xml_bytes).hexdigest()
    with open(os.path.join(output_dir, "addons.xml.md5"), "w", encoding="utf-8", newline="\n") as f:
        f.write(md5_digest + "\n")
```

Never commit `addons.xml` without committing the freshly written `addons.xml.sha256` and `addons.xml.md5` in the same git commit.

**Warning signs:** The `addons.xml.sha256` file has an older mtime than `addons.xml`. Installed Kodi addon version does not advance even after pushing a new ZIP.

---

### Pitfall 3: BOM bytes or CRLF in `addons.xml` — Kodi silently parses zero addons

**What goes wrong:** If `addons.xml` starts with a UTF-8 BOM (`\xef\xbb\xbf`), Kodi's XML parser fails. The repository appears to install, but the addon list is empty. CRLF (`\r\n`) line endings produce the same class of silent failure.

**Why it happens:** Python's `open()` with `encoding='utf-8-sig'` emits BOM. `xml.etree.ElementTree.write(encoding='UTF-8')` writes a BOM in some Python versions. CRLF happens when the file is written on Windows without `newline='\n'`.

**How to avoid:** Always write with `encoding='utf-8'` (not `'utf-8-sig'`) and `newline='\n'`. Write the XML declaration manually as the first line (ElementTree's declaration handling is inconsistent across Python versions):

```python
with open("addons.xml", "w", encoding="utf-8", newline="\n") as f:
    f.write('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n')
    f.write("<addons>\n")
    for addon_xml_content in all_addon_xmls:
        f.write(addon_xml_content)
    f.write("</addons>\n")
```

**Manual verification:** `python3 -c "d=open('addons.xml','rb').read(3); assert d != b'\xef\xbb\xbf', 'BOM detected'; print('OK')"`. Also `xxd addons.xml | head -1` — first three hex bytes must NOT be `ef bb bf`.

**Warning signs:** Repository installs with no error but Kodi's addon browser shows zero addons from it.

---

### Pitfall 4: GitHub Pages 404 cached at CDN edge — not visible in curl

**What goes wrong (first-publish specific):** On the very first push to `gh-pages`, GitHub's Fastly CDN may cache a 404 for the domain for 5–10 minutes. Curl shows 404; a retry 2 minutes later shows 200. Kodi, queried in this window, also gets 404 and logs `"Could not connect to repository"` — even though the files exist in the branch.

**Why it happens:** CDN edge nodes cache responses (including 404s) before the Pages deployment fully propagates. First deploy has no warm cache — every edge node must be primed.

**How to avoid:** After the first push to `gh-pages` and GitHub Pages reports "Your site is ready at …", wait at least 2 minutes before running smoke tests. If curl returns 404, wait and retry rather than assuming setup is wrong. GitHub Pages documentation cites up to 10 minutes for first-publish propagation; in practice 30–90 seconds is typical for confirmed changes, but initial 404 caching can delay the first 200 response.

**Warning signs:** GitHub Pages Settings shows "Your site is published at …" but `curl -fsSI https://sandwichfarm.github.io/repository.sandwichfarm/addons.xml` returns 404. Symptom resolves within 10 minutes without any further action.

---

### Pitfall 5: Kodi caches the repo addon's own `addon.xml` — force-update required after first install

**What goes wrong (first-publish specific):** After a user installs `repository.sandwichfarm-1.0.0.zip`, Kodi caches the repo's `addons.xml` and does not automatically re-fetch it. If you push a corrected `addons.xml` shortly after the first install (e.g., to fix a typo in the plugin version), Kodi on the user's machine will not see the change until the next 24-hour poll cycle — or until the user manually triggers "Check for updates" from Kodi's addon manager.

**Why it happens:** Kodi's polling is checksum-gated and time-gated (default 24h). It will not re-fetch `addons.xml` until either the poll interval elapses or the user forces a check.

**How to avoid (for testing during Phase 1):** After every push to `gh-pages`, force-trigger an update in Kodi: Settings > Add-ons > Manage add-ons (or select the repo in the add-on manager) > "Check for updates." The checksum file changing is the trigger — Kodi compares the current `addons.xml.sha256` against its cached copy and fetches fresh `addons.xml` only if the checksum changed. This is why the checksum file MUST change even for a minor tweak to `addons.xml`.

**Warning signs:** Kodi shows old plugin version after you published a new one; Kodi log shows `"checksum not changed"`.

---

### Pitfall 6: The flat `<info>/<checksum>/<datadir>` format (no `<dir>`) — Kodi Nexus 20+ silent fail

**What goes wrong:** Kodi Nexus (20.x) removed support for the pre-Nexus flat format where `<info>`, `<checksum>`, `<datadir>` appear directly under `<extension point="xbmc.addon.repository">` without a `<dir>` wrapper. The repo installs without error but Kodi cannot find any addons in it.

**Why it happens:** Copying a template from an older repository that predates Nexus. The linuxserver/libreelec-addons GitHub issue #50 documents exactly this failure — the error message from Kodi is `"uses old schema definition for the repository extension point"`.

**How to avoid:** Always use the `<dir>` wrapper. The correct shape:

```xml
<extension point="xbmc.addon.repository" name="Sandwichfarm Repository">
  <dir>
    <info compressed="false">…</info>
    <checksum verify="sha256">…</checksum>
    <datadir zip="true">…</datadir>
  </dir>
</extension>
```

**Warning signs:** Kodi log contains `"uses old schema definition"`. Repository shows as installed but has no addons listed under it.
</common_pitfalls>

<code_examples>
## Code Examples

### Generator Script (`tools/generate.py`) — Concrete Shape

This is the full function structure for a Phase 1 stdlib-only generator. It is adapted from the drinfernoo `_repo_generator.py` and chadparry `create_repository.py` patterns with SHA-256 primary checksum added.

```python
#!/usr/bin/env python3
"""
tools/generate.py — Kodi repository generator (Phase 1: local/manual)
Stdlib only: hashlib, zipfile, xml.etree.ElementTree, os, shutil, json

Usage:
  python3 tools/generate.py --plugin-src /path/to/plugin.audio.subsonic \
                             --output /tmp/gh-pages-staging
"""
import argparse
import hashlib
import json
import os
import shutil
import zipfile
import xml.etree.ElementTree as ET

# --- Config (could also come from plugins.json) ---
REPO_ADDON_ID   = "repository.sandwichfarm"
REPO_ADDON_VER  = "1.0.0"

IGNORES = {".git", "__pycache__", ".mypy_cache", ".pytest_cache", "*.pyc"}


def should_exclude(name: str) -> bool:
    import fnmatch
    for pattern in IGNORES:
        if fnmatch.fnmatch(name, pattern):
            return True
    return False


def make_zip(addon_src_dir: str, addon_id: str, addon_ver: str, output_dir: str) -> str:
    """
    Package addon_src_dir into <output_dir>/<addon_id>/<addon_id>-<addon_ver>.zip
    Top-level directory in ZIP is always <addon_id>/.
    Returns the absolute path to the created ZIP.
    """
    zip_dir = os.path.join(output_dir, addon_id)
    os.makedirs(zip_dir, exist_ok=True)
    zip_path = os.path.join(zip_dir, f"{addon_id}-{addon_ver}.zip")

    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for root, dirs, files in os.walk(addon_src_dir):
            # Prune excluded dirs in-place so os.walk does not descend into them
            dirs[:] = [d for d in dirs if not should_exclude(d)]
            for fname in files:
                if should_exclude(fname):
                    continue
                full_path = os.path.join(root, fname)
                # arcname always starts with addon_id/ so top-level dir is correct
                rel = os.path.relpath(full_path, addon_src_dir)
                arcname = os.path.join(addon_id, rel)
                zf.write(full_path, arcname)

    return zip_path


def read_addon_xml(addon_src_dir: str) -> ET.Element:
    """Parse and return the <addon> root element from addon_src_dir/addon.xml."""
    tree = ET.parse(os.path.join(addon_src_dir, "addon.xml"))
    return tree.getroot()


def copy_addon_assets(addon_src_dir: str, addon_id: str, output_dir: str) -> None:
    """Copy addon.xml, icon.png, fanart.jpg, changelog-*.txt to output_dir/<addon_id>/."""
    dest = os.path.join(output_dir, addon_id)
    os.makedirs(dest, exist_ok=True)
    for fname in os.listdir(addon_src_dir):
        if fname in ("addon.xml", "icon.png", "fanart.jpg") or fname.startswith("changelog-"):
            shutil.copy2(os.path.join(addon_src_dir, fname), os.path.join(dest, fname))


def build_addons_xml(addon_elements: list) -> str:
    """
    Assemble addons.xml from a list of <addon> ET.Elements.
    Returns a UTF-8 string with no BOM, \n line endings, XML declaration on line 1.
    """
    lines = ['<?xml version="1.0" encoding="UTF-8" standalone="yes"?>', "<addons>"]
    for elem in addon_elements:
        # ET.tostring with encoding='unicode' gives a str without BOM or declaration
        lines.append("  " + ET.tostring(elem, encoding="unicode"))
    lines.append("</addons>")
    return "\n".join(lines) + "\n"


def write_index_and_checksums(content: str, output_dir: str) -> None:
    """Write addons.xml, addons.xml.sha256, addons.xml.md5 atomically."""
    xml_bytes = content.encode("utf-8")

    # Verify no BOM leaked in
    assert not xml_bytes.startswith(b"\xef\xbb\xbf"), "BOM detected — check encoding"

    with open(os.path.join(output_dir, "addons.xml"), "w", encoding="utf-8", newline="\n") as f:
        f.write(content)
    with open(os.path.join(output_dir, "addons.xml.sha256"), "w", encoding="utf-8", newline="\n") as f:
        f.write(hashlib.sha256(xml_bytes).hexdigest() + "\n")
    with open(os.path.join(output_dir, "addons.xml.md5"), "w", encoding="utf-8", newline="\n") as f:
        f.write(hashlib.md5(xml_bytes).hexdigest() + "\n")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--plugin-src", required=True,
                        help="Path to cloned plugin.audio.subsonic source directory")
    parser.add_argument("--repo-addon-src", default="repository.sandwichfarm",
                        help="Path to repo addon source directory (default: ./repository.sandwichfarm)")
    parser.add_argument("--output", required=True,
                        help="Output directory (becomes gh-pages branch root)")
    args = parser.parse_args()

    os.makedirs(args.output, exist_ok=True)

    # Create .nojekyll
    open(os.path.join(args.output, ".nojekyll"), "w").close()

    addon_elements = []

    # 1. Process repo addon
    repo_elem = read_addon_xml(args.repo_addon_src)
    addon_elements.append(repo_elem)
    copy_addon_assets(args.repo_addon_src, REPO_ADDON_ID, args.output)
    make_zip(args.repo_addon_src, REPO_ADDON_ID, REPO_ADDON_VER, args.output)
    # Move repo ZIP from <output>/repository.sandwichfarm/ to <output>/ (root)
    zip_in_subdir = os.path.join(args.output, REPO_ADDON_ID,
                                 f"{REPO_ADDON_ID}-{REPO_ADDON_VER}.zip")
    zip_at_root = os.path.join(args.output, f"{REPO_ADDON_ID}-{REPO_ADDON_VER}.zip")
    shutil.move(zip_in_subdir, zip_at_root)

    # 2. Process each plugin
    plugin_src = args.plugin_src
    plugin_elem = read_addon_xml(plugin_src)
    plugin_id  = plugin_elem.get("id")    # e.g. "plugin.audio.subsonic"
    plugin_ver = plugin_elem.get("version")  # e.g. "3.1.0"
    addon_elements.append(plugin_elem)
    copy_addon_assets(plugin_src, plugin_id, args.output)
    make_zip(plugin_src, plugin_id, plugin_ver, args.output)

    # 3. Build and write index + checksums
    content = build_addons_xml(addon_elements)
    write_index_and_checksums(content, args.output)

    print(f"Generated: {args.output}")
    print(f"  addons.xml — {len(addon_elements)} addons")
    print(f"  addons.xml.sha256")
    print(f"  addons.xml.md5")
    print(f"  {REPO_ADDON_ID}-{REPO_ADDON_VER}.zip (at root)")
    print(f"  {plugin_id}/{plugin_id}-{plugin_ver}.zip")


if __name__ == "__main__":
    main()
```

**`plugins.json` stub (Phase 1 — minimal schema for Phase 2 to extend):**

```json
[
  {
    "id": "plugin.audio.subsonic",
    "repo": "sandwichfarm/plugin.audio.subsonic",
    "source": "local"
  }
]
```

Phase 2 will evolve this schema; Phase 1 only needs it to exist.

---

### Placeholder Artwork Generation (one-time, NOT in generate.py)

**Constraint:** `generate.py` is stdlib-only. Artwork generation uses ImageMagick (`magick` — confirmed installed at 7.1.2-15) and is a one-time manual step that produces committed assets.

```bash
# repo icon — 512×512 dark background, white text wordmark
magick -size 512x512 \
  -background "#1a1a2e" \
  -fill white \
  -gravity center \
  -font DejaVu-Sans-Bold \
  -pointsize 52 \
  label:"sandwichfarm\nrepository" \
  repository.sandwichfarm/icon.png

# repo fanart — 1920×1080 neutral dark gradient
magick -size 1920x1080 \
  gradient:"#1a1a2e-#16213e" \
  -fill white -gravity center \
  -font DejaVu-Sans-Bold \
  -pointsize 80 \
  -annotate 0 "sandwichfarm" \
  repository.sandwichfarm/fanart.jpg

# plugin icon — 512×512 (copy from upstream if icon.png exists in cloned repo)
# If upstream has icon.png, copy it. Otherwise generate placeholder:
magick -size 512x512 \
  -background "#0f3460" \
  -fill white -gravity center \
  -font DejaVu-Sans-Bold \
  -pointsize 48 \
  label:"plugin.audio\n.subsonic" \
  plugin.audio.subsonic/icon.png
```

Check whether upstream `plugin.audio.subsonic` already ships `icon.png` and `fanart.jpg` before generating placeholders — the upstream `addon.xml` declares `<icon>icon.png</icon>` and `<fanart>fanart.jpg</fanart>`, so these likely exist in the repo. [MEDIUM confidence — declared in addon.xml; need to verify files exist in HEAD]

---

### GitHub Pages Setup Procedure (concrete commands)

**Prerequisites:** GitHub repo `sandwichfarm/repository.sandwichfarm` must be public. `gh` CLI confirmed installed (2.87.3).

```bash
# Step 1: Create the GitHub repo if not already created
gh repo create sandwichfarm/repository.sandwichfarm --public --description "Kodi addon repository"

# Step 2: Push main branch with initial skeleton
git -C /home/sandwich/Develop/repository.sandwichfarm init
git -C /home/sandwich/Develop/repository.sandwichfarm add .
git -C /home/sandwich/Develop/repository.sandwichfarm commit -m "chore: initial project skeleton"
git -C /home/sandwich/Develop/repository.sandwichfarm remote add origin git@github.com:sandwichfarm/repository.sandwichfarm.git
git -C /home/sandwich/Develop/repository.sandwichfarm push -u origin main

# Step 3: Create gh-pages branch (orphan — no history from main)
git -C /home/sandwich/Develop/repository.sandwichfarm checkout --orphan gh-pages
git -C /home/sandwich/Develop/repository.sandwichfarm rm -rf .
echo "" > .nojekyll
git -C /home/sandwich/Develop/repository.sandwichfarm add .nojekyll
git -C /home/sandwich/Develop/repository.sandwichfarm commit -m "chore: init gh-pages branch"
git -C /home/sandwich/Develop/repository.sandwichfarm push -u origin gh-pages

# Step 4: Configure GitHub Pages to serve from gh-pages branch root
# Via gh CLI (Pages API):
gh api repos/sandwichfarm/repository.sandwichfarm/pages \
  --method POST \
  --field source='{"branch":"gh-pages","path":"/"}' \
  2>/dev/null || \
gh api repos/sandwichfarm/repository.sandwichfarm/pages \
  --method PUT \
  --field source='{"branch":"gh-pages","path":"/"}'

# Step 5: Verify Pages is enabled and URL is correct
gh api repos/sandwichfarm/repository.sandwichfarm/pages --jq '.html_url'
# Expected: "https://sandwichfarm.github.io/repository.sandwichfarm/"

# Step 6: Wait for first deployment (30–90s typical; up to 10 minutes on first publish)
# Poll until 200:
until curl -fsSI https://sandwichfarm.github.io/repository.sandwichfarm/.nojekyll 2>/dev/null | grep -q "200"; do
  echo "Waiting for Pages to go live..."; sleep 10
done
echo "GitHub Pages is live."

# Step 7: Switch back to main
git -C /home/sandwich/Develop/repository.sandwichfarm checkout main
```

**GitHub Pages UI alternative (if API fails):** Repository Settings > Pages > Build and deployment > Source: "Deploy from a branch" > Branch: "gh-pages" > Folder: "/" (root) > Save.

**Build complete indicator:** GitHub Pages Settings shows "Your site is live at https://sandwichfarm.github.io/repository.sandwichfarm/" with a green checkmark. GitHub also creates a deployment in the repo's Deployments section (visible at `github.com/sandwichfarm/repository.sandwichfarm/deployments`). Via CLI: `gh api repos/sandwichfarm/repository.sandwichfarm/pages --jq '.status'` returns `"built"`.

---

### Manual Publish Flow (after GitHub Pages is live)

```bash
# 1. Clone plugin source (if not already cloned locally)
git clone https://github.com/sandwichfarm/plugin.audio.subsonic.git /tmp/plugin.audio.subsonic

# 2. Run generate.py to produce all artifacts in a staging dir
python3 /home/sandwich/Develop/repository.sandwichfarm/tools/generate.py \
  --plugin-src /tmp/plugin.audio.subsonic \
  --repo-addon-src /home/sandwich/Develop/repository.sandwichfarm/repository.sandwichfarm \
  --output /tmp/gh-pages-staging

# 3. Switch to gh-pages branch and copy artifacts
git -C /home/sandwich/Develop/repository.sandwichfarm checkout gh-pages
cp -r /tmp/gh-pages-staging/. /home/sandwich/Develop/repository.sandwichfarm/
git -C /home/sandwich/Develop/repository.sandwichfarm add -A
git -C /home/sandwich/Develop/repository.sandwichfarm commit -m "publish: initial repo with plugin.audio.subsonic 3.1.0"
git -C /home/sandwich/Develop/repository.sandwichfarm push origin gh-pages

# 4. Switch back to main
git -C /home/sandwich/Develop/repository.sandwichfarm checkout main

# 5. Wait for deployment (~30–90 seconds), then run smoke tests
```

---

### Manual Smoke Test Procedure (Phase 1 success criteria verification)

Run these after pushing to `gh-pages` and waiting for deployment to settle (at least 60 seconds after the push):

```bash
BASE="https://sandwichfarm.github.io/repository.sandwichfarm"

# Test 1: addons.xml returns 200 and is UTF-8 XML
curl -fsSI "$BASE/addons.xml" | grep "HTTP/"
# Expected: HTTP/2 200

# Test 2: addons.xml.sha256 exists and looks like a hex digest
curl -fsS "$BASE/addons.xml.sha256"
# Expected: 64-character hex string (e.g. "a3f2d1c9b8e7f6...")

# Validate hex format
curl -fsS "$BASE/addons.xml.sha256" | xxd | head -3
# First few bytes should be ASCII hex chars, not binary

# Test 3: addons.xml.md5 exists and looks like a hex digest
curl -fsS "$BASE/addons.xml.md5"
# Expected: 32-character hex string

# Test 4: repo addon ZIP exists at root
curl -fsSI "$BASE/repository.sandwichfarm-1.0.0.zip" | grep "HTTP/"
# Expected: HTTP/2 200

# Test 5: plugin ZIP exists at canonical path
curl -fsSI "$BASE/plugin.audio.subsonic/plugin.audio.subsonic-3.1.0.zip" | grep "HTTP/"
# Expected: HTTP/2 200

# Test 6: Verify ZIP top-level directory is exactly "repository.sandwichfarm/"
curl -fsS "$BASE/repository.sandwichfarm-1.0.0.zip" -o /tmp/repo-test.zip
unzip -l /tmp/repo-test.zip | head -10
# Expected: first entry is "repository.sandwichfarm/"
# FAIL if: first entry is "addon.xml" (flat) or "repository.sandwichfarm/repository.sandwichfarm/" (double-nested)

# Test 7: Verify addons.xml has no BOM
curl -fsS "$BASE/addons.xml" | python3 -c "
import sys
data = sys.stdin.buffer.read()
assert not data.startswith(b'\xef\xbb\xbf'), 'FAIL: BOM detected'
assert b'\r' not in data, 'FAIL: CRLF detected'
print('OK: no BOM, no CRLF')
"

# Test 8: checksum consistency — sha256 in file matches addons.xml content
import hashlib
ADDONS=$(curl -fsS "$BASE/addons.xml")
STORED=$(curl -fsS "$BASE/addons.xml.sha256" | tr -d '\n')
COMPUTED=$(echo -n "$ADDONS" | sha256sum | awk '{print $1}')
# Note: shell sha256sum may differ from Python due to encoding; use Python:
python3 - <<'PY'
import urllib.request, hashlib
addons = urllib.request.urlopen("$BASE/addons.xml").read()
stored = urllib.request.urlopen("$BASE/addons.xml.sha256").read().decode().strip()
computed = hashlib.sha256(addons).hexdigest()
assert stored == computed, f"MISMATCH: stored={stored} computed={computed}"
print("OK: sha256 matches")
PY
```

**Kodi verification (minimum):**

1. In Kodi: Settings > System > Add-ons > "Unknown sources" → enable
2. Settings > File Manager > Add Network Location → enter `https://sandwichfarm.github.io/repository.sandwichfarm/` as Name and Address
3. Add-ons > Install from zip file → navigate to the sandwichfarm.github.io location → install `repository.sandwichfarm-1.0.0.zip`
4. Add-ons > Install from repository → "Sandwichfarm Repository" should appear → Music add-ons → `plugin.audio.subsonic` should be listed and installable

**Phase 1 success criteria mapping:**

| Criterion | Smoke Test | Pass condition |
|-----------|------------|----------------|
| HOST-03: all endpoint URLs return 200 | Tests 1, 4, 5 | `curl -fsSI` shows `HTTP/2 200` |
| IDX-01: addons.xml UTF-8 no BOM | Test 7 | "OK: no BOM, no CRLF" |
| IDX-02: addons.xml.sha256 correct | Test 8 | "OK: sha256 matches" |
| REPO-03: ZIP top-level dir correct | Test 6 | first `unzip -l` entry is `repository.sandwichfarm/` |
| PLUG-02: plugin installable from Kodi | Kodi steps 3–4 | plugin.audio.subsonic visible and installable in Kodi |
</code_examples>

<sota_updates>
## State of the Art (2026)

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Flat `<info>/<checksum>/<datadir>` in addon.xml | `<dir>` wrapper required | Kodi Nexus 20.x (2022) | All new repos MUST use `<dir>`; old format silently breaks on Nexus/Omega |
| MD5 only checksum (`<checksum>` with no `verify` attribute) | `<checksum verify="sha256">` preferred | Kodi Nexus / Omega era | MD5 still works but Repository.cpp logs deprecation warning; SHA-256 is the forward-compatible choice |
| Travis CI for automation | GitHub Actions | ~2021-2022 (Travis free tier gutted) | All active community repos now use Actions; Travis is effectively dead for open source |
| `raw.githubusercontent.com` as `<datadir>` | GitHub Pages URL | Community migration ~2020 onward | Raw URLs have CDN caching issues; Pages is stable and has proper CDN |
| Python 2 addon.xml (`xbmc.python` 2.x) | Python 3, `xbmc.python` 3.0.0 | Kodi Matrix 19.x (2021) | Python 2 addons rejected on all current Kodi versions; always declare `version="3.0.0"` |
| Per-version repo directories (krypton/, leia/, etc.) | Single flat repo targeting current Kodi | Omega 21.x era | For single-author personal repos, branching adds complexity with no user benefit; only add `minversion`/`maxversion` if a plugin actually breaks between versions |

**Deprecated/outdated:**

- **`<hashes>true</hashes>`:** Kodi source logs this as deprecated alias for MD5. Use `<hashes>sha256</hashes>` or omit.
- **`xbmc/action-kodi-addon-submitter`:** For official repo submission only, not personal repos.
- **`compressed="true"` on `<info>` with plain `addons.xml`:** Only set `compressed="true"` if serving an actual `.gz` file. GitHub Pages negotiates gzip transparently; serve plain `addons.xml` with `compressed="false"`.
- **Kodi Matrix 19.x targeting:** EOL; not worth testing against for a new repo in 2026.
</sota_updates>

<open_questions>
## Open Questions

1. **Does upstream `plugin.audio.subsonic` HEAD include `icon.png` and `fanart.jpg` as actual files (not just declared in `addon.xml`)?**
   - What we know: upstream `addon.xml` declares `<icon>icon.png</icon>` and `<fanart>fanart.jpg</fanart>`
   - What's unclear: whether those files actually exist at HEAD in the git repo vs. being referenced but missing
   - Recommendation: verify with `git ls-files icon.png fanart.jpg` in the cloned repo during Wave 0 execution; if absent, generate placeholders using the `magick` commands above
   - Confidence: MEDIUM (declaration implies existence but the files were not directly verified)

2. **Exact behavior of `<datadir>` trailing slash in Kodi Omega vs. older versions**
   - What we know: the locked decision and community pattern both use a trailing slash; Kodi constructs `<datadir>/<id>/<id>-<ver>.zip`; if `<datadir>` has a trailing slash, this becomes `<datadir>/<id>/<id>-<ver>.zip` (correct)
   - What's unclear: whether Kodi normalises double-slash internally (e.g., if `<datadir>` had trailing slash AND Kodi prepended `/`); Repository.cpp extracts `datadir` as-is and passes to `URIUtils`
   - Recommendation: use trailing slash (as locked in context); smoke-test the constructed URL in Test 5 above; if 404, check for double-slash
   - Confidence: HIGH (trailing slash is universal in community examples and matches the URL math)

3. **`plugins.json` schema for Phase 1 stub**
   - What we know: Phase 1 only needs a stub; Phase 2 will iterate; the minimal schema needs at minimum `id` and `source` fields
   - What's unclear: whether Phase 2 will want `repo` (GitHub org/repo) vs. `url` (direct asset URL) as the fetch key
   - Recommendation: include both `id`, `repo`, and `source: "local"` fields in the Phase 1 stub so Phase 2 has a clear migration path to `source: "github-release"` without schema breakage
   - Confidence: MEDIUM (schema is Claude's discretion per CONTEXT.md)

4. **GitHub Pages API availability for Pages configuration**
   - What we know: `gh api repos/.../pages` endpoint exists and is documented
   - What's unclear: whether the sandwichfarm account has Pages enabled at the organization level; whether a newly created repo has Pages available immediately
   - Recommendation: attempt the API path in the setup procedure; fall back to UI (Settings > Pages) if the API returns a 404 or 403; both paths achieve the same result
   - Confidence: MEDIUM (API exists but account-level Pages availability not verified)
</open_questions>

<sources>
## Sources

### Primary (HIGH confidence)

- `xbmc/xbmc/addons/repository.xbmc.org/addon.xml` (fetched live 2026-04-29) — official `<dir>` block shape, `verify="sha256"` attribute, `<artdir>`, `<hashes>` elements
- `xbmc/xbmc/xbmc/addons/Repository.cpp` — `ParseDirConfiguration` function; `verify` attribute handling; `FetchIfChanged` polling sequence; datadir extraction
- `chadparry/kodi-repository.chad.parry.org/tools/create_repository.py` (fetched live 2026-04-29) — `zipfile.ZipFile.write(src, arcname)` pattern; addons.xml encoding; MD5 generation
- `drinfernoo/repository.example` (README + structure, fetched live 2026-04-29) — canonical community generator structure; `_repo_generator.py` algorithm description
- GitHub Pages official docs — deployment timing (up to 10 minutes; typically 30–90s for changes); `gh-pages` branch configuration; `.nojekyll` requirement for binary file serving

### Secondary (MEDIUM confidence)

- `sualfred/my-kodi-repo/repositories/repository.fredsrepo/addon.xml` (fetched live 2026-04-29) — multi-`<dir>` pattern; `<requires><import addon="xbmc.addon" version="12.0.0"/>` form; trailing slash on `<datadir>`
- `linuxserver/libreelec-addons/issues/50` (fetched live 2026-04-29) — "old schema definition" error when `<dir>` wrapper is absent on Kodi 20.1; confirms Pitfall 6
- WebSearch results: GitHub Pages CDN 404 caching on first deploy (community threads confirm 5–10 min delay, not officially documented)
- WebSearch results: Kodi force-update procedure (Settings > Addons > Check for updates); confirmed against koditips.com and libreelec.tv wiki

### Tertiary (LOW confidence — verify during execution)

- Upstream `plugin.audio.subsonic` HEAD contains `icon.png` and `fanart.jpg` as actual files (inferred from `addon.xml` declaration; not directly checked in file listing)
- ImageMagick `label:` primitive font availability on this system (DejaVu-Sans-Bold used in commands; may need to substitute available font — run `magick -list font` to check)
</sources>

<metadata>
## Metadata

**Research scope:**
- Core technology: Kodi repository protocol (Repository.cpp); GitHub Pages static hosting
- Ecosystem: Python 3 stdlib generator; ImageMagick 7 for artwork; `gh` CLI for Pages setup
- Patterns: `<dir>` wrapper XML schema; ZIP arcname construction; atomic checksum regeneration; `.nojekyll` for binary serving; orphan `gh-pages` branch
- Pitfalls: ZIP nesting, BOM/CRLF, stale checksums, GitHub Pages first-deploy CDN delay, Kodi repo cache, old schema without `<dir>`

**Confidence breakdown:**
- File layout: HIGH — cross-verified against Repository.cpp (how Kodi constructs download URLs) and five live repos
- repo addon addon.xml shape: HIGH — verified against official `repository.xbmc.org/addon.xml` (fetched live) and community examples
- Generator script pseudocode: HIGH — derived from chadparry (fetched live) and drinfernoo (analyzed live) patterns; only output path for repo ZIP (root vs. subdir) is a Phase 1-specific adaptation
- Artwork: MEDIUM — ImageMagick commands are standard; font availability on this system not fully checked; upstream plugin artwork existence inferred not verified
- GitHub Pages setup: MEDIUM — API endpoint documented but account-level Pages availability and timing not tested against this specific repo
- First-publish pitfalls: MEDIUM — CDN caching behavior documented in GitHub community threads but not officially specified; Kodi cache behavior derived from Repository.cpp polling logic

**Research date:** 2026-04-29
**Valid until:** 2026-05-30 (30 days — Kodi protocol is very stable; GitHub Pages behavior is stable; only version numbers may drift)
</metadata>

---

*Phase: 01-bootstrap*
*Research completed: 2026-04-29*
*Ready for planning: yes*
