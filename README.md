# Minolta Maxxum 5000 — 49 mm Front Lens Cap (3D Printable)

Parametric front lens caps for the **Minolta Maxxum 5000** kit lenses (and other Minolta AF / Sony A-mount lenses with a **49 mm** filter thread). Includes ready-to-print STL files, a Python generator, and notes on how to design printable fit parts.

## Check your lens first

Look at the front of the lens for `Ø49mm` (or similar). The common Maxxum 5000 kit lenses (AF 50 mm f/1.7, AF 35–70, etc.) use **49 × 0.75** filter threads (ISO 1948 photographic filter series).

If your lens is a different size, regenerate with:

```bash
python3 generate_lens_cap.py --size 52
```

## Ready-to-print files

| File | Fit style | When to use |
|------|-----------|-------------|
| [`stl/minolta_maxxum_49mm_push_on_lens_cap.stl`](stl/minolta_maxxum_49mm_push_on_lens_cap.stl) | Push-on over filter rim | Start here |
| [`stl/minolta_maxxum_49mm_push_on_lens_cap_tight.stl`](stl/minolta_maxxum_49mm_push_on_lens_cap_tight.stl) | Tighter push-on | If the default is loose |
| [`stl/minolta_maxxum_49mm_snap_in_lens_cap.stl`](stl/minolta_maxxum_49mm_snap_in_lens_cap.stl) | Snap bead into threads | Closer to OEM feel; may need tuning |

## Print settings (FDM)

- **Material:** PETG preferred (flex + durability); PLA works for a first fit test
- **Nozzle:** 0.4 mm
- **Layer height:** 0.16–0.20 mm (0.12 mm if you later add real threads)
- **Walls / perimeters:** 3–4
- **Infill:** 15–25%
- **Orientation:** Face down on the bed (open rim up) for a clean outer face
- **Supports:** None for these designs
- **Elephant-foot compensation:** On (helps the open rim stay round)

If the push-on is too tight, lightly sand the inner bead or regenerate with a larger `--size` offset in the script. If too loose, print the `_tight` variant.

## Generator

```bash
python3 generate_lens_cap.py                  # all 49 mm variants
python3 generate_lens_cap.py --size 49 --style push_on
python3 generate_lens_cap.py --size 55 --style all --out ./stl
```

No third-party libraries required (stdlib only).

## Existing community models

These are also worth trying if you prefer a spring-clip OEM style:

- [Front Lens Caps — All Sizes (Printables)](https://www.printables.com/model/352819-front-lens-caps-all-sizes) — spring-fit mains + inserts, includes 49 mm
- [Customized push-on 49 mm Minolta (Thingiverse)](https://www.thingiverse.com/thing:625302)
- [Minolta 49 mm Lens Cap Spring (Printables)](https://www.printables.com/model/927966-minolta-49mm-lens-cap-spring) — replacement spring only
- [Sony A / Minolta AF rear cap (Cults)](https://cults3d.com/en/3d-model/gadget/sony-a-mount-minolta-af-lens-cap) — **rear** lens cap, not front

## Design research

See [`docs/TECHNIQUES.md`](docs/TECHNIQUES.md) for the techniques used to generate printable models like this: CAD approaches, mesh rules, DfAM constraints, fit strategies, and filter-thread standards.

## License

MIT — see [`LICENSE`](LICENSE). Not affiliated with Minolta or Sony.
