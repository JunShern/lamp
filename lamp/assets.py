"""Load the shared asset files (emotes, glyphs, chirps)."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ASSETS_DIR = ROOT / "assets"


def load_assets(assets_dir: Path | None = None) -> dict:
    d = Path(assets_dir) if assets_dir else ASSETS_DIR
    return {
        "emotes": json.loads((d / "emotes.json").read_text()),
        "glyphs": json.loads((d / "glyphs.json").read_text()),
        "chirps": json.loads((d / "chirps.json").read_text()),
    }
