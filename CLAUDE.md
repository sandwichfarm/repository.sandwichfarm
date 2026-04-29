<!-- GSD:project-start source:PROJECT.md -->
## Project

**repository.sandwichfarm**

A Kodi addon repository that hosts and distributes the user's personal Kodi plugins to end users. End users install a small "repository" addon once, then Kodi can browse, install, and auto-update any plugin published here. The first plugin to ship through it is [plugin.audio.subsonic](https://github.com/sandwichfarm/plugin.audio.subsonic), with capacity for additional plugins over time.

**Core Value:** Kodi users can install and stay up-to-date on `sandwichfarm` plugins (starting with `plugin.audio.subsonic`) by adding a single repository URL to Kodi — without manually downloading ZIPs from GitHub.

### Constraints

- **Compatibility**: Must work with current and recent Kodi versions (Nexus / Omega / Piers — at minimum the version `plugin.audio.subsonic` already targets in its `addon.xml`).
- **Tech stack**: Whatever produces a valid `addons.xml` + ZIP layout; must run on free-tier static hosting and be reproducible in CI.
- **Cost**: Free or near-free to host indefinitely (GitHub Pages / Cloudflare Pages tier is fine).
- **Security**: Distribute unsigned ZIPs over HTTPS; users will need to enable "unknown sources" in Kodi (standard for non-official repos), and we should not require it to be off.
- **Maintenance**: One-person maintenance — automation must minimise manual steps when releasing.
<!-- GSD:project-end -->

<!-- GSD:stack-start source:research/STACK.md -->
## Technology Stack

## Recommended Stack
### Core Technologies
| Technology | Version | Purpose | Why Recommended |
|------------|---------|---------|-----------------|
| GitHub Pages | N/A (free tier) | Static HTTPS hosting for addons.xml + ZIPs | Zero-cost, built-in HTTPS, Fastly CDN, custom domain support, native GitHub Actions integration — the de-facto host for personal Kodi repos; nearly every community example uses it |
| Python | 3.x (stdlib only) | Repository generator runtime | Canonical language for all Kodi tooling; both major generator scripts (drinfernoo/_repo_generator.py, chadparry/create_repository.py) are pure Python with no third-party deps |
| GitHub Actions | N/A | CI/CD: regenerate addons.xml + commit on push | Replaces Travis CI (used by older templates); modern community repos (dot-Justin/kodi-repo) trigger on push-to-main and auto-commit the regenerated index |
### Repository Generator: drinfernoo/_repo_generator.py
- Source: https://github.com/drinfernoo/repository.example (fork/copy the `_repo_generator.py` into your own repo's `tools/` directory)
- No external dependencies — uses only `hashlib`, `os`, `shutil`, `sys`, `zipfile`, `xml.etree.ElementTree`
- Works with Python 3.x (any minor version)
- Scans addon subdirectories for `addon.xml`, builds ZIP archives into `zips/<addon.id>/<addon.id>-<version>.zip`, writes `addons.xml` and `addons.xml.md5`
- Supports per-Kodi-version directory targeting (krypton, leia, matrix, nexus, repo)
- Confidence: MEDIUM (verified via script source inspection; last upstream commit not dateable due to GitHub auth wall, but widely forked and referenced)
- Source: https://github.com/chadparry/kodi-repository.chad.parry.org/blob/master/tools/create_repository.py
- Copyright 2016–2022; version 2.3.8; last confirmed update 2022
- Supports fetching addon source directly from Git URLs (not just local dirs), parallel processing, gzip-compressed addons.xml
- Requires `GitPython` pip dep when using Git URL sources
- More powerful but overkill for a single-author repo with local submodules; last update is 2022
- Confidence: MEDIUM (script content verified; maintenance status LOW — no confirmed 2023+ activity)
### Supporting Libraries
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| kodi-addon-checker | 0.0.36 (June 2025) | Validates addon.xml, artwork, file structure against Kodi rules | Run in CI on plugin source repos before publishing to the distribution repo; not needed in the repo itself |
| hashlib (stdlib) | built-in | MD5 and SHA256 checksum generation for addons.xml | Always — part of every generator script |
| xml.etree.ElementTree (stdlib) | built-in | Parse/write addons.xml | Always — no external XML lib needed |
| zipfile (stdlib) | built-in | Pack addon source into distribution ZIP | Always |
| GitPython | >=3.x | Fetch addon source directly from remote Git URLs | Only if using chadparry's create_repository.py with remote Git sources; not needed otherwise |
### Development Tools
| Tool | Purpose | Notes |
|------|---------|-------|
| `actions/checkout@v4` | Check out repo in CI | Use v4; v1 is used by older Kodi action templates but is deprecated |
| `actions/setup-python@v5` | Set up Python in CI | Use `python-version: '3.x'` — no specific minor version needed |
| `stefanzweifel/git-auto-commit-action` | Auto-commit regenerated index in CI | Community-standard action for committing changed files back to the repo from within a workflow; eliminates hand-rolling git config/commit/push steps |
| `xbmc/action-kodi-addon-checker` | Run kodi-addon-checker in CI on plugin repos | For validating individual addon source repos, not the distribution repo |
## Repository Addon Structure (the wrapper addon)
- `<hashes>` can be `md5` or `sha256`. Kodi source code (Repository.cpp) explicitly warns that MD5 "is broken and will only guard against unintentional data corruption" and treats the string `"true"` as a deprecated alias for MD5. SHA256 is the modern option but requires the generator to also produce `addons.xml.sha256`. For personal repos in 2026, MD5 remains the community standard because all generator scripts output it. SHA256 support is a minor enhancement worth adding.
- The repository addon itself gets ZIPped and placed at the repo root so users can "install from ZIP" on first setup.
- Confidence: HIGH (cross-verified from gnoling/kodi.addons addon.xml, search result descriptions of the extension point schema, xbmc/xbmc Repository.cpp source)
## Hosting Comparison
| Platform | HTTPS | Custom Domain | Free Bandwidth | Free Storage | CI Integration | Verdict |
|----------|-------|---------------|----------------|--------------|----------------|---------|
| **GitHub Pages** | Yes (auto) | Yes (CNAME, free TLS) | 100 GB/month soft limit | 1 GB repo | Native; deploy from Actions | **Best choice** for this project |
| **Cloudflare Pages** | Yes (auto) | Yes (up to 100/project) | Unlimited (undocumented cap) | 25 MiB/file, 20k files | GitHub integration (500 builds/month free) | Good alternative; adds complexity for no clear gain for a static file repo this size |
| **GitHub raw.githubusercontent.com** | Yes | No (raw.githubusercontent.com only) | Unknown/throttled | Same as repo | N/A — no deployment step | Avoid for production; no CDN, content-type issues, rate-limit risk |
| **AWS S3** | Requires CloudFront | Yes | 5 GB free tier then pay-per-GB | 5 GB free | Requires separate setup | Overkill; cost unpredictable at scale; S3 static hosting does not serve HTTPS natively |
## CI/CD Pattern (GitHub Actions)
# .github/workflows/update-repo.yml
## Kodi Version Targeting
| Kodi Version | Code Name | Status (April 2026) | Python | Target? |
|---|---|---|---|---|
| 19.x | Matrix | End of life | 3.x (3.6+) | No |
| 20.x | Nexus | Maintenance only | 3.x (3.11) | Optional |
| 21.x | Omega | **Current stable** | 3.x (3.12) | **Yes — primary target** |
| 22.x | Piers | Alpha 3 (pre-release) | 3.14.3 | No (wait for stable) |
## Alternatives Considered
| Recommended | Alternative | Why Not |
|-------------|-------------|---------|
| drinfernoo `_repo_generator.py` (adapted) | chadparry `create_repository.py` | Last updated 2022; adds GitPython dep; overkill for a local-source workflow; harder to customize |
| GitHub Pages | Cloudflare Pages | Adds a second platform account and DNS/CI complexity for no meaningful benefit at this repo's scale |
| GitHub Pages | raw.githubusercontent.com | No CDN, no content-type negotiation, rate-limit risk, no custom domain |
| GitHub Pages | AWS S3 + CloudFront | Requires paid services beyond free tier; more infrastructure to manage; not the community pattern |
| GitHub Actions | Travis CI | Travis CI free tier is now severely restricted (credits-based); older Kodi templates used Travis but all modern examples have migrated to Actions |
| Git submodules (for plugin source) | Copying source directly into repo | Submodules keep plugin source authoritative in its own repo; avoids duplication; easier to track upstream changes |
| Flat single-directory repo layout | Per-version directories (matrix/, nexus/, omega/) | Single-author repo targeting one stable version; version branching adds complexity with no benefit until a second incompatible Kodi version exists |
## What NOT to Use
| Avoid | Why | Use Instead |
|-------|-----|-------------|
| Hand-edited `addons.xml` | Error-prone, doesn't scale beyond 1-2 addons, breaks on version bumps | `tools/generate_repo.py` script auto-regenerated in CI |
| Travis CI | Free tier now effectively requires paid credits after 10,000 build minutes (consumed fast); migration path to Actions is well documented | GitHub Actions |
| `raw.githubusercontent.com` URLs in `addon.xml` datadir | GitHub does not guarantee raw URL stability or CDN delivery; rate-limited; no custom domain; some Kodi versions reported slow/failed updates | GitHub Pages URL |
| Python 2 | All Kodi versions still in active support (Nexus, Omega) require Python 3 addons; Python 2 was dropped at Matrix (19.x) | Python 3.x |
| `xbmc/action-kodi-addon-submitter` | This action submits to the **official Kodi addon repo** (requires a PR/review process); it is not for personal/self-hosted repos | Custom generate + commit workflow |
| Unsigned-only without HTTPS | Kodi strongly recommends HTTPS for all repository URLs; HTTP exposes users to MITM | GitHub Pages (auto-HTTPS) |
## Version Compatibility
| Component | Compatible With | Notes |
|-----------|-----------------|-------|
| `_repo_generator.py` / `generate_repo.py` | Python 3.6–3.13+ | No version-specific features; uses only stdlib |
| `kodi-addon-checker` 0.0.36 | Python 3.8–3.13 | For linting plugin source repos; run in plugin CI, not repo CI |
| Kodi Omega 21.x | `addons.xml` + `addons.xml.md5` | MD5 checksum format works; SHA256 also accepted if `<hashes>sha256</hashes>` declared |
| Kodi Nexus 20.x | Same format as Omega | Backward-compatible; no format changes needed |
| GitHub Pages | Public repos on free tier | Must be a public repository; 1 GB size limit, 100 GB/month soft bandwidth |
## Installation
# Verify Python 3 is available (any 3.x works)
# Optional: install kodi-addon-checker for linting plugin source
## Sources
- https://github.com/drinfernoo/repository.example — `_repo_generator.py` source inspection; GitHub Pages setup workflow; MEDIUM confidence (last commit not dateable; widely forked)
- https://github.com/dot-Justin/kodi-repo — GitHub Actions workflow verified (actions/checkout@v4, setup-python@v5, git-auto-commit); HIGH confidence
- https://github.com/chadparry/kodi-repository.chad.parry.org — `create_repository.py` source inspection; copyright 2016-2022; MEDIUM confidence (maintenance status unclear post-2022)
- https://github.com/xbmc/xbmc/blob/master/xbmc/addons/Repository.cpp — Hash format support (MD5 deprecation warning, SHA256 support); HIGH confidence
- https://github.com/xbmc/xbmc/blob/master/addons/xbmc.python/addon.xml — xbmc.python version 3.0.2; HIGH confidence
- https://pypi.org/project/kodi-addon-checker/ — version 0.0.36, June 2025, Python 3.8–3.13; HIGH confidence
- https://github.com/xbmc/action-kodi-addon-checker — official Kodi GitHub Action; HIGH confidence
- https://github.com/xbmc/action-kodi-addon-submitter — for official repo submission (not personal repos); HIGH confidence
- https://docs.github.com/en/pages/getting-started-with-github-pages/github-pages-limits — 100 GB/month soft bandwidth, 1 GB site limit; HIGH confidence
- https://developers.cloudflare.com/pages/platform/limits/ — 500 builds/month, 20k files, 25 MiB/file; HIGH confidence
- https://troypoint.com/kodi-22-piers/ — Kodi 22 Piers Alpha 3 status, Python 3.14.3; MEDIUM confidence (third-party site)
- https://kodi.tv/article/kodi-22-piers-alpha-3/ — Omega 21.3 is current stable; Alpha 3 confirmed; MEDIUM (403 blocked, cross-verified via search)
- https://github.com/gnoling/kodi.addons/blob/master/repository.gnoling/addon.xml — repository addon.xml extension block structure; HIGH confidence
<!-- GSD:stack-end -->

<!-- GSD:conventions-start source:CONVENTIONS.md -->
## Conventions

Conventions not yet established. Will populate as patterns emerge during development.
<!-- GSD:conventions-end -->

<!-- GSD:architecture-start source:ARCHITECTURE.md -->
## Architecture

Architecture not yet mapped. Follow existing patterns found in the codebase.
<!-- GSD:architecture-end -->

<!-- GSD:workflow-start source:GSD defaults -->
## GSD Workflow Enforcement

Before using Edit, Write, or other file-changing tools, start work through a GSD command so planning artifacts and execution context stay in sync.

Use these entry points:
- `/gsd:quick` for small fixes, doc updates, and ad-hoc tasks
- `/gsd:debug` for investigation and bug fixing
- `/gsd:execute-phase` for planned phase work

Do not make direct repo edits outside a GSD workflow unless the user explicitly asks to bypass it.
<!-- GSD:workflow-end -->



<!-- GSD:profile-start -->
## Developer Profile

> Profile not yet configured. Run `/gsd:profile-user` to generate your developer profile.
> This section is managed by `generate-claude-profile` -- do not edit manually.
<!-- GSD:profile-end -->
