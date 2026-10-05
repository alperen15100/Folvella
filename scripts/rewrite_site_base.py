"""Rewrite legacy public site URLs in deployable static text files to the configured siteBase."""
from pathlib import Path
from site_config import ROOT, BASE, LEGACY_BASES

EXTENSIONS = {".html", ".xml", ".txt"}
NAMES = {"robots.txt"}
changed = 0

for path in ROOT.rglob("*"):
    if not path.is_file():
        continue
    if path.suffix.lower() not in EXTENSIONS and path.name not in NAMES:
        continue
    if any(part in {".git", ".github", "scripts", "data"} for part in path.parts):
        continue
    text = path.read_text(encoding="utf-8")
    updated = text
    for old in LEGACY_BASES:
        if old != BASE:
            updated = updated.replace(old, BASE)
            updated = updated.replace(
                old.replace(":", "%3A").replace("/", "%2F"),
                BASE.replace(":", "%3A").replace("/", "%2F"),
            )
    if updated != text:
        path.write_text(updated, encoding="utf-8")
        changed += 1

print(f"Rewrote siteBase in {changed} static files -> {BASE}")
