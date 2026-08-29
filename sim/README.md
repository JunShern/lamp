# Simulator

Browser-based character sandbox for the lamp. Everything it plays comes from
`../assets/*.json` — the same data the Pi daemon will consume.

- `template.html` — the app, with an `__ASSETS_JSON__` placeholder
- `build.py` — validates the asset files (grid sizes, joint limits, time
  ordering, referenced glyph/chirp names) and inlines them → `dist.html`
- `dist.html` — open in any browser, no server needed

Build: `python3 sim/build.py`
