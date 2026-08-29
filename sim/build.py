#!/usr/bin/env python3
"""Inline the assets/*.json data into sim/template.html -> sim/dist.html.

The JSON files in assets/ are the single source of truth for emotes, glyphs
and chirps; the simulator and (later) the Pi daemon both consume them.
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def main() -> None:
    assets = {
        "glyphs": json.loads((ROOT / "assets/glyphs.json").read_text()),
        "emotes": json.loads((ROOT / "assets/emotes.json").read_text()),
        "chirps": json.loads((ROOT / "assets/chirps.json").read_text()),
    }
    # sanity checks
    for name, rows in assets["glyphs"]["glyphs"].items():
        assert len(rows) == 16, f"glyph {name}: {len(rows)} rows"
        for i, row in enumerate(rows):
            assert len(row) == 16, f"glyph {name} row {i}: {len(row)} cols"
            assert set(row) <= {".", "o", "#"}, f"glyph {name} row {i}: bad chars"
    limits = assets["emotes"]["limits"]
    for ename, e in assets["emotes"]["emotes"].items():
        for j, keys in e["tracks"].items():
            ts = [k[0] for k in keys]
            assert ts == sorted(ts), f"emote {ename} {j}: keys not time-sorted"
            assert ts[-1] <= e["duration"] + 1e-9, f"emote {ename} {j}: key beyond duration"
            for t, v in keys:
                lo, hi = limits[j]
                if j != "j1":  # j1 tracks are offsets from base yaw
                    assert lo <= v <= hi, f"emote {ename} {j}@{t}: {v} outside {lo}..{hi}"
        if e.get("glyph") and not e["glyph"].startswith("@"):
            assert e["glyph"] in assets["glyphs"]["glyphs"], f"emote {ename}: unknown glyph {e['glyph']}"
        if e.get("chirp"):
            assert e["chirp"] in assets["chirps"]["chirps"], f"emote {ename}: unknown chirp {e['chirp']}"

    template = (ROOT / "sim/template.html").read_text()
    out = template.replace("__ASSETS_JSON__", json.dumps(assets, separators=(",", ":")))
    (ROOT / "sim/dist.html").write_text(out)
    print(f"OK -> sim/dist.html ({len(out)//1024} KB), "
          f"{len(assets['glyphs']['glyphs'])} glyphs, "
          f"{len(assets['emotes']['emotes'])} emotes, "
          f"{len(assets['chirps']['chirps'])} chirps")


if __name__ == "__main__":
    main()
