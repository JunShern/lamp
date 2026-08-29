"""The animation engine: keyframe evaluation, spring dynamics, kinematics.

This is a line-for-line behavioural mirror of the engine in
``sim/template.html``. Constants and formulas must stay in sync — the
cross-check in ``tests/test_engine.py`` (and the browser's own validation
panel) will catch drift. All angles in degrees, lengths in mm, torques in
kg·cm, time in seconds.

Joints: j1 base yaw, j2 shoulder pitch, j3 elbow pitch (relative to lower
arm), j4 head pitch (relative to upper arm), j5 head roll.
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field

JOINTS = ("j1", "j2", "j3", "j4", "j5")

# geometry (mm) — DESIGN.md §4
L1, L2, LH = 160.0, 160.0, 70.0

# spring dynamics — must match sim/template.html
SPRING_K = 170.0
SPRING_ZETA = 0.62
SPRING_C = 2.0 * math.sqrt(SPRING_K) * SPRING_ZETA
VEL_CLAMP = 900.0

# mass model (kg) — DESIGN.md §4.2
M_LOWER_ARM = 0.08
M_ELBOW = 0.11
M_FOREARM = 0.08
M_HEAD = 0.22

# servo envelope — ST3215 @ 12 V
SERVO_NOLOAD_DEG_S = 270.0
SERVO_SPEED_BUDGET = 0.7          # flag emotes using more than 70% of no-load speed
TORQUE_SUSTAINED = 15.0           # kg·cm, 50% of stall
TORQUE_STALL = 30.0


def clamp(v: float, lo: float, hi: float) -> float:
    return min(hi, max(lo, v))


def smoothstep(t: float) -> float:
    return t * t * (3.0 - 2.0 * t)


def eval_track(keys: list[list[float]], t: float) -> float:
    """Piecewise smoothstep interpolation over [time, value] keys."""
    if t <= keys[0][0]:
        return keys[0][1]
    for i in range(1, len(keys)):
        if t <= keys[i][0]:
            t0, v0 = keys[i - 1]
            t1, v1 = keys[i]
            u = 1.0 if t1 == t0 else (t - t0) / (t1 - t0)
            return v0 + (v1 - v0) * smoothstep(u)
    return keys[-1][1]


@dataclass
class Kin:
    elbow: tuple[float, float]
    wrist: tuple[float, float]
    lens: tuple[float, float]
    dir: tuple[float, float]
    rh: float  # head world angle, radians


def forward_kin(pose: dict) -> Kin:
    r2 = math.radians(pose["j2"])
    r23 = math.radians(pose["j2"] + pose["j3"])
    rh = math.radians(pose["j2"] + pose["j3"] + pose["j4"])
    elbow = (L1 * math.cos(r2), L1 * math.sin(r2))
    wrist = (elbow[0] + L2 * math.cos(r23), elbow[1] + L2 * math.sin(r23))
    d = (math.cos(rh), math.sin(rh))
    lens = (wrist[0] + LH * d[0], wrist[1] + LH * d[1])
    return Kin(elbow, wrist, lens, d, rh)


def torques(k: Kin) -> tuple[float, float]:
    """Static gravity torque (kg·cm) about the shoulder (J2) and elbow (J3)."""
    head_x = k.wrist[0] + 35.0 * k.dir[0]
    tq2 = max(0.0, (M_LOWER_ARM * (k.elbow[0] / 2)
                    + M_ELBOW * k.elbow[0]
                    + M_FOREARM * ((k.elbow[0] + k.wrist[0]) / 2)
                    + M_HEAD * head_x) / 10.0)
    tq3 = max(0.0, (M_FOREARM * ((k.wrist[0] - k.elbow[0]) / 2)
                    + M_HEAD * (head_x - k.elbow[0])) / 10.0)
    return tq2, tq3


@dataclass
class SpringRig:
    """Per-joint under-damped springs chasing goal angles."""
    limits: dict
    pose: dict = field(default_factory=dict)
    vel: dict = field(default_factory=dict)

    def __post_init__(self):
        if not self.pose:
            self.pose = {j: 0.0 for j in JOINTS}
        self.vel = {j: 0.0 for j in JOINTS}

    def step(self, goals: dict, dt: float) -> dict:
        for j in JOINTS:
            goal = goals[j]
            if j != "j1":
                goal = clamp(goal, *self.limits[j])
            self.vel[j] += (SPRING_K * (goal - self.pose[j]) - SPRING_C * self.vel[j]) * dt
            self.vel[j] = clamp(self.vel[j], -VEL_CLAMP, VEL_CLAMP)
            self.pose[j] += self.vel[j] * dt
        return self.pose


@dataclass
class EmoteStats:
    name: str
    max_speed: float          # deg/s
    max_speed_joint: str
    max_tq2: float            # kg·cm
    max_tq3: float
    limit_violation: bool

    @property
    def flags(self) -> list[str]:
        f = []
        if self.limit_violation:
            f.append("limit")
        if self.max_speed > SERVO_NOLOAD_DEG_S * SERVO_SPEED_BUDGET:
            f.append("fast")
        if self.max_tq2 > TORQUE_SUSTAINED:
            f.append("torque")
        return f

    @property
    def ok(self) -> bool:
        return not self.flags


def sweep_emote(name: str, emotes_asset: dict, dt: float = 1 / 120) -> EmoteStats:
    """Run one emote from neutral through the spring rig; gather peaks.

    Mirrors ``simulateEmote`` in sim/template.html.
    """
    defn = emotes_asset["emotes"][name]
    neutral = dict(emotes_asset["neutral"])
    limits = emotes_asset["limits"]
    start = {j: (0.0 if j == "j1" else neutral[j]) for j in JOINTS}

    tracks = {}
    for j, keys in defn["tracks"].items():
        tracks[j] = [[0.0, start[j]]] + [list(k) for k in keys]

    rig = SpringRig(limits=limits, pose=dict(start))
    dur = defn["duration"] + 0.7
    max_v, max_vj, max_t2, max_t3, lim = 0.0, "", 0.0, 0.0, False

    t = 0.0
    while t < dur:
        goals = {}
        for j in JOINTS:
            if j in tracks:
                goals[j] = eval_track(tracks[j], min(t, defn["duration"]))
            else:
                goals[j] = start[j]
        rig.step(goals, dt)
        for j in JOINTS:
            if abs(rig.vel[j]) > max_v:
                max_v, max_vj = abs(rig.vel[j]), j
            if j != "j1":
                lo, hi = limits[j]
                if rig.pose[j] < lo - 2.5 or rig.pose[j] > hi + 2.5:
                    lim = True
        tq2, tq3 = torques(forward_kin(rig.pose))
        max_t2, max_t3 = max(max_t2, tq2), max(max_t3, tq3)
        t += dt

    return EmoteStats(name, max_v, max_vj, max_t2, max_t3, lim)


def validate(emotes_asset: dict) -> list[EmoteStats]:
    return [sweep_emote(n, emotes_asset) for n in emotes_asset["emotes"]]
