# Techniques for Generating Printable Models (Lens Caps & Fit Parts)

This document summarizes the techniques needed to design and generate 3D-printable parts like a Minolta Maxxum front lens cap: from measuring the real interface, through CAD/mesh generation, to FDM design rules and fit iteration.

---

## 1. Pipeline overview

```
Measure interface → Parametric CAD / script → Solid / B-rep or CSG
       → Tessellate to mesh (STL / 3MF)
       → Validate manifold geometry
       → Slice (G-code) with DfAM-aware settings
       → Print → Fit test → Adjust parameters → repeat
```

Printable functional parts almost always need **iteration**. Treat clearances and bead interference as parameters, not one-shot guesses.

---

## 2. Know the physical interface

Before modeling, identify what the part must mate with.

### Front lens cap (this repo)

| Fact | Value / note |
|------|----------------|
| Interface | Photographic filter thread on lens barrel |
| Common Maxxum kit size | **49 × 0.75** mm |
| Standard | ISO 1948 (lens/filter thread series); profile follows ISO metric (ISO 68 / ISO 724 family) |
| Pitch (≈30–86 mm filters) | **0.75 mm** |
| Below ~30 mm | Often 0.5 mm pitch |
| Above ~86 mm | Often 1.0 mm pitch |

For M49 × 0.75-class threads (ISO 724 formulas):

- Major diameter ≈ **49.00 mm**
- Pitch diameter ≈ \(d - 0.649519\,P\) ≈ **48.51 mm**
- Minor diameter (internal flat crest) ≈ \(d - 1.082532\,P\) ≈ **48.19 mm**

You do **not** always need a full thread. Three workable front-cap strategies:

1. **Push-on** — cup slips over the filter rim; internal bead/friction holds it (forgiving on FDM).
2. **Snap / spring clips** — two flexible tabs catch behind the first thread (OEM-like; needs flex + XY orientation).
3. **Screw-in** — model a female 0.75 mm thread with print clearance (precise; needs fine layers).

### Other Maxxum-related caps

- **Rear lens cap / body cap** — Minolta AF / Sony A-mount bayonet (different geometry; flange focal distance 44.5 mm is *not* the cap OD).
- Do not confuse SR/MC/MD (manual) rear caps with AF/A-mount caps.

**Measure when possible:** calipers on filter OD, thread depth, and any outer barrel lip beat nominal assumptions.

---

## 3. CAD approaches that generate printable geometry

### A. Parametric solid CAD (best for fit parts)

Tools: **FreeCAD**, **Fusion 360**, **Onshape**, **CadQuery** (Python + OpenCascade B-rep).

- Model as solids with named parameters: `filter_mm`, `clearance`, `wall`, `bead_height`.
- Export **STEP** for archival, **STL/3MF** for slicing.
- CadQuery STL export controls mesh quality via `tolerance` / `angularTolerance`.

**Why this is preferred:** fillets, exact threads, and Boolean ops stay valid solids; tessellation is a last step.

### B. CSG scripting (OpenSCAD)

- Construct with `difference()`, `union()`, `cylinder()`, etc.
- Great for fully parametric public models (`.scad` + Customizer).
- Critical rule: subtracted volumes must **extend past** the stock (not merely touch faces), or export fails with *“Object isn't a valid 2-manifold!”*
- Coincident/tangent faces that only touch (no overlap) also break manifold export.

### C. Direct mesh generation (this repo’s Python script)

- Emit triangles yourself (binary STL).
- Fine for simple lathe-like parts (caps, bushings).
- You are responsible for:
  - Consistent winding / normals
  - Watertight seams between rings
  - No gaps at segment joins
- Harder for true helical threads and complex fillets.

### D. Hybrid community pattern (best OEM-like caps)

Many Printables/Thingiverse lens caps use:

- Rigid **main** cap + separate **spring insert(s)** (PETG / high infill)
- Or FreeCAD spreadsheet parameters for filter size + spring thickness

That splits “stiff shell” from “flexing latch,” which maps well to FDM anisotropy.

---

## 4. Mesh rules the slicer actually requires

A printable mesh must be **manifold** (watertight):

1. Every edge shared by **exactly two** triangles
2. Consistent normals (outward)
3. No self-intersections
4. Positive enclosed volume
5. Prefer a **single** connected solid component per printable body

Validate outside the CAD tool when possible (Meshmixer, `trimesh`, PrusaSlicer warnings, online manifold checkers). Tool self-reports are not always enough.

**Formats:**

| Format | Role |
|--------|------|
| **STL** | Universal triangle soup; no units metadata (assume mm) |
| **3MF** | Preferred modern package; units, multiple bodies, better metadata |
| **STEP** | Exact CAD exchange; not sliced directly |

Units for desktop FDM: **millimeters**.

Tessellation: enough segments that a Ø50 mm circle is not visibly polygonal (this generator uses ~96–100 segments). In OpenSCAD, raise `$fn` for cylinders that must fit round parts.

---

## 5. Design for Additive Manufacturing (DfAM) — FDM

Rules that decide whether a nice CAD model survives the printer.

### Walls & features (0.4 mm nozzle)

| Target | Guideline |
|--------|-----------|
| Min printable wall | ≥ 1 extrusion width (~0.45 mm) |
| Reliable thin wall | ≥ **2 perimeters** (~0.9 mm) |
| Structural wall (caps) | **1.6–2.0 mm** (3–4 perimeters) |
| Tiny text / logos | Prefer emboss ≥ 0.4–0.5 mm deep/tall |

Align wall thickness to integer multiples of extrusion width when you care about surface quality.

### Overhangs, bridges, orientation

- Unsupported overhangs: aim ≤ **45–60°** from vertical (machine-dependent; some printers reach ~75°).
- Short bridges OK; long unsupported floors need supports or a redesign.
- **Print orientation is a design decision:**
  - Cap face on the bed → smooth outer face, rim printed upward
  - Snap arms should flex in the **XY** plane when possible — FDM is weaker across layer lines (Z)
- Prefer **chamfers** on bed-facing edges over large downward fillets (fillets create steep unsupported curves).

### Material choice for caps

| Material | Use |
|----------|-----|
| **PLA** | Fast fit prototypes; brittle snaps |
| **PETG** | Better for springs, beads, repeated on/off |
| **TPU** | Soft push-on / bumper rings (often multi-part) |
| **ASA / ABS** | Outdoor / heat; more shrinkage → retune fits |

Spring clips: print in PETG, high perimeter count, often **100% infill** on the flexure.

---

## 6. Fit engineering (the hard part)

There is no universal clearance. Start from process baselines, then print a test.

### Clearance baselines (assembly gaps)

| Process | Typical starting clearance |
|---------|----------------------------|
| FDM | ~**0.5 mm** for sliding fits; tighter after calibration |
| SLA / SLS / MJF | ~**0.3 mm** |

Prusa notes ~0.2 mm machine accuracy class, but filament shrinkage and elephant’s foot add error. Use elephant-foot compensation so the open rim of a cap stays circular.

### Strategies for lens caps

**Push-on (forgiving)**

- Cavity ID ≈ filter major + **1.5–2.5 mm**
- Internal retention bead slightly tighter (e.g. major + **1.0–1.5 mm**)
- Lead-in chamfer / ramp so the bead flexes on
- This repo’s defaults for 49 mm: cavity ≈ 51.2 mm ID, bead ≈ 50.4 mm ID

**Snap / cantilever**

- Long, tapered beams; fillet the root (≥ ~0.5× root thickness)
- Gentle entry ramp, sharper retaining face
- Deflection in XY; avoid bending across layers
- Locating lugs share shear load

**Screw-in thread (FDM)**

- Prefer coarse, large diameters (filter threads at 49 mm are printable with care)
- Layer height ≤ pitch / 4 when possible (0.75 mm pitch → ≤ 0.2 mm, better 0.12–0.16 mm)
- Add diameter clearance: internal thread oversized ~**0.2–0.4 mm**, or external undersized ~**0.1–0.2 mm**
- Print thread axis **vertical**
- Chamfer thread starts
- PETG is grippier than PLA — needs more clearance

### Iteration workflow

1. Print the looser variant first.
2. Measure with calipers (printed ID vs design ID).
3. Change **one parameter** (bead ID or clearance).
4. Keep a size ladder: loose / nominal / tight STLs (as in this repo).

Parametric source (OpenSCAD, FreeCAD spreadsheet, CadQuery, or this Python script) makes that cheap.

---

## 7. Geometry construction patterns for a cap

A typical printable front cap is a **solid of revolution** plus optional local flexures:

1. **Face disk** — closes the optical path; optional finger recess
2. **Outer skirt** — grip texture (knurls / flats); wall ≥ 1.6 mm
3. **Inner cavity** — clears glass / filter rim
4. **Retention feature** — bead, clips, or thread
5. **Lead-in** — chamfer so assembly does not scrape threads

Boolean recipe (CSG / CAD):

```text
outer_cylinder
  − inner_bore
  − (optional) face_recess
  ∪ retention_bead or clip_bodies
  − cleanup_chamfers
```

Keep a single outer shell; avoid zero-thickness sheets and non-manifold “surface only” models.

---

## 8. Toolchain checklist

| Stage | Tools | Check |
|-------|-------|-------|
| Design | FreeCAD, Fusion, OpenSCAD, CadQuery, Python mesh | Parameters for size & clearance |
| Export | STL / 3MF | mm units, sufficient tessellation |
| Repair | PrusaSlicer, Meshmixer, `trimesh` | Manifold, one body |
| Slice | PrusaSlicer, Bambu Studio, Cura | Orientation, walls, elephant foot |
| Verify | Calipers + fit on real lens | Adjust parameters |

---

## 9. How this repo maps to the techniques

| Technique | Implementation here |
|-----------|---------------------|
| Parametric size | `--size` in `generate_lens_cap.py` |
| Push-on + bead | Default and `_tight` STLs |
| Snap bead | `snap_in` STL |
| Manifold mesh | Closed ring/tube/disk triangulation |
| DfAM walls | ~1.8 mm outer wall, grip flats |
| Print orientation | Designed face-down friendly (flat top) |
| Iteration | Loose / tight variants instead of one magic fit |

For production-quality OEM clones, prefer **solid CAD + spring insert** (FreeCAD/Printables parametric caps) or CadQuery with real thread helpers. Direct STL scripts are ideal for quick, dependency-free push-on protectors.

---

## 10. References

- [Prusa Knowledge Base — Modeling with 3D printing in mind](https://help.prusa3d.com/article/modeling-with-3d-printing-in-mind_164135)
- [OpenSCAD manual — STL export / manifold errors](https://en.wikibooks.org/wiki/OpenSCAD_User_Manual/STL_Export)
- [CadQuery — import/export (STL tolerances)](https://cadquery.readthedocs.io/en/latest/importexport.html)
- [Formlabs — Designing 3D printed snap-fits](https://formlabs.com/blog/designing-3d-printed-snap-fit-enclosures/)
- [Protolabs Network — Snap-fit clearances for AM](https://www.hubs.com/knowledge-base/how-design-snap-fit-joints-3d-printing/)
- [Photo SE — Filter thread pitches (ISO 1948 series)](https://photo.stackexchange.com/questions/90951/cutting-lens-filter-accessory-threads)
- [Printables — Front Lens Caps All Sizes](https://www.printables.com/model/352819-front-lens-caps-all-sizes)
- [Printables — Parametric FreeCAD lens cap generator](https://www.printables.com/model/1388014)
- ISO 1948 (photographic lens filter threads), ISO 68 / ISO 724 (metric thread basic profile/dimensions)
