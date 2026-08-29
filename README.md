# Lamp

A Pixar-style animatronic desk lamp: silent, expressive, and alive.

It listens (mic array), perceives without a camera (multizone time-of-flight),
thinks (Claude), and answers entirely through **motion**, a **16×16 projected
pixel display**, and **piezo chirps**. No voice, ever — the character is the
interface.

- **Design doc:** [docs/DESIGN.md](docs/DESIGN.md)
- **Bill of materials:** [docs/BOM.md](docs/BOM.md)
- **Status:** concept settled, design phase in progress.

## Repository layout (planned)

```
docs/       design doc, BOM, decisions
assets/     emotes, glyphs, chirps (JSON) — the shared contract
cad/        parametric Blender (bpy) model, renders, massing STLs
sim/        browser simulator (build: python3 sim/build.py)
lamp/       Python engine for the Raspberry Pi (validate: python3 -m lamp.validate)
tests/      pytest suite incl. envelope sweep (python3 -m pytest tests/)
```

The browser simulator and the Python engine implement the same spring/keyframe
physics over the same asset files and are cross-validated against each other —
what you tune in the simulator is what the hardware will do.
