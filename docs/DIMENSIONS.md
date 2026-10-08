# Lens & Cap Dimensions — Minolta Maxxum 5000

Research notes used for the v2 pinch / OEM-spring redesign.

## Camera kit lens

| Item | Value | Source |
|------|-------|--------|
| Camera | Minolta Maxxum 5000 (α-5000 / Dynax 5000), 1986 | camera-wiki |
| Original kit lens | **Minolta AF 50 mm f/1.7** | camera-wiki |
| Mount | Minolta A / Sony A bayonet | — |
| Filter thread | **Ø49 mm, pitch 0.75 mm** | Minolta specs, ISO 1948 series |
| Max lens diameter | 65.5 mm | Minolta / mhohner |
| Lens length | ~38–46 mm (focus extension) | mhohner / Wikipedia |
| Weight | ~170–186 g | specs |
| OEM front cap P/N | **LF-1349** (49 mm front) | KEH / Minolta accessory lists |

Confirm on your glass: the front ring should read something like `Ø49mm` or `49mm`.

## Filter thread geometry (what the cap must grip)

Photographic filter threads follow the ISO metric profile (ISO 68 / ISO 724 family) in the ISO 1948 size series.

For **49 × 0.75**:

| Parameter | Formula / value |
|-----------|-----------------|
| Major diameter \(d\) | **49.00 mm** |
| Pitch \(P\) | **0.75 mm** |
| Pitch diameter | \(d - 0.649519\,P\) ≈ **48.513 mm** |
| Minor diameter (internal flat crest) | \(d - 1.082532\,P\) ≈ **48.188 mm** |

Functional meaning for a front cap:

1. The cap’s **pilot / plug** must fit inside the female filter bore → OD ≲ minor (~48.2 mm) when latches are retracted.
2. The **locking teeth / spring arches** must expand into the thread → tip OD ≳ major (~49.0 mm) when released.
3. A **lead-in chamfer** on the teeth lets you push the cap on without pinching first (OEM behavior).
4. Keep the face clear of the front element — typical AF 50/1.7 filter-stack depth leaves a few mm; designs here keep insertion ~5–6 mm and open in the center.

## OEM LF-1349 mechanism (what “inward push” means)

Maxxum-era Minolta front caps are **not** friction push-ons. They use an internal sprung latch:

- Two opposing pads stick up through the lid (side / near-center pinch).
- **Squeeze pads inward** → spring arches retract from the filter thread.
- **Release** → arches expand into the thread and lock the cap.
- The plastic spring is the famous failure point (Photrio repair threads; Printables replacement springs by Philip Stanz et al., tested on Maxxum 35–70 and 70–210).

Typical aftermarket / OEM 49 mm center-pinch envelope (commercial listings):

| Envelope | Approx. |
|----------|---------|
| Outer diameter | ~54–55 mm |
| Thickness / height | ~8–9 mm |
| Mass | ~10 g |

## Design targets used in this repo (v2)

### Shared thread targets

| Feature | Target (mm) | Why |
|---------|-------------|-----|
| Plug / lip OD | **47.6–47.8** | Clears minor (48.19) with FDM margin |
| Lock tip OD (rest) | **49.5–49.7** | Positive catch past major 49.0 |
| Lock tip OD (pinched) | **~47.3** | Clears minor for removal |
| Pinch travel / side | **~1.2–1.4** | Comfortable finger squeeze |
| Moving clearance | **0.30** | FDM sliding fit baseline |
| Face OD | **54.6–54.8** | Covers filter rim, OEM-like |
| Skirt / insert depth | **5.8–6.2** | Engages first threads, clears glass |

### Variant A — `stl/oem_spring/` (closest to Minolta)

| Part | File | Notes |
|------|------|-------|
| Shell / lid | `minolta_49mm_oem_shell.stl` | Rigid face + spring seat + pad slots |
| Spring clip | `minolta_49mm_oem_spring_clip.stl` | Dual arches + inward pinch pads |

Print spring in **PETG, 100% infill, 0.12–0.16 mm** layers. Shell can be PLA or PETG.

### Variant B — `stl/pinch/` (sliding center-pinch)

| Part | File | Notes |
|------|------|-------|
| Body | `minolta_49mm_pinch_cap_body.stl` | Guides + tab windows |
| Latch | `minolta_49mm_pinch_latch.stl` + `_mirror.stl` | Pad + tooth + flexure |

Same thread engagement numbers; uses discrete sliding latches instead of one spring ring.

## Why v1 push-on failed

The first STLs were friction / bead push-ons sized for an *outer* slip-over fit. OEM Maxxum caps **insert into** the filter thread and **lock with sprung tabs**. Without inward-pinch retractable teeth sized to minor/major, a solid plastic “cap” either will not enter the bore or will not stay locked.

## If fit is still off after printing

Measure with calipers and change only one parameter in the generators:

1. Printed plug OD vs 48.19 → adjust `PLUG_OD` / `LIP_ID`
2. Tab tip vs 49.0 → adjust `TAB_TIP_OD` / `ARCH_TIP_OD`
3. Pinch feel → spring thickness or `ARCH_THICK`
4. Elephant’s foot on open rim → enable compensation in slicer

## References

- Camera-wiki: [Minolta 5000](https://camera-wiki.org/wiki/Minolta_5000)
- Lens data: [Minolta AF 50/1.7](https://en.wikipedia.org/wiki/Minolta_AF_50mm_f/1.7), [mhohner AF50/1.7 new](https://mhohner.de/sony-minolta/onelens/af50f17new)
- Cap P/N: Minolta **LF-1349**
- Spring failure / repair: [Photrio thread](https://www.photrio.com/forum/threads/minolta-lens-cap-for-the-front-lens-fix-for-broken-spring.203021/)
- Maxxum-tested 49 mm spring: [Printables — Philip Stanz](https://www.printables.com/model/927966-minolta-49mm-lens-cap-spring)
- Proven FDM spring-fit architecture (tested 49 mm): [ThomPatterson — Front Lens Caps All Sizes](https://www.printables.com/model/352819-front-lens-caps-all-sizes)
- ISO 1948 filter thread series; ISO 724 basic metric thread dimensions
