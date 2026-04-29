---
phase: 01-bootstrap
plan: 02
subsystem: infra
tags: [kodi, python, generator, zipfile, hashlib, addons-xml, checksums, stdlib]

requires:
  - phase: 01-bootstrap/01-01
    provides: "repository.sandwichfarm/addon.xml with three locked-in Kodi URLs, icon.png, fanart.jpg"

provides:
  - "tools/generate.py — stdlib-only Kodi repo generator (make_zip, read_addon_xml, copy_addon_assets, build_addons_xml, write_index_and_checksums, main)"
  - "vendor/plugin.audio.subsonic/ cloned locally at HEAD (gitignored, not committed to main)"
  - "/tmp/gh-pages-staging/ with full verified staging output ready for Plan 03 gh-pages push"
  - "addons.xml with UTF-8 no-BOM no-CRLF encoding, containing both repository.sandwichfarm and plugin.audio.subsonic"
  - "addons.xml.sha256 and addons.xml.md5 checksum sidecars (atomic, consistent)"
  - "repository.sandwichfarm-1.0.0.zip at staging root with correct repository.sandwichfarm/ top-level directory"
  - "plugin.audio.subsonic/plugin.audio.subsonic-3.1.0.zip with correct plugin.audio.subsonic/ top-level directory"

affects:
  - "01-bootstrap/01-03 — staging artifacts in /tmp/gh-pages-staging/ ready to push to gh-pages branch"
  - "phase-02 CI — tools/generate.py is the exact script CI will wrap; no rewrite needed"

tech-stack:
  added: []
  patterns:
    - "Generator pattern: stdlib-only Python (hashlib, zipfile, xml.etree.ElementTree, os, shutil)"
    - "Atomic checksum write: addons.xml + addons.xml.sha256 + addons.xml.md5 in one write_index_and_checksums() call"
    - "ZIP arcname pattern: os.path.join(addon_id, os.path.relpath(full_path, addon_src_dir)) — explicit top-level dir"
    - "addons.xml encoding: open(..., 'w', encoding='utf-8', newline='\\n') with BOM assertion"
    - "ET.tostring(elem, encoding='unicode') — avoids BOM/declaration that encoding='utf-8' adds"
    - "Repo addon ZIP moved from subdir to staging root after make_zip() via shutil.move()"

key-files:
  created:
    - tools/generate.py
  modified: []

key-decisions:
  - "Plugin changelog-3.1.0.txt was absent from upstream; created with minimal content 'Version 3.1.0 — initial publish through repository.sandwichfarm.' — matches ZIP version exactly per IDX-06"
  - "upstream plugin.audio.subsonic ships real icon.png and fanart.jpg — no placeholder generation needed for plugin assets"
  - "generator reads plugin id and version dynamically from addon.xml (not hardcoded) — handles future version bumps without script changes"

patterns-established:
  - "Pattern: write_index_and_checksums() is atomic — all three index files written in a single function call"
  - "Pattern: assert not xml_bytes.startswith(b'\\xef\\xbb\\xbf') guards against BOM at write time"
  - "Pattern: repo addon ZIP lives at staging root (not subdir) — users install repository.sandwichfarm-1.0.0.zip directly"
  - "Pattern: .nojekyll created unconditionally in output_dir — required for GitHub Pages to serve binary ZIPs"

requirements-completed: [IDX-01, IDX-02, IDX-03, IDX-04, IDX-05, IDX-06, PLUG-01, REPO-03]

duration: 3min
completed: 2026-04-29
---

# Phase 01 Plan 02: Generator Script and Staging Artifacts Summary

**stdlib-only tools/generate.py producing addons.xml (UTF-8/no-BOM), SHA-256+MD5 checksum sidecars, repository.sandwichfarm-1.0.0.zip (staging root, correct nesting), and plugin.audio.subsonic-3.1.0.zip — all verified locally in /tmp/gh-pages-staging/**

## Performance

- **Duration:** ~3 min
- **Started:** 2026-04-29T13:56:27Z
- **Completed:** 2026-04-29T13:58:41Z
- **Tasks:** 2
- **Files modified:** 1 (tools/generate.py created)

## Accomplishments
- Cloned plugin.audio.subsonic into vendor/ (gitignored; not committed to main); confirmed it ships real icon.png and fanart.jpg
- Authored tools/generate.py with all six required functions (make_zip, read_addon_xml, copy_addon_assets, build_addons_xml, write_index_and_checksums, main) using only Python 3 stdlib
- Ran generator and verified all staging artifacts pass full correctness suite: BOM check, CRLF check, SHA-256 and MD5 checksum consistency, ZIP top-level directory nesting for both ZIPs, XML validity, addons.xml containing both addons

## Task Commits

1. **Task 1: Clone plugin and author tools/generate.py** - `8028f59` (feat)
2. **Task 2: Run generator and verify staging artifacts** — no commit (staging artifacts live in /tmp/, not in repo)

**Plan metadata:** (committed after SUMMARY.md)

## Files Created/Modified
- `tools/generate.py` — stdlib-only Kodi repository generator; implements make_zip with explicit arcname, build_addons_xml with ET.tostring encoding='unicode', write_index_and_checksums atomic writer with BOM assertion, and main() orchestrating full staging output

## Decisions Made
- Created `vendor/plugin.audio.subsonic/changelog-3.1.0.txt` with content "Version 3.1.0 — initial publish through repository.sandwichfarm." — upstream has CHANGELOG.md but no changelog-3.1.0.txt required by IDX-06; auto-generated minimal content satisfies the Kodi filename-version-match requirement
- Plugin assets (icon.png, fanart.jpg) used directly from upstream — no placeholder generation needed; both files exist at HEAD

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 2 - Missing Critical] Created changelog-3.1.0.txt absent from upstream plugin repo**
- **Found during:** Task 1 (Clone plugin source)
- **Issue:** IDX-06 requires `changelog-{VERSION}.txt` filename to match the ZIP version exactly; upstream plugin ships CHANGELOG.md but no `changelog-3.1.0.txt`
- **Fix:** Created `/home/sandwich/Develop/repository.sandwichfarm/vendor/plugin.audio.subsonic/changelog-3.1.0.txt` with content "Version 3.1.0 — initial publish through repository.sandwichfarm." — minimum required content per plan acceptance criteria
- **Files modified:** vendor/plugin.audio.subsonic/changelog-3.1.0.txt (local only, gitignored)
- **Verification:** File present in staging output at plugin.audio.subsonic/changelog-3.1.0.txt; copied correctly by copy_addon_assets()
- **Committed in:** Not committed to main (vendor/ is gitignored)

---

**Total deviations:** 1 auto-added (Rule 2 — missing required IDX-06 artifact)
**Impact on plan:** Necessary for IDX-06 compliance. Plan documented this exact scenario ("If missing, create it…"). No scope creep.

## Fallback Notes
- **Plugin assets**: No fallback taken. upstream plugin.audio.subsonic ships both `icon.png` and `fanart.jpg` at HEAD — no placeholder generation was needed.
- **Plugin changelog**: Fallback taken — upstream has no `changelog-3.1.0.txt`. Created with minimal required content per plan instructions.

## Known Stubs
None — all data is wired from real sources. addons.xml pulls actual addon.xml content from both addons. ZIPs contain real source files.

## Issues Encountered
None beyond the changelog fallback noted above.

## User Setup Required
None — no external service configuration required for this plan. Staging artifacts are local in /tmp/gh-pages-staging/.

## Next Phase Readiness
- `/tmp/gh-pages-staging/` contains all artifacts verified and ready for Plan 03 to push to gh-pages branch
- `tools/generate.py` committed to main — Phase 2 CI wraps this exact script
- Concern from Phase 1 carried forward: before pushing to gh-pages, GitHub Pages URL must be confirmed live (Plan 03 handles this)
- Staging artifacts summary:
  - addons.xml: UTF-8, no BOM, no CRLF, 2 addons (repository.sandwichfarm + plugin.audio.subsonic)
  - addons.xml.sha256: 64-char lowercase hex, consistent with addons.xml bytes
  - addons.xml.md5: 32-char lowercase hex, consistent with addons.xml bytes
  - repository.sandwichfarm-1.0.0.zip: at root, first entry is repository.sandwichfarm/addon.xml
  - plugin.audio.subsonic/plugin.audio.subsonic-3.1.0.zip: first entry is plugin.audio.subsonic/LICENSE
  - repository.sandwichfarm/{addon.xml, icon.png, fanart.jpg}: all present
  - plugin.audio.subsonic/{addon.xml, icon.png, fanart.jpg, changelog-3.1.0.txt}: all present

---
*Phase: 01-bootstrap*
*Completed: 2026-04-29*
