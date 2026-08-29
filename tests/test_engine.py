"""Engine tests, including known-value kinematics and the envelope sweep."""
import math

import pytest

from lamp.assets import load_assets
from lamp.engine import (JOINTS, eval_track, forward_kin, sweep_emote,
                         torques, validate)


@pytest.fixture(scope="module")
def assets():
    return load_assets()


def test_eval_track_endpoints_and_midpoint():
    keys = [[0.0, 10.0], [1.0, 20.0]]
    assert eval_track(keys, -1) == 10
    assert eval_track(keys, 2) == 20
    assert eval_track(keys, 0.5) == pytest.approx(15.0)   # smoothstep is symmetric


def test_forward_kin_neutral_matches_design_doc(assets):
    n = dict(assets["emotes"]["neutral"])
    n["j1"] = 0
    k = forward_kin(n)
    # DESIGN.md §4 neutral pose: j2=70, j3=-50, j4=-75
    assert k.elbow[0] == pytest.approx(160 * math.cos(math.radians(70)), abs=1e-6)
    assert k.wrist[0] == pytest.approx(205.06, abs=0.05)
    assert k.wrist[1] == pytest.approx(205.07, abs=0.05)
    # torque at neutral ~6.8 kg·cm, as shown in the simulator at rest
    tq2, tq3 = torques(k)
    assert tq2 == pytest.approx(6.85, abs=0.15)
    assert tq3 == pytest.approx(4.45, abs=0.15)


def test_all_emotes_inside_servo_envelope(assets):
    stats = validate(assets["emotes"])
    bad = [f"{s.name}: {'+'.join(s.flags)}" for s in stats if not s.ok]
    assert not bad, f"emotes outside envelope: {bad}"
    assert len(stats) >= 13


def test_hold_emotes_settle_within_limits(assets):
    emotes = assets["emotes"]
    for name, defn in emotes["emotes"].items():
        s = sweep_emote(name, emotes)
        assert not s.limit_violation, name


def test_glyphs_are_16x16(assets):
    for name, gdef in assets["glyphs"]["glyphs"].items():
        rows = gdef["rows"] if isinstance(gdef, dict) else gdef
        extra = set((gdef.get("palette") or {})) if isinstance(gdef, dict) else set()
        assert len(rows) == 16, name
        assert all(len(r) == 16 for r in rows), name
        assert all(set(r) <= {".", "o", "#"} | extra for r in rows), name


def test_emote_glyph_and_chirp_references_resolve(assets):
    glyphs = assets["glyphs"]["glyphs"]
    chirps = assets["chirps"]["chirps"]
    for name, defn in assets["emotes"]["emotes"].items():
        g = defn.get("glyph")
        if g and not g.startswith("@"):
            assert g in glyphs, f"{name}: glyph {g}"
        c = defn.get("chirp")
        if c:
            assert c in chirps, f"{name}: chirp {c}"
