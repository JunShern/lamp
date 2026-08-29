# CAD

`lamp_preview.py` — parametric massing model of the lamp, runnable headless
with Blender-as-a-module (`pip install bpy`). Builds the whole lamp in the
neutral pose from a single PARAMS dict (same joint angles as
`../assets/emotes.json`), renders design-review images (Workbench engine)
in three MicroDuck-inspired colourways, and exports massing STLs.

- `renders/` — design review renders
- `preview_stl/` — **massing shells only** — proportions and silhouettes for
  review, NOT print-ready engineering parts (no servo pockets, walls,
  fasteners, or clearances yet; those come in Phase 3)

Run: `python3 cad/lamp_preview.py`
