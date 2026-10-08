# Minolta Maxxum 5000 — 49 mm Front Lens Cap (pinch lock)

Redesigned **front** caps for the Maxxum 5000 kit lens (**Minolta AF 50 mm f/1.7**, filter **49 × 0.75**), with an **inward-pinch lock** like the OEM **LF-1349**.

> The older friction push-on STLs in `stl/*.stl` did **not** work well — they are kept only for reference. Use **`stl/oem_spring/`** or **`stl/pinch/`**.

## What lens / what cap

| | |
|--|--|
| Camera | Minolta Maxxum 5000 |
| Kit lens | AF 50 mm f/1.7 |
| Filter thread | **Ø49 mm × 0.75** |
| OEM cap | **LF-1349** |
| Mechanism | Squeeze pads **inward** → tabs/arches retract → insert or remove; release → locks in the filter thread |

Full measurement notes: [`docs/DIMENSIONS.md`](docs/DIMENSIONS.md)

## Print this (recommended): OEM-style shell + spring

Files in [`stl/oem_spring/`](stl/oem_spring/):

| File | Qty | Role |
|------|-----|------|
| `minolta_49mm_oem_shell.stl` | 1 | Outer lid |
| `minolta_49mm_oem_spring_clip.stl` | 1 | Inward-pinch spring that locks in the threads |
| `minolta_49mm_oem_PREVIEW_assembled.stl` | — | Visual only, do not print |

### Print settings

**Shell**

- PLA or PETG, 0.16–0.20 mm layers, 3–4 walls, 15–25% infill  
- Face down on the bed  

**Spring clip (critical)**

- **PETG**, **100% infill**, **0.12–0.16 mm** layers, 3+ walls  
- Seam away from the arch tips  
- No supports if oriented flat  

### Assembly

1. Clean spring seat and pad slots in the shell.  
2. Compress the spring pads slightly and seat the clip under the face ledges.  
3. Pads should sit in the face slots so you can pinch them.  
4. Pinch → push onto the 49 mm filter thread → release to lock.

## Alternate: sliding center-pinch (2 latches)

Files in [`stl/pinch/`](stl/pinch/):

| File | Qty |
|------|-----|
| `minolta_49mm_pinch_cap_body.stl` | 1 |
| `minolta_49mm_pinch_latch.stl` | 1 |
| `minolta_49mm_pinch_latch_mirror.stl` | 1 |

Latches print in PETG; body in PLA/PETG. Slide latches into the body guides so teeth poke through the skirt windows.

## Thread engagement (design intent)

| State | Tip / plug OD | Purpose |
|-------|---------------|---------|
| Pinched | ~47.3–47.8 mm | Clears filter minor Ø ≈ 48.19 mm |
| Locked | ~49.5–49.7 mm | Catches past filter major Ø 49.00 mm |

## Regenerate (optional)

Needs CadQuery (e.g. a venv):

```bash
python3 -m venv .venv
.venv/bin/pip install cadquery
.venv/bin/python generate_oem_spring_cap.py   # recommended
.venv/bin/python generate_pinch_cap.py        # alternate
```

Tune diameters in the script constants if your printer runs oversized/undersized.

## Community parts worth knowing

- [Minolta 49 mm Lens Cap Spring (Printables)](https://www.printables.com/model/927966-minolta-49mm-lens-cap-spring) — replacement spring tested on Maxxum lenses  
- [Front Lens Caps All Sizes — ThomPatterson](https://www.printables.com/model/352819-front-lens-caps-all-sizes) — spring-fit main+inserts, author-tested at 49 mm  
- [Minolta 49 mm lens cap clip](https://www.printables.com/model/1592707-minolta-49mm-lens-cap-clip)

## License

MIT — see [`LICENSE`](LICENSE). Not affiliated with Minolta or Sony.
