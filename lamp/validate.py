"""CLI: sweep every emote through the physics and report the envelope.

    python3 -m lamp.validate

Exit code 0 when every emote is inside the servo envelope, 1 otherwise.
"""
import sys

from .assets import load_assets
from .engine import validate


def main() -> int:
    stats = validate(load_assets()["emotes"])
    w = max(len(s.name) for s in stats)
    print(f"{'emote':<{w}}  {'peak speed':>14}  {'shoulder':>9}  {'elbow':>8}  verdict")
    for s in stats:
        verdict = "ok" if s.ok else "+".join(s.flags)
        print(f"{s.name:<{w}}  {s.max_speed:7.1f}°/s {s.max_speed_joint}  "
              f"{s.max_tq2:6.1f} kg·cm  {s.max_tq3:5.1f} kg·cm  {verdict}")
    bad = [s for s in stats if not s.ok]
    print(f"\n{'✓' if not bad else '⚠'} {len(stats) - len(bad)}/{len(stats)} "
          f"emotes inside the servo envelope")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
