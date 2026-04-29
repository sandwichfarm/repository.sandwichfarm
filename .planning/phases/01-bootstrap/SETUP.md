# Phase 1 Setup: GitHub Pages Manual Steps

**Generated:** 2026-04-29
**Phase:** 01-bootstrap / Plan 03
**Status:** gh-pages branch published; GitHub Pages activation required (see Section 2)

---

## Section 1: Prerequisites

- GitHub account with owner access to the `sandwichfarm` organization
- `gh` CLI authenticated: `gh auth status` (authed as `dskvr`)
- Local clone at `/home/sandwich/Develop/repository.sandwichfarm`
- `git` and `curl` on `$PATH`

---

## Section 2: One-time GitHub Setup

### 2a. Enable Pages for the Organization (owner step)

The `sandwichfarm` org has "Pages creation" restricted. Before the repository can serve GitHub Pages, the org owner must enable it:

1. Go to: https://github.com/organizations/sandwichfarm/settings/member_privileges
2. Scroll to **"Pages"** section
3. Set: **"Public pages"** to **Enabled** (or "Enabled for all members")
4. Click **Save**

**Note:** This is a one-time org-level toggle. Without it, the Pages API returns HTTP 422 "organization administrators disabled Pages creation" and the Settings > Pages tab on the repo will not show the source selector.

### 2b. Enable Pages for the Repository

After the org-level toggle is enabled:

1. Go to: https://github.com/sandwichfarm/repository.sandwichfarm/settings/pages
2. Under **"Build and deployment"**:
   - **Source**: Deploy from a branch
   - **Branch**: `gh-pages`
   - **Folder**: `/ (root)`
3. Click **Save**
4. Wait for the green indicator: *"Your site is live at https://sandwichfarm.github.io/repository.sandwichfarm/"*
   - Typical wait: 30–90 seconds for first deployment
   - Maximum wait: up to 10 minutes for CDN propagation (Pitfall 4)

**Alternative (CLI — works only after org-level Pages is enabled):**

```bash
gh api repos/sandwichfarm/repository.sandwichfarm/pages \
  --method POST \
  -H "Accept: application/vnd.github+json" \
  --field source='{"branch":"gh-pages","path":"/"}'
```

### 2c. Verify Deployment

```bash
# Poll until live (up to 10 minutes on first publish)
BASE="https://sandwichfarm.github.io/repository.sandwichfarm"
until curl -fsSI "$BASE/.nojekyll" 2>/dev/null | grep -q "200"; do
  echo "Waiting for Pages..."; sleep 10
done
echo "GitHub Pages is live."
```

Or check the Deployments tab: https://github.com/sandwichfarm/repository.sandwichfarm/deployments

---

## Section 3: Verify GitHub Pages is Live

Run this after the org + repo setup above:

```bash
BASE="https://sandwichfarm.github.io/repository.sandwichfarm"

# Wait for Pages to go live
until curl -fsSI "$BASE/.nojekyll" 2>/dev/null | grep -q "200"; do
  echo "Waiting..."; sleep 10
done
echo "GitHub Pages is live."

# Verify all endpoints
curl -fsSI "$BASE/addons.xml" | grep "HTTP/"
curl -fsSI "$BASE/addons.xml.sha256" | grep "HTTP/"
curl -fsSI "$BASE/addons.xml.md5" | grep "HTTP/"
curl -fsSI "$BASE/repository.sandwichfarm-1.0.0.zip" | grep "HTTP/"
curl -fsSI "$BASE/plugin.audio.subsonic/plugin.audio.subsonic-3.1.0.zip" | grep "HTTP/"
```

Expected: all return `HTTP/2 200`.

---

## Section 4: Canonical Live URLs (Smoke Test)

All of these must return HTTP 200 after Pages is configured:

| URL | Purpose |
|-----|---------|
| `https://sandwichfarm.github.io/repository.sandwichfarm/addons.xml` | Kodi addon index |
| `https://sandwichfarm.github.io/repository.sandwichfarm/addons.xml.sha256` | SHA-256 checksum sidecar |
| `https://sandwichfarm.github.io/repository.sandwichfarm/addons.xml.md5` | MD5 checksum sidecar (compat) |
| `https://sandwichfarm.github.io/repository.sandwichfarm/repository.sandwichfarm-1.0.0.zip` | Repo addon ZIP (users install this) |
| `https://sandwichfarm.github.io/repository.sandwichfarm/plugin.audio.subsonic/plugin.audio.subsonic-3.1.0.zip` | Plugin ZIP at canonical path |

**Kodi repository source URL (copy-paste this into Kodi):**

```
https://sandwichfarm.github.io/repository.sandwichfarm/
```

---

## Section 5: Kodi Verification Steps

After all smoke tests pass, verify with Kodi:

1. **Enable Unknown Sources** (required for non-official repos):
   - Settings > System > Add-ons > "Unknown sources" → turn **ON** → confirm "Yes"

2. **Add the repository source via File Manager:**
   - Settings > File Manager > Add source
   - Enter URL: `https://sandwichfarm.github.io/repository.sandwichfarm/`
   - Name: `sandwichfarm` (or any label you prefer)
   - OK / Save

3. **Install the repo addon ZIP:**
   - Add-ons > Install from zip file
   - Navigate to the `sandwichfarm` source you just added
   - Select `repository.sandwichfarm-1.0.0.zip`
   - Wait for "Add-on installed" notification (may take a few seconds)

4. **Browse and install plugin.audio.subsonic:**
   - Add-ons > Install from repository
   - "Sandwichfarm Repository" should appear in the list
   - Music add-ons > `plugin.audio.subsonic` should be listed
   - Select it > Install
   - Wait for "Add-on installed" notification

**Expected outcomes:**
- Step 3: Kodi shows notification "Sandwichfarm Repository Add-on installed"
- Step 4: "Sandwichfarm Repository" appears in the repository list
- Step 4: `plugin.audio.subsonic` is listed and installable from the repo browser
- Step 4: Install completes without "Could not connect to repository" error

**Troubleshooting:**
- "Could not connect to repository": GitHub Pages CDN is still settling. Wait 2 minutes and try "Check for updates" on the repo addon.
- Repo browser shows zero addons: Check `.nojekyll` is in the gh-pages branch root and that `addons.xml` passes the BOM check.
- "Unknown source" error on the ZIP install: Ensure "Unknown sources" is enabled in Settings > System > Add-ons.

---

## Section 6: Re-Publishing (Future Updates)

When a new plugin version is released:

```bash
# 1. Update vendor/plugin.audio.subsonic (pull or re-clone)
git -C /home/sandwich/Develop/repository.sandwichfarm/vendor/plugin.audio.subsonic pull

# 2. Re-run the generator to produce fresh staging artifacts
python3 /home/sandwich/Develop/repository.sandwichfarm/tools/generate.py \
  --plugin-src /home/sandwich/Develop/repository.sandwichfarm/vendor/plugin.audio.subsonic \
  --repo-addon-src /home/sandwich/Develop/repository.sandwichfarm/repository.sandwichfarm \
  --output /tmp/gh-pages-staging

# 3. Switch to gh-pages, copy artifacts, commit, push
git -C /home/sandwich/Develop/repository.sandwichfarm checkout gh-pages
cp -a /tmp/gh-pages-staging/. /home/sandwich/Develop/repository.sandwichfarm/
git -C /home/sandwich/Develop/repository.sandwichfarm add -A
git -C /home/sandwich/Develop/repository.sandwichfarm commit -m "publish: update plugin.audio.subsonic to X.Y.Z"
git -C /home/sandwich/Develop/repository.sandwichfarm push origin gh-pages
git -C /home/sandwich/Develop/repository.sandwichfarm checkout main

# 4. In Kodi: force check for updates
# Settings > Add-ons > (select Sandwichfarm Repository) > Check for updates
```

**Note:** Phase 2 will automate steps 1-3 via GitHub Actions.

---

## Section 7: What Was Done Automatically (Plan 03 Execution Log)

| Step | Result |
|------|--------|
| gh-pages orphan branch created | Done — commit `da3383e` |
| gh-pages pushed to origin | Done — `git push -u origin gh-pages` succeeded |
| `.nojekyll` at gh-pages root | Done — included in commit `da3383e` |
| `addons.xml` + checksums published | Done — included in commit `da3383e` |
| `repository.sandwichfarm-1.0.0.zip` at root | Done — included in commit `da3383e` |
| `plugin.audio.subsonic/plugin.audio.subsonic-3.1.0.zip` at canonical path | Done — included in commit `da3383e` |
| GitHub Pages configured via API | FAILED — org-level Pages creation disabled (HTTP 422); manual UI step required (see Section 2) |
| HTTP smoke tests | PENDING — blocked on Pages activation |
| Kodi human verification | PENDING — blocked on Pages activation |
