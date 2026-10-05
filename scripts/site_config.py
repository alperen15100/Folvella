"""Central site configuration for Folvella builds."""
import json
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
BRAND = json.loads((ROOT / "data/brand.json").read_text(encoding="utf-8"))
BASE = BRAND["siteBase"].rstrip("/") + "/"
LEGACY_BASES = tuple(x.rstrip("/") + "/" for x in BRAND.get("legacySiteBases", []))
parsed = urlparse(BASE)
assert parsed.scheme == "https" and parsed.netloc, "siteBase must be an absolute https URL"
BASE_PATH = parsed.path if parsed.path.endswith("/") else parsed.path + "/"
