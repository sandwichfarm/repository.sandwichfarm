---
phase: 01-bootstrap
plan: 01
subsystem: infra
tags: [kodi, addon-xml, repository, artwork, imagemagick, gitignore]

requires: []

provides:
  - "repository.sandwichfarm/addon.xml with three locked-in Kodi repository URLs"
  - "Placeholder 512x512 icon.png and 1920x1080 fanart.jpg for repo addon"
  - "plugins.json stub with plugin.audio.subsonic entry"
  - ".gitignore excluding binaries from main branch"
  - "README.md stub"

affects:
  - "01-bootstrap/01-02 — generate.py depends on repository.sandwichfarm/addon.xml existing"
  - "01-bootstrap/01-03 — gh-pages branch requires artwork already committed to main"

tech-stack:
  added: [ImageMagick 7 (artwork generation)]
  patterns:
    - "main branch = source only; gh-pages = generated artifacts only"
    - "addon.xml <dir> wrapper required for Kodi 20+ (Nexus/Omega)"
    - "Three hard-coded URLs in addon.xml cannot change without user reinstall"

key-files:
  created:
    - repository.sandwichfarm/addon.xml
    - repository.sandwichfarm/icon.png
    - repository.sandwichfarm/fanart.jpg
    - plugins.json
    - .gitignore
    - README.md
  modified: []

key-decisions:
  - "Used Adwaita-Sans-Black font instead of DejaVu-Sans-Bold — DejaVu-Sans-Bold not available on this system; Adwaita-Sans-Black is a suitable bold-weight sans serif substitute"
  - "All three addon.xml URLs hard-coded pointing to https://sandwichfarm.github.io/repository.sandwichfarm/ — locked in before any ZIP is built, as required"
  - "plugins.json schema includes id, repo, and source fields to enable clean Phase 2 migration to source: github-release"

patterns-established:
  - "Pattern: addon.xml uses <dir> wrapper — mandatory for Kodi Nexus 20+ compatibility"
  - "Pattern: <checksum verify=sha256> — modern form, MD5 is deprecated per Kodi Repository.cpp"
  - "Pattern: <datadir zip=true> with trailing slash — required for correct Kodi URL construction"
  - "Pattern: all binary/generated artifacts excluded from main via .gitignore"

requirements-completed: [REPO-01, REPO-02]

duration: 1min
completed: 2026-04-29
---

# Phase 01 Plan 01: Repo Skeleton — addon.xml, artwork, plugins.json, .gitignore Summary

**Kodi repository addon source skeleton with three locked-in GitHub Pages URLs in addon.xml, 512x512 PNG icon, 1920x1080 JPEG fanart, and plugins.json stub for plugin.audio.subsonic**

## Performance

- **Duration:** ~1 min
- **Started:** 2026-04-29T13:52:20Z
- **Completed:** 2026-04-29T13:53:54Z
- **Tasks:** 3
- **Files modified:** 6

## Accomplishments
- Authored `repository.sandwichfarm/addon.xml` with the three load-bearing Kodi repository URLs locked in: info (addons.xml), checksum (addons.xml.sha256 with verify="sha256"), and datadir (trailing-slash URL with zip="true") — all pointing at https://sandwichfarm.github.io/repository.sandwichfarm/
- Generated placeholder artwork: 512x512 PNG icon and 1920x1080 JPEG fanart using ImageMagick 7 with dark-background wordmark style
- Stubbed plugins.json with plugin.audio.subsonic entry, .gitignore excluding vendor/ and *.zip from main, and README.md stub

## Task Commits

All three tasks were committed in a single atomic commit as specified in the plan:

1. **Task 1: Author repository.sandwichfarm/addon.xml** - `dc42764` (chore)
2. **Task 2: Generate placeholder artwork** - `dc42764` (chore)
3. **Task 3: Write plugins.json, .gitignore, README.md** - `dc42764` (chore)

**Plan commit (combined):** `dc42764` — `chore(01): repo skeleton — addon.xml, artwork, plugins.json, .gitignore`

## Files Created/Modified
- `repository.sandwichfarm/addon.xml` — Kodi repository addon declaration with three locked-in GitHub Pages URLs, <dir> wrapper, verify="sha256" checksum, datadir zip="true" with trailing slash
- `repository.sandwichfarm/icon.png` — 512x512 PNG placeholder icon (dark background, Adwaita-Sans-Black wordmark)
- `repository.sandwichfarm/fanart.jpg` — 1920x1080 JPEG placeholder fanart (dark gradient, sandwichfarm text)
- `plugins.json` — plugin registry stub with one entry: plugin.audio.subsonic
- `.gitignore` — excludes /vendor/, /tmp/, *.zip, __pycache__/, *.pyc, .mypy_cache/, .pytest_cache/, .DS_Store, *.swp
- `README.md` — one-paragraph stub (full docs deferred to Phase 3)

## Decisions Made
- Substituted `Adwaita-Sans-Black` for `DejaVu-Sans-Bold` in ImageMagick artwork generation — DejaVu-Sans-Bold is not installed on this system; Adwaita-Sans-Black is an equivalent bold-weight sans serif available via Adwaita theme fonts. Visual result is a valid 512x512 PNG and 1920x1080 JPEG meeting the dimension requirements.
- plugins.json schema includes `id`, `repo`, and `source` fields — the `repo` field gives Phase 2 a clear path to `source: "github-release"` without schema breakage.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Substituted Adwaita-Sans-Black for unavailable DejaVu-Sans-Bold**
- **Found during:** Task 2 (Generate placeholder artwork)
- **Issue:** Plan specified `-font DejaVu-Sans-Bold` but this font is not installed on this system (only DejaVu-Sans-Mono-for-Powerline variants are present, not DejaVu-Sans-Bold)
- **Fix:** Used `Adwaita-Sans-Black` (available via `/usr/share/fonts/Adwaita/AdwaitaSans-Regular.ttf`) — produces correct dimensions and valid file formats
- **Files modified:** N/A (command line argument only; files created correctly)
- **Verification:** `icon.png` verified as 512x512 PNG; `fanart.jpg` verified as 44441-byte JPEG (well above the 10KB threshold)
- **Committed in:** `dc42764`

---

**Total deviations:** 1 auto-fixed (Rule 1 — font substitution)
**Impact on plan:** Artwork meets all size/format requirements. Font choice is aesthetic only; the plan explicitly grants Claude discretion over artwork aesthetics.

## Issues Encountered
None beyond the font substitution noted above.

## User Setup Required
None — no external service configuration required for this plan.

## Next Phase Readiness
- `repository.sandwichfarm/addon.xml` is committed with all three locked-in URLs. Plan 02 (tools/generate.py) can now reference this file as its source input.
- artwork is committed; no regeneration needed for Phase 2.
- `.gitignore` in place — *.zip and /vendor/ are excluded from main, ready for binary artifact handling on gh-pages.
- Concern carried forward: before any ZIP is published, the GitHub Pages URL must be confirmed live (Plan 03). The addon.xml URLs are locked and cannot be changed after first user install.

---
*Phase: 01-bootstrap*
*Completed: 2026-04-29*
