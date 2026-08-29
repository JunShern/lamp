#!/usr/bin/env python3
"""Parametric massing model + design renders for the lamp.

Run with Blender-as-a-module (pip install bpy) or inside Blender:
    python3 cad/lamp_preview.py

Outputs:
    cad/renders/*.png        design-review renders (Workbench, studio look)
    cad/preview_stl/*.stl    massing shells (NOT print-ready engineering parts)

Design language (Pollen Robotics MicroDuck-inspired, see docs/DESIGN.md):
matte pastel shell + one warm saturated accent on the mechanical hero parts,
black reserved for optics, articulation honestly visible.

All dimensions in mm and driven by the PARAMS dict; pose uses the same
neutral angles as assets/emotes.json.
"""
import math
import sys
from pathlib import Path

import bpy

ROOT = Path(__file__).resolve().parent.parent
RENDERS = ROOT / "cad" / "renders"
STLS = ROOT / "cad" / "preview_stl"
RENDERS.mkdir(parents=True, exist_ok=True)
STLS.mkdir(parents=True, exist_ok=True)

PARAMS = {
    "base_r": 90, "base_h": 60,
    "link1": 160, "link2": 160,
    "shoulder_z": 104,                 # J2 height above ground
    "arm_r": 13,                       # arm tube radius
    "cap_r": 19, "cap_w": 38,          # joint cap cylinders (over servo)
    "shade_len": 110, "shade_r0": 24, "shade_r1": 54,
    "j2_deg": 70, "j3_deg": -50, "j4_deg": -75,   # neutral pose
}

COLORWAYS = {
    "cream":   {"shell": "F7E6CB", "accent": "F2A33C"},
    "sky":     {"shell": "A9DBE8", "accent": "F2A33C"},
    "graphite":{"shell": "6C6A68", "accent": "F5C242"},
}
BLACK = "1A1714"
DARK_FACE = "241F18"
REC_RED = "E06C4F"


def srgb_to_linear(c: float) -> float:
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def hex_rgba(h: str):
    r, g, b = (int(h[i:i + 2], 16) / 255 for i in (0, 2, 4))
    return (srgb_to_linear(r), srgb_to_linear(g), srgb_to_linear(b), 1.0)


MATS = {}


def mat(name: str, hexcol: str, roughness=0.6, metallic=0.0):
    key = f"{name}-{hexcol}"
    if key not in MATS:
        m = bpy.data.materials.new(key)
        m.diffuse_color = hex_rgba(hexcol)
        m.roughness = roughness
        m.metallic = metallic
        MATS[key] = m
    return MATS[key]


def assign(obj, m):
    obj.data.materials.clear()
    obj.data.materials.append(m)


def bevel(obj, width=3.0, segments=4):
    b = obj.modifiers.new("bevel", "BEVEL")
    b.width = width
    b.segments = segments
    b.limit_method = "ANGLE"
    b.angle_limit = math.radians(40)


def smooth(obj):
    try:
        with bpy.context.temp_override(object=obj, selected_objects=[obj]):
            bpy.ops.object.shade_auto_smooth(angle=math.radians(35))
    except Exception:
        pass


def cyl(name, r, depth, loc, rot=(0, 0, 0), verts=64, m=None, do_bevel=None):
    bpy.ops.mesh.primitive_cylinder_add(radius=r, depth=depth, location=loc,
                                        rotation=rot, vertices=verts)
    o = bpy.context.object
    o.name = name
    if do_bevel:
        bevel(o, do_bevel)
    smooth(o)
    if m:
        assign(o, m)
    return o


def cone(name, r0, r1, depth, loc, rot=(0, 0, 0), m=None, open_ends=False):
    bpy.ops.mesh.primitive_cone_add(radius1=r0, radius2=r1, depth=depth,
                                    location=loc, rotation=rot, vertices=96,
                                    end_fill_type="NOTHING" if open_ends else "NGON")
    o = bpy.context.object
    o.name = name
    bevel(o, 2.5)
    smooth(o)
    if m:
        assign(o, m)
    return o


def torus(name, R, r, loc, rot=(0, 0, 0), m=None):
    bpy.ops.mesh.primitive_torus_add(major_radius=R, minor_radius=r,
                                     location=loc, rotation=rot,
                                     major_segments=72, minor_segments=24)
    o = bpy.context.object
    o.name = name
    smooth(o)
    if m:
        assign(o, m)
    return o


def box(name, dims, loc, rot=(0, 0, 0), m=None, bev=2.0):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc, rotation=rot)
    o = bpy.context.object
    o.name = name
    o.scale = (dims[0] / 2, dims[1] / 2, dims[2] / 2)
    bpy.ops.object.transform_apply(scale=True)
    bevel(o, bev)
    smooth(o)
    if m:
        assign(o, m)
    return o


def v_add(a, b):
    return (a[0] + b[0], a[1] + b[1], a[2] + b[2])


def v_scale(a, s):
    return (a[0] * s, a[1] * s, a[2] * s)


def build_lamp(colorway: str, pose=None):
    cw = COLORWAYS[colorway]
    shell = mat("shell", cw["shell"])
    accent = mat("accent", cw["accent"])
    dark = mat("dark", BLACK, roughness=0.35)
    face = mat("face", DARK_FACE)
    glow = mat("glow", cw["accent"], roughness=0.3)
    rec = mat("rec", REC_RED)

    P = PARAMS
    parts = {}

    # --- base ---
    parts["base_drum"] = cyl("base_drum", P["base_r"], P["base_h"],
                             (0, 0, P["base_h"] / 2), m=shell, do_bevel=8)
    parts["base_ring"] = torus("base_ring", P["base_r"] - 2, 3.0,
                               (0, 0, 12), m=accent)
    parts["yaw_disc"] = cyl("yaw_disc", 40, 12, (0, 0, P["base_h"] + 6),
                            m=accent, do_bevel=3)
    # mic mute switch nub on the rear
    parts["mute_switch"] = box("mute_switch", (14, 10, 10),
                               (-P["base_r"] + 2, 0, 40), m=dark)

    # --- kinematics (x-z plane, same neutral pose as emotes.json) ---
    pose = pose or {}
    j2 = pose.get("j2", P["j2_deg"])
    j3 = pose.get("j3", P["j3_deg"])
    j4 = pose.get("j4", P["j4_deg"])
    a2 = math.radians(j2)
    a23 = math.radians(j2 + j3)
    ah = math.radians(j2 + j3 + j4)
    P2 = (0, 0, P["shoulder_z"])
    d1 = (math.cos(a2), 0, math.sin(a2))
    P3 = v_add(P2, v_scale(d1, P["link1"]))
    d2 = (math.cos(a23), 0, math.sin(a23))
    P4 = v_add(P3, v_scale(d2, P["link2"]))
    dh = (math.cos(ah), 0, math.sin(ah))
    vh = (-math.sin(ah), 0, math.cos(ah))     # perpendicular, in-plane

    # shoulder tower between yaw disc and J2
    parts["shoulder_tower"] = cyl("shoulder_tower", 15, P["shoulder_z"] - P["base_h"] - 8,
                                  (0, 0, (P["shoulder_z"] + P["base_h"] + 8) / 2),
                                  m=shell, do_bevel=2)

    def arm(name, p_from, d, length, ang):
        rot = (0, math.pi / 2 - ang, 0)
        center = v_add(p_from, v_scale(d, length / 2))
        return cyl(name, P["arm_r"], length - 24, center, rot, m=shell, do_bevel=None)

    parts["arm_lower"] = arm("arm_lower", P2, d1, P["link1"], a2)
    parts["arm_upper"] = arm("arm_upper", P3, d2, P["link2"], a23)

    cap_rot = (math.pi / 2, 0, 0)  # axis along Y
    for nm, pos in (("cap_shoulder", P2), ("cap_elbow", P3), ("cap_wrist", P4)):
        parts[nm] = cyl(nm, P["cap_r"], P["cap_w"], pos, cap_rot, m=accent, do_bevel=3)

    # --- head ---
    shade_rot = (0, math.pi / 2 - ah, 0)
    shade_center = v_add(P4, v_scale(dh, P["shade_len"] / 2))
    parts["head_shade"] = cone("head_shade", P["shade_r0"], P["shade_r1"],
                               P["shade_len"], shade_center, shade_rot, m=shell,
                               open_ends=True)
    # cap the narrow end behind the wrist
    parts["shade_backcap"] = cyl("shade_backcap", P["shade_r0"] - 0.5, 4,
                                 v_add(P4, v_scale(dh, 2)), shade_rot, m=shell)
    parts["head_rim"] = torus("head_rim", P["shade_r1"] - 1, 4.5,
                              v_add(P4, v_scale(dh, P["shade_len"] - 2)),
                              shade_rot, m=accent)
    # inner face: dark disc + pixel "face" dots + lens
    face_c = v_add(P4, v_scale(dh, P["shade_len"] - 8))
    parts["head_face"] = cyl("head_face", P["shade_r1"] - 8, 3, face_c,
                             shade_rot, m=face)
    parts["lens"] = cyl("lens", 15, 6, v_add(face_c, v_scale(dh, 3)),
                        shade_rot, m=mat("lensglass", "0B0908", roughness=0.2))
    # pixel dots (two eyes + smile) on the face plane, offset in (y, vh)
    dots = [(-18, 14), (18, 14), (-14, -14), (0, -19), (14, -14)]
    for i, (yy, vv) in enumerate(dots):
        pos = v_add(v_add(face_c, (0, yy, 0)), v_scale(vh, vv))
        parts[f"pix{i}"] = cyl(f"pix{i}", 5.0, 6.0, v_add(pos, v_scale(dh, 3.5)),
                               shade_rot, verts=24, m=glow)
    # ToF window on the rim (looks where the lamp looks)
    tof_pos = v_add(v_add(P4, v_scale(dh, P["shade_len"] - 12)), v_scale(vh, P["shade_r1"] - 6))
    parts["tof"] = box("tof", (14, 18, 7), tof_pos, shade_rot, m=dark, bev=1.5)
    # REC-style listening indicator beside it
    rec_pos = v_add(v_add(P4, v_scale(dh, P["shade_len"] - 26)), v_scale(vh, P["shade_r1"] - 10))
    parts["rec_dot"] = cyl("rec_dot", 3.2, 6, rec_pos, shade_rot, verts=24, m=rec)

    return parts, P4, dh


def setup_scene():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    MATS.clear()
    scene = bpy.context.scene
    scene.render.engine = "BLENDER_WORKBENCH"
    scene.view_settings.view_transform = "Standard"
    sd = scene.display.shading
    sd.light = "STUDIO"
    sd.color_type = "MATERIAL"
    sd.show_shadows = True
    sd.shadow_intensity = 0.22
    sd.show_specular_highlight = False
    sd.show_cavity = True
    sd.cavity_type = "WORLD"
    sd.cavity_ridge_factor = 0.4
    sd.cavity_valley_factor = 0.4
    world = bpy.data.worlds.new("world")
    world.color = (0.72, 0.69, 0.63)
    scene.world = world
    scene.display.light_direction = (0.4, 0.55, 0.75)
    scene.render.resolution_x = 1100
    scene.render.resolution_y = 850
    # backdrop: floor + wall in warm grey
    back = mat("backdrop", "EDE7DB", roughness=0.9)
    bpy.ops.mesh.primitive_plane_add(size=4000, location=(0, 0, -0.5))
    floor = bpy.context.object
    floor.name = "floor"
    assign(floor, back)
    bpy.ops.mesh.primitive_plane_add(size=4000, location=(0, 900, 0),
                                     rotation=(math.pi / 2, 0, 0))
    wall = bpy.context.object
    wall.name = "wall"
    assign(wall, back)
    return scene


def add_camera(scene, loc, target):
    cam_data = bpy.data.cameras.new("cam")
    cam_data.lens = 55
    cam_data.clip_end = 10000
    cam = bpy.data.objects.new("cam", cam_data)
    scene.collection.objects.link(cam)
    cam.location = loc
    tgt = bpy.data.objects.new("target", None)
    scene.collection.objects.link(tgt)
    tgt.location = target
    con = cam.constraints.new("TRACK_TO")
    con.target = tgt
    con.track_axis = "TRACK_NEGATIVE_Z"
    con.up_axis = "UP_Y"
    scene.camera = cam
    return cam, tgt


def render(scene, path):
    scene.render.filepath = str(path)
    bpy.ops.render.render(write_still=True)
    print("rendered", path.name)


def export_stls(parts):
    shells = ["base_drum", "arm_lower", "arm_upper", "head_shade",
              "shoulder_tower", "yaw_disc"]
    for name in shells:
        obj = parts[name]
        bpy.ops.object.select_all(action="DESELECT")
        obj.select_set(True)
        bpy.context.view_layer.objects.active = obj
        bpy.ops.wm.stl_export(filepath=str(STLS / f"{name}.stl"),
                              export_selected_objects=True)
    print("exported", len(shells), "massing STLs")


def main():
    center = (110, 0, 195)
    views = {
        "hero":  ((640, -560, 330), center),
        "side":  ((110, -820, 210), center),
    }
    for colorway in ("cream", "sky", "graphite"):
        scene = setup_scene()
        parts, P4, dh = build_lamp(colorway)
        if colorway == "cream":
            for vname, (loc, tgt) in views.items():
                cam, t = add_camera(scene, loc, tgt)
                render(scene, RENDERS / f"lamp_{colorway}_{vname}.png")
                bpy.data.objects.remove(cam)
                bpy.data.objects.remove(t)
            export_stls(parts)
        else:
            add_camera(scene, *views["hero"])
            render(scene, RENDERS / f"lamp_{colorway}_hero.png")

    # head-up "portrait" — face visible (head tilted to horizontal)
    scene = setup_scene()
    parts, P4, dh = build_lamp("cream", pose={"j4": -20})
    face_c = v_add(P4, v_scale(dh, PARAMS["shade_len"] - 8))
    cam_pos = v_add(v_add(face_c, v_scale(dh, 330)), (0, -130, 40))
    add_camera(scene, cam_pos, face_c)
    render(scene, RENDERS / "lamp_cream_face.png")


if __name__ == "__main__":
    main()
