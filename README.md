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
cad/        parametric Blender (bpy) scripts + exported STLs
sim/        desktop simulator for character/animation work
lamp/       the Python daemon that runs on the Raspberry Pi
```
