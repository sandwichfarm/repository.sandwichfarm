# Pitfalls Research

**Domain:** Kodi addon repository — self-hosted static distribution endpoint (addons.xml + ZIPs)
**Researched:** 2026-04-29
**Confidence:** MEDIUM-HIGH (official Kodi wiki, xbmc/addon-check source, forum threads, known-good repo examples)

---

## Critical Pitfalls

### Pitfall 1: ZIP nesting — addon directory not at ZIP root

**What goes wrong:**
Kodi unpacks the ZIP and expects to find `addon.xml` at `<addon_id>/addon.xml`. If the ZIP was created from the wrong working directory, you get double-nesting: `plugin.audio.subsonic/plugin.audio.subsonic/addon.xml`. Kodi rejects it immediately with "Addon does not have correct structure" or "Failed due to an invalid structure."

**Why it happens:**
Running `zip -r plugin.audio.subsonic.zip plugin.audio.subsonic/` from the parent directory is correct. Running `zip -r ../plugin.audio.subsonic.zip .` from inside the addon directory produces a flat archive (no top-level folder). Running `zip -r plugin.audio.subsonic.zip .` from the grandparent directory produces double-nesting. The CI working directory at job time often differs from where developers test manually.

**How to avoid:**
Pin the zip command to always run from the directory *containing* the addon folder:
```bash
# CORRECT — run from the directory that contains plugin.audio.subsonic/
zip -r zips/plugin.audio.subsonic/plugin.audio.subsonic-1.0.0.zip plugin.audio.subsonic/ \
  --exclude "*.git*" --exclude "*__pycache__*" --exclude "*.pyc"
```
Add a CI check: after zipping, `unzip -l` the archive and assert the first entry is `plugin.audio.subsonic/addon.xml`.

**Warning signs:**
- Kodi log: `"Addon does not have correct structure"` or `"Unable to load ... addon.xml, Line 0"`
- Kodi log: `"Failed due to an invalid structure"`
- Manually unzipping shows `addon.xml` at archive root (no folder) or two folder levels deep

**Phase to address:** Publishing pipeline (ZIP generation step)

---

### Pitfall 2: Stale or mismatched addons.xml.md5

**What goes wrong:**
Kodi compares the MD5 it fetched against the one cached from the previous poll. If the MD5 does not change, Kodi skips re-fetching `addons.xml` entirely, so users never see new addon versions. Kodi logs: `"checksum not changed"` and silently moves on. Conversely, if `addons.xml` was updated but the MD5 was not regenerated atomically, Kodi fetches the new XML but the MD5 still matches the old one — causing the same skip-on-next-poll problem.

**Why it happens:**
Manually editing `addons.xml` then forgetting to regenerate `addons.xml.md5`. CI pipelines that write files in two separate steps with no guarantee of atomic delivery (GitHub Pages deploys files independently; a Kodi poll that hits the CDN edge between the two writes sees inconsistency).

**How to avoid:**
Always regenerate MD5 in the same script step that writes `addons.xml`, immediately after:
```bash
md5sum addons.xml | awk '{print $1}' > addons.xml.md5
# OR (macOS-compatible):
python3 -c "import hashlib,sys; print(hashlib.md5(open('addons.xml','rb').read()).hexdigest())" > addons.xml.md5
```
Never commit `addons.xml` without committing the new `addons.xml.md5` in the same commit.

**Warning signs:**
- Kodi log: `"checksum not changed"` appearing even after you published a new version
- Installed addon version in Kodi does not advance despite new ZIP being on the host
- `addons.xml.md5` file timestamp is older than `addons.xml`

**Phase to address:** Publishing pipeline (index generation step)

---

### Pitfall 3: Version not bumped in addon.xml — Kodi ignores the update

**What goes wrong:**
Kodi decides whether to offer or apply an update purely by comparing the version string in the installed addon's `addon.xml` against the version in the repository's `addons.xml`. If the version string is identical, Kodi considers the addon up-to-date and does not download the new ZIP, even if the file on disk differs byte-for-byte.

**Why it happens:**
Developer fixes a bug, pushes a new ZIP, regenerates `addons.xml` — but forgets to increment `version="x.y.z"` in the source `addon.xml` before packaging. The new ZIP contains the fix but announces the same version as what users already have installed.

**How to avoid:**
Make the version bump a mandatory gate before packaging. One pattern: a CI step that reads the version from `addon.xml`, checks it against the last git-tagged version, and fails the build if they match. Alternatively use `kodi-addon-release` (GitHub: felixmosh/kodi-addon-release) which automates version bump + tag + changelog + publish in one command.

Enforce semantic versioning: MAJOR.MINOR.PATCH. Patch = bug fix, Minor = new feature, Major = breaking change or Kodi minimum version change.

**Warning signs:**
- Kodi's "Check for updates" reports nothing new despite new code on the host
- `addons.xml` lists the same version as what the user has installed
- Kodi log: no update-related lines at all when you expected an update offer

**Phase to address:** Developer workflow / release convention (document in CONTRIBUTING or Makefile)

---

### Pitfall 4: BOM bytes or wrong encoding in addons.xml / addon.xml

**What goes wrong:**
If `addons.xml` is written with a UTF-8 BOM (`\xEF\xBB\xBF` at byte 0), Kodi's XML parser fails to parse it. The file looks valid in a text editor but Kodi silently refuses to read the repository index. On Windows, editors like Notepad and some Python `open()` calls with `encoding='utf-8-sig'` emit BOM bytes. Windows-style CRLF line endings (`\r\n`) in an XML file that Kodi's parser does not tolerate produce the same class of silent parse failure.

**Why it happens:**
Generator scripts written or run on Windows without explicitly specifying `newline='\n'` and `encoding='utf-8'` (not `utf-8-sig`). Copying XML boilerplate from a Windows editor. Python's `xml.etree.ElementTree.write()` with `encoding='unicode'` does not emit a declaration, while `encoding='UTF-8'` does but must be used carefully.

**How to avoid:**
In the generator script, always write explicitly:
```python
with open('addons.xml', 'w', encoding='utf-8', newline='\n') as f:
    f.write('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n')
    f.write(content)
```
Add a CI validation step:
```bash
python3 -c "
data = open('addons.xml', 'rb').read()
assert not data.startswith(b'\xef\xbb\xbf'), 'BOM detected'
assert b'\r' not in data, 'CRLF detected'
print('encoding OK')
"
```

**Warning signs:**
- Repository installs but addon list is empty (Kodi parsed zero addons from malformed XML)
- Kodi log: `"Failed to parse addons.xml"` or `"CXBMCTinyXML ... ERROR"` near line 1
- `xxd addons.xml | head -1` shows `ef bb bf` as first three bytes

**Phase to address:** Publishing pipeline (index generation + CI validation)

---

### Pitfall 5: Wrong ZIP path layout for hosted files — datadir mismatch

**What goes wrong:**
Kodi constructs the download URL for a plugin as `<datadir>/<addon_id>/<addon_id>-<version>.zip`. If the ZIPs are not stored at exactly that path relative to `<datadir>`, every install attempt returns a 404. A trailing slash discrepancy in the `<datadir>` URL in the repository's `addon.xml` is the single most common cause — Kodi appends its own `/`, leading to double-slash URLs that some hosts reject.

**Why it happens:**
Hosting layout decisions made without cross-referencing the `<datadir>` value. GitHub Pages serves content at `https://user.github.io/repo/` (trailing slash implicit). Developers set `<datadir>https://user.github.io/repo/zips</datadir>` (no trailing slash) then store files at `zips/plugin.audio.subsonic/plugin.audio.subsonic-1.0.0.zip` — which works. But if they accidentally add a trailing slash to `<datadir>`, the constructed URL becomes `https://user.github.io/repo/zips//plugin.audio.subsonic/...`.

**How to avoid:**
Standardise: no trailing slash on `<datadir>`. Validate by constructing the expected URL manually in CI and doing an HTTP HEAD request:
```bash
DATADIR="https://user.github.io/repo/zips"
ADDON="plugin.audio.subsonic"
VERSION="1.0.0"
curl -sI "$DATADIR/$ADDON/$ADDON-$VERSION.zip" | grep "HTTP/"
```
The response must be `200 OK`, not 301/302/404.

**Warning signs:**
- Kodi log: `"CUrl::FillBuffer - Failed: HTTP returned error 404"` when installing a plugin
- Browser can navigate to `<datadir>` root but not the specific ZIP path
- Double-slash visible when you manually construct the URL

**Phase to address:** Publishing pipeline (hosting layout + repository addon.xml `<datadir>` configuration)

---

### Pitfall 6: xbmc.python version mismatch — dependency cannot be satisfied

**What goes wrong:**
`"The dependency on xbmc.python version X could not be satisfied"` is one of the most common Kodi addon installation errors. It arises when `addon.xml` declares a minimum `xbmc.python` version that is higher than what the user's Kodi build provides, or when it still specifies a Python 2 version (2.x) on a Kodi version that only ships Python 3.

**Why it happens:**
- Copying `addon.xml` from an old project that targeted Kodi Leia (Python 2, `xbmc.python` 2.x)
- Targeting too-new a version (e.g. `3.0.1`) without checking whether the minimum supported Kodi version provides it
- Not knowing the mapping: Kodi Matrix/Nexus/Omega all ship `xbmc.python` 3.0.0 (minimum compatible) / 3.0.1 (advised). Python 2 addons are rejected on all these versions.

**How to avoid:**
For `plugin.audio.subsonic` targeting Nexus/Omega:
```xml
<import addon="xbmc.python" version="3.0.0"/>
```
`3.0.0` is the safe minimum — it works on Matrix, Nexus, and Omega. Do not use `2.x` at all; do not use `3.0.1` as minimum unless you are willing to drop Matrix support.

Run `kodi-addon-checker` locally before publishing:
```bash
pip install kodi-addon-checker
kodi-addon-checker --branch omega plugin.audio.subsonic/
```

**Warning signs:**
- Kodi notification: `"The dependency on xbmc.python could not be satisfied"`
- Users on older Kodi versions (Nexus vs Omega) report inability to install while others succeed
- `addon.xml` contains `version="2.` in the xbmc.python import

**Phase to address:** Addon packaging / addon.xml validation step in CI

---

### Pitfall 7: repository addon's checksum URL or info URL points at wrong location

**What goes wrong:**
The repository addon (the ZIP users install first) contains its own `addon.xml` with three critical URLs: `<info>` (points to `addons.xml`), `<checksum>` (points to `addons.xml.md5`), and `<datadir>` (ZIP root). If any of these are wrong — stale placeholder, wrong branch name, old raw GitHub URL after a branch rename — every single addon in the repository fails silently. Users see "Could not connect to repository."

**Why it happens:**
Setting up the repository using a template (e.g. drinfernoo/repository.example) and not replacing all placeholder strings (`YOUR_USERNAME_HERE`, `REPOSITORY_NAME_HERE`, `BRANCH_NAME_HERE`). Renaming the `main` branch to `master` or vice versa after publishing the repository addon ZIP. Moving hosting from GitHub raw to GitHub Pages without updating the repository ZIP and re-publishing it to users.

**How to avoid:**
Treat the repository addon's `addon.xml` URLs as load-bearing configuration. After any hosting migration, the repository ZIP itself must be rebuilt and users must reinstall it. Add a CI smoke test that fetches all three URLs and asserts HTTP 200:
```bash
for URL in "$INFO_URL" "$CHECKSUM_URL"; do
  STATUS=$(curl -sI "$URL" | awk 'NR==1{print $2}')
  [ "$STATUS" = "200" ] || { echo "FAIL: $URL returned $STATUS"; exit 1; }
done
```

**Warning signs:**
- Kodi: `"Could not connect to repository"` immediately after installing the repo ZIP
- Browser 404 on the `<info>` URL value extracted from the installed repository's `addon.xml`
- Kodi log: `"CRepository: ... failed to read ... addons.xml"`

**Phase to address:** Repository addon creation + hosting setup

---

## Technical Debt Patterns

| Shortcut | Immediate Benefit | Long-term Cost | When Acceptable |
|----------|-------------------|----------------|-----------------|
| Hand-editing addons.xml | No tooling needed for one addon | Guaranteed stale MD5, copy-paste errors on next addon | Never — use generator script from day one |
| Using GitHub raw URLs (`raw.githubusercontent.com`) for datadir | Easiest to set up | Raw URLs have aggressive Cloudflare caching; a new ZIP may not be visible for minutes to hours; no custom domain | Only for MVP validation; migrate to GitHub Pages or Cloudflare Pages for production |
| Single `main` branch, no version branches | Simpler structure | Cannot serve different addon versions for different Kodi generations without branching later | Acceptable if only targeting Nexus/Omega and no older versions |
| No CI — build and publish locally | Zero setup time | One missed step (forgot to regenerate MD5, wrong zip command) breaks the repo for all users | Only for initial proof-of-concept; automate before first public announcement |
| Bundling ALL addon files including dev artifacts | No exclude list needed | ZIP contains `.git/`, `__pycache__/`, `.pyc`, test fixtures — inflates ZIP size, may confuse Kodi | Never |

---

## Integration Gotchas

| Integration | Common Mistake | Correct Approach |
|-------------|----------------|------------------|
| GitHub Pages | Assuming files are live immediately after `git push` | GitHub Pages deploy can take 30–90 seconds; CI must wait for deployment before running URL smoke tests |
| GitHub raw URLs | Using `github.com/user/repo/blob/main/file` instead of `raw.githubusercontent.com` | Use raw URLs, but be aware CDN edge nodes cache aggressively — a purge is not possible without the GitHub API |
| Cloudflare Pages / Workers | Default Cache-Control is aggressive; a 404 on a not-yet-deployed path gets cached for up to 5 minutes | Set `Cache-Control: no-store` for `addons.xml` and `addons.xml.md5`; allow longer TTL for versioned ZIPs (they never change once published) |
| GitHub Actions zip step | `actions/upload-artifact` strips the top-level directory by default | Use `zip` CLI directly with explicit working-directory control, not artifact actions |
| kodi-addon-checker | Running against the source directory (includes dev files) instead of the packaged ZIP | Run checker against the unpacked ZIP to catch what Kodi actually sees |

---

## Performance Traps

| Trap | Symptoms | Prevention | When It Breaks |
|------|----------|------------|----------------|
| Serving addons.xml uncompressed from a slow host | Kodi times out fetching the index on slow connections (FireTV on mobile data) | GitHub Pages and Cloudflare Pages both gzip automatically; ensure host supports gzip or pre-gzip | Essentially any connection slower than ~1Mbps on a large addons.xml |
| Storing full addon source history in ZIPs (`.git/`) | ZIPs are 10-100x larger than needed; slow to download on FireTV | Exclude `.git` explicitly in zip command | Any ZIP over ~5MB will timeout on slow FireTV connections |
| Re-generating addons.xml by scanning GitHub raw on each CI run | CI is slow; rate limits on GitHub API | Clone the repo in CI and scan local filesystem | Not a scale problem for single-maintainer; still fragile |

---

## Security Mistakes

| Mistake | Risk | Prevention |
|---------|------|------------|
| Distributing over plain HTTP | Kodi 19+ warns users about non-HTTPS repositories; modern Kodi versions may block HTTP repos outright | Use HTTPS exclusively — GitHub Pages and Cloudflare Pages provide this automatically |
| Letting TLS certificate expire | All users' auto-updates silently fail; Kodi logs SSL errors; users cannot install anything | Use Let's Encrypt via Cloudflare or GitHub Pages — both auto-renew; add a monthly calendar reminder to check cert expiry if on a custom domain with manual cert |
| Using the same addon ID as a well-known public repo | Kodi's addon database will confuse the two; users with both repos enabled will get unpredictable which version "wins" | Prefix all addon IDs with `sandwichfarm` or similar namespace: `plugin.audio.subsonic.sandwichfarm` if the generic ID is taken, or verify the ID is globally unique before publishing |
| Bundling third-party code whose license is incompatible | Kodi's moderation team blacklists entire repos that host piracy-adjacent content; even non-piracy repos get association-tainted | Scope is own-authored plugins only (already a stated constraint) — maintain this boundary strictly |

---

## UX Pitfalls

| Pitfall | User Impact | Better Approach |
|---------|-------------|-----------------|
| Install docs only describe desktop Kodi (File Manager > Add source) without mentioning Android / FireTV path differences | FireTV users (a large portion of Kodi's user base) are stuck at "where is File Manager?" | Write Android/FireTV-specific steps: Settings > File Manager > Add Network Location; call out that the menu labels differ |
| Not mentioning "Unknown sources" must be enabled | Users hit a hard block at the install-from-zip step with no explanation of why | Put `Settings > System > Add-ons > Unknown sources` as Step 0 in the install guide |
| Docs describe the repo addon URL but not what to do if "Install from zip file" is grayed out | Confuses new Kodi users — the option only appears after a source is added | Show File Manager source-add step before the "Install from zip file" step |
| No install verification step | Users don't know if the repo installed correctly vs just appearing installed | End the install guide with: "Open Add-ons > Get more > Music add-ons — you should see plugin.audio.subsonic listed." |
| Changelog file absent from the repository | Users see version numbers change with no context | Publish `changelog-x.y.z.txt` alongside each ZIP at `<datadir>/<addon_id>/changelog-x.y.z.txt` |

---

## "Looks Done But Isn't" Checklist

- [ ] **addons.xml.md5 regenerated:** The MD5 file is newer than addons.xml — verify with `stat -c %Y addons.xml addons.xml.md5 | sort -n` (md5 must be equal or newer)
- [ ] **Version bumped:** `grep version= plugin.audio.subsonic/addon.xml` matches the version in `addons.xml` AND differs from the previously published version
- [ ] **ZIP structure correct:** `unzip -l zips/plugin.audio.subsonic/plugin.audio.subsonic-1.0.0.zip | head -5` shows `plugin.audio.subsonic/addon.xml` as first entry
- [ ] **No dev artifacts in ZIP:** `unzip -l ... | grep -E '\.git|__pycache__|\.pyc'` returns empty
- [ ] **Repository addon URLs live:** All three URLs from the repository addon's `addon.xml` (`<info>`, `<checksum>`, `<datadir>`) return HTTP 200 from `curl -sI`
- [ ] **addons.xml no BOM:** `python3 -c "assert not open('addons.xml','rb').read(3)==b'\xef\xbb\xbf'"` exits 0
- [ ] **Unknown sources mentioned in docs:** Install guide explicitly includes the Settings toggle step
- [ ] **FireTV / Android path documented:** Install guide covers non-desktop Kodi UI
- [ ] **TLS active on hosting domain:** `curl -vI <base_url> 2>&1 | grep "SSL connection"` shows connection established

---

## Recovery Strategies

| Pitfall | Recovery Cost | Recovery Steps |
|---------|---------------|----------------|
| Wrong ZIP structure published | LOW | Repackage ZIP correctly, bump patch version, regenerate addons.xml + MD5, push; users who installed the bad ZIP must reinstall manually |
| Stale MD5 (users not seeing updates) | LOW | Regenerate MD5, push; Kodi polls on next scheduled check (default 24h) or user can force-check via Settings > Add-ons > My add-ons |
| Wrong URLs in published repository ZIP | HIGH | Must rebuild repository ZIP with correct URLs AND republish it; users must reinstall the repository addon itself — cannot be pushed silently |
| Certificate expired on custom domain | HIGH | Renew cert immediately; users' auto-updates are completely broken until resolved — no graceful degradation |
| Version not bumped — users stuck on old code | MEDIUM | Bump version, repackage, republish; users who already have the "same-version" install will get the update only once the new higher version is visible in addons.xml |
| BOM in addons.xml | LOW | Fix generator script, regenerate + push; once fixed, MD5 changes and Kodi fetches the corrected file |

---

## Pitfall-to-Phase Mapping

| Pitfall | Prevention Phase | Verification |
|---------|------------------|--------------|
| ZIP nesting wrong | Publishing pipeline — ZIP generation | CI: `unzip -l` assertion on generated ZIP |
| Stale MD5 | Publishing pipeline — index generation | CI: MD5 consistency check post-generation |
| Version not bumped | Developer workflow / release convention | CI: version differs from last git tag |
| BOM / encoding | Publishing pipeline — index generation | CI: byte-check on addons.xml before commit |
| datadir path mismatch | Hosting setup + repository addon creation | CI: HTTP HEAD smoke test on constructed ZIP URLs |
| xbmc.python version mismatch | Addon packaging / addon.xml authoring | CI: kodi-addon-checker --branch omega |
| Repository addon URLs stale | Repository addon creation + hosting setup | CI: smoke test all three `<dir>` URLs |
| TLS expiry | Infrastructure / hosting selection | Monthly cert expiry monitor or use auto-renew host |
| No Unknown Sources docs | Documentation phase | Manual review of install guide against Android Kodi |
| Dev artifacts in ZIP | Publishing pipeline — ZIP generation | CI: exclude-list in zip command + `unzip -l` grep |

---

## Sources

- [Add-on repositories — Official Kodi Wiki](https://kodi.wiki/view/Add-on_repositories)
- [Add-on structure — Official Kodi Wiki](https://kodi.wiki/view/Add-on_structure)
- [Addon.xml — Official Kodi Wiki](https://kodi.wiki/view/Addon.xml)
- [kodi-addon-checker — xbmc/addon-check on GitHub](https://github.com/xbmc/addon-check)
- [check_dependencies.py — xbmc/addon-check](https://github.com/xbmc/addon-check/blob/master/kodi_addon_checker/check_dependencies.py)
- [addons.xml.md5 / checksum in a repository — Kodi Forum thread #196459](https://forum.kodi.tv/showthread.php?tid=196459)
- [Problems with packaging zip for an addon (Unable to load addon.xml, Line 0) — Kodi Forum #371579](https://forum.kodi.tv/showthread.php?tid=371579)
- [Can't install .zip add-on: "invalid structure" — Kodi Forum #355413](https://forum.kodi.tv/showthread.php?tid=355413)
- [check the addons.xml.gz failed at get expected sha256 — xbmc/xbmc Issue #16104](https://github.com/xbmc/xbmc/issues/16104)
- [drinfernoo/repository.example — GitHub Pages Kodi repo example](https://github.com/drinfernoo/repository.example)
- [The dependency on xbmc.python could not be satisfied — CoreELEC Forum](https://discourse.coreelec.org/t/the-dependency-on-xbmc-python-version-2-x-could-not-be-satisfied/16428)
- [Submitting Add-ons — Official Kodi Wiki](https://kodi.wiki/index.php?title=Submitting_Add-ons)
- [felixmosh/kodi-addon-release — version bump automation](https://github.com/felixmosh/kodi-addon-release)
- [Cloudflare static site deployments causing prolonged 404s — Cloudflare Community](https://community.cloudflare.com/t/static-site-deployments-causing-prolonged-404s-to-users/558247)
- [Certificate expiry incidents — Kodi Forum thread #341127](https://forum.kodi.tv/showthread.php?tid=341127)

---
*Pitfalls research for: Kodi addon repository (self-hosted static)*
*Researched: 2026-04-29*
