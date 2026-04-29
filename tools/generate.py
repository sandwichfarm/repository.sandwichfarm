#!/usr/bin/env python3
"""
tools/generate.py -- Kodi repository generator (Phase 1: local/manual)
Stdlib only: hashlib, zipfile, xml.etree.ElementTree, os, shutil, json, argparse

Usage:
  python3 tools/generate.py --plugin-src /path/to/plugin.audio.subsonic \
                             --repo-addon-src repository.sandwichfarm \
                             --output /tmp/gh-pages-staging
"""
import argparse
import fnmatch
import hashlib
import json
import os
import shutil
import zipfile
import xml.etree.ElementTree as ET

# --- Constants ---
REPO_ADDON_ID = "repository.sandwichfarm"
REPO_ADDON_VER = "1.0.0"

IGNORES = {".git", "__pycache__", ".mypy_cache", ".pytest_cache", "*.pyc"}


def should_exclude(name: str) -> bool:
    """Return True if the file or directory name should be excluded from ZIPs."""
    for pattern in IGNORES:
        if fnmatch.fnmatch(name, pattern):
            return True
    return False


def make_zip(addon_src_dir: str, addon_id: str, addon_ver: str, output_dir: str) -> str:
    """
    Package addon_src_dir into <output_dir>/<addon_id>/<addon_id>-<addon_ver>.zip
    Top-level directory in ZIP is always <addon_id>/.
    Returns the absolute path to the created ZIP.
    arcname MUST be: os.path.join(addon_id, os.path.relpath(full_path, addon_src_dir))
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
    Returns a UTF-8 string with no BOM, \\n line endings, XML declaration on line 1.
    Uses ET.tostring(elem, encoding='unicode') -- NOT encoding='utf-8' (avoids BOM).
    """
    lines = ['<?xml version="1.0" encoding="UTF-8" standalone="yes"?>', "<addons>"]
    for elem in addon_elements:
        # ET.tostring with encoding='unicode' gives a str without BOM or XML declaration
        lines.append("  " + ET.tostring(elem, encoding="unicode"))
    lines.append("</addons>")
    return "\n".join(lines) + "\n"


def write_index_and_checksums(content: str, output_dir: str) -> None:
    """
    Write addons.xml, addons.xml.sha256, addons.xml.md5 -- ATOMICALLY in one call.
    Uses: open(..., 'w', encoding='utf-8', newline='\\n')
    Asserts no BOM in bytes before writing.
    sha256_digest = hashlib.sha256(xml_bytes).hexdigest()
    md5_digest = hashlib.md5(xml_bytes).hexdigest()
    """
    xml_bytes = content.encode("utf-8")

    # Verify no BOM leaked in
    assert not xml_bytes.startswith(b"\xef\xbb\xbf"), "BOM detected -- check encoding"

    # Write addons.xml with explicit utf-8 encoding and LF-only line endings
    with open(os.path.join(output_dir, "addons.xml"), "w", encoding="utf-8", newline="\n") as f:
        f.write(content)

    # Write SHA-256 checksum sidecar
    sha256_digest = hashlib.sha256(xml_bytes).hexdigest()
    with open(os.path.join(output_dir, "addons.xml.sha256"), "w", encoding="utf-8", newline="\n") as f:
        f.write(sha256_digest + "\n")

    # Write MD5 checksum sidecar (backward compat)
    md5_digest = hashlib.md5(xml_bytes).hexdigest()
    with open(os.path.join(output_dir, "addons.xml.md5"), "w", encoding="utf-8", newline="\n") as f:
        f.write(md5_digest + "\n")


def main():
    parser = argparse.ArgumentParser(
        description="Generate Kodi repository artifacts (addons.xml, checksums, ZIPs)"
    )
    parser.add_argument(
        "--plugin-src",
        required=True,
        help="Path to cloned plugin source directory (e.g. vendor/plugin.audio.subsonic)",
    )
    parser.add_argument(
        "--repo-addon-src",
        default="repository.sandwichfarm",
        help="Path to repo addon source directory (default: ./repository.sandwichfarm)",
    )
    parser.add_argument(
        "--output",
        required=True,
        help="Output directory — becomes the gh-pages branch root",
    )
    args = parser.parse_args()

    output_dir = os.path.abspath(args.output)
    os.makedirs(output_dir, exist_ok=True)

    # Create .nojekyll to prevent GitHub Pages from running Jekyll (required for binary ZIPs)
    open(os.path.join(output_dir, ".nojekyll"), "w").close()

    addon_elements = []

    # ------------------------------------------------------------------
    # 1. Process repo addon (repository.sandwichfarm)
    # ------------------------------------------------------------------
    repo_src = os.path.abspath(args.repo_addon_src)
    repo_elem = read_addon_xml(repo_src)
    addon_elements.append(repo_elem)

    copy_addon_assets(repo_src, REPO_ADDON_ID, output_dir)
    make_zip(repo_src, REPO_ADDON_ID, REPO_ADDON_VER, output_dir)

    # Move repo ZIP from <output>/repository.sandwichfarm/ to <output>/ (repo root)
    # Kodi users download this directly from the staging root.
    zip_in_subdir = os.path.join(
        output_dir, REPO_ADDON_ID, f"{REPO_ADDON_ID}-{REPO_ADDON_VER}.zip"
    )
    zip_at_root = os.path.join(output_dir, f"{REPO_ADDON_ID}-{REPO_ADDON_VER}.zip")
    shutil.move(zip_in_subdir, zip_at_root)

    # ------------------------------------------------------------------
    # 2. Process each plugin listed in plugins.json
    # ------------------------------------------------------------------
    plugin_src = os.path.abspath(args.plugin_src)
    plugin_elem = read_addon_xml(plugin_src)
    plugin_id = plugin_elem.get("id")    # e.g. "plugin.audio.subsonic"
    plugin_ver = plugin_elem.get("version")  # e.g. "3.1.0"
    addon_elements.append(plugin_elem)

    copy_addon_assets(plugin_src, plugin_id, output_dir)
    make_zip(plugin_src, plugin_id, plugin_ver, output_dir)

    # ------------------------------------------------------------------
    # 3. Build and write addons.xml + both checksum sidecars (atomic)
    # ------------------------------------------------------------------
    content = build_addons_xml(addon_elements)
    write_index_and_checksums(content, output_dir)

    print(f"Generated: {output_dir}")
    print(f"  addons.xml -- {len(addon_elements)} addons")
    print(f"  addons.xml.sha256")
    print(f"  addons.xml.md5")
    print(f"  {REPO_ADDON_ID}-{REPO_ADDON_VER}.zip (at root)")
    print(f"  {plugin_id}/{plugin_id}-{plugin_ver}.zip")


if __name__ == "__main__":
    main()
