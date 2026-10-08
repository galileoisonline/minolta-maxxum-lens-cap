#!/usr/bin/env python3
"""
Center-pinch front lens cap for Minolta Maxxum AF 50mm f/1.7 (49×0.75).

Two-part assembly matching OEM LF-1349-style behavior:
  - Squeeze the two pads inward → locking tabs retract → insert/remove
  - Release → tabs spring outward into the filter thread and lock

Requires CadQuery (OpenCascade). Example:
  /tmp/cqvenv/bin/python generate_pinch_cap.py
"""

from __future__ import annotations

from pathlib import Path

import cadquery as cq

# ---------------------------------------------------------------------------
# Research-backed dimensions (see docs/DIMENSIONS.md)
# ---------------------------------------------------------------------------

FILTER_MM = 49.0
PITCH = 0.75
# ISO 724 basic minor diameter of internal thread ≈ d − 1.082532·P
FILTER_MINOR = FILTER_MM - 1.082532 * PITCH  # ~48.188
FILTER_MAJOR = FILTER_MM  # 49.0

# Cap envelope (typical 49 mm center-pinch OEM/aftermarket: ~54–55 OD, ~8–9 tall)
OUTER_OD = 54.8
FACE_T = 2.0
SKIRT_H = 5.8  # insertion depth into filter barrel
TOTAL_H = FACE_T + SKIRT_H

# Plug that enters the filter bore (must clear minor diameter when pinched)
PLUG_OD = FILTER_MINOR - 0.55  # ~47.64 — clearance into female thread

# Locking tab tip radius when at rest (locks in thread groove / major)
TAB_TIP_OD = FILTER_MAJOR + 0.55  # ~49.55 — positive engagement
TAB_WIDTH = 7.0
TAB_THICK = 1.6
TAB_LEAD_ANGLE = 28  # degrees — push-on install without pinching
TAB_Z0 = 1.1  # height of tab from open end (engages first thread)
TAB_Z1 = TAB_Z0 + 1.7

# Pinch pad / latch slide
PAD_W = 12.0
PAD_H = 9.5
PAD_T = 1.8
SLIDE_CLEAR = 0.30  # FDM clearance between body guides and latch
PINCH_TRAVEL = 1.35  # mm each side

# Guide channel in body
GUIDE_W = PAD_W + SLIDE_CLEAR
GUIDE_H = 3.2
GUIDE_DEPTH = OUTER_OD / 2 - 4.0

OUT = Path(__file__).resolve().parent / "stl" / "pinch"


def make_body() -> cq.Workplane:
    """Main shell: face + skirt + guide slots + tab windows."""
    r_out = OUTER_OD / 2
    r_plug = PLUG_OD / 2

    # Solid face disk
    body = cq.Workplane("XY").circle(r_out).extrude(TOTAL_H)

    # Hollow the skirt interior (leave face solid)
    body = (
        body.faces(">Z").workplane()
        .circle(r_plug)
        .cutBlind(-(SKIRT_H - 0.15))
    )

    # Outer face finger recess (center well for pinch pads)
    body = (
        body.faces(">Z").workplane()
        .circle(16.5)
        .cutBlind(-0.7)
    )

    # Two opposing guide slots through the face for latch pads (radial)
    # Slot along X, mirrored
    slot = (
        cq.Workplane("XY")
        .transformed(offset=(0, 0, TOTAL_H - 0.05))
        .box(OUTER_OD - 2.0, GUIDE_W, FACE_T + 0.2, centered=(True, True, False))
    )
    body = body.cut(slot)

    # Deeper pocket under face for latch arms (inside skirt)
    pocket = (
        cq.Workplane("XY")
        .transformed(offset=(0, 0, FACE_T - 0.1))
        .box(PLUG_OD - 1.0, GUIDE_W + 0.4, SKIRT_H, centered=(True, True, False))
    )
    body = body.cut(pocket)

    # Tab exit windows in plug wall (where teeth poke into filter threads)
    for rot in (0, 180):
        win = (
            cq.Workplane("XY")
            .transformed(rotate=(0, 0, rot), offset=(r_plug - 0.2, 0, TAB_Z0 - 0.15))
            .box(3.5, TAB_WIDTH + 0.5, TAB_Z1 - TAB_Z0 + 0.5, centered=(False, True, False))
        )
        body = body.cut(win)

    # Light outer chamfer on open rim for print / mate
    body = body.edges("<Z").chamfer(0.4)

    return body


def make_latch(side: str = "pos") -> cq.Workplane:
    """
    One pinch latch: finger pad + radial slide + locking tooth + flexure spring.

    Coordinate system: pad centered near +X; tooth points +X (outward).
    Print two: one as-is, one rotated 180° in the body (or export mirrored).
    """
    sign = 1.0 if side == "pos" else -1.0

    # Finger pad sitting in face recess
    pad_x = 8.5 * sign
    pad = (
        cq.Workplane("XY")
        .transformed(offset=(pad_x, 0, TOTAL_H - PAD_T))
        .box(PAD_H, PAD_W - 0.4, PAD_T, centered=(True, True, False))
        .edges(">Z").fillet(0.6)
    )

    # Radial slide bar under the face
    slide_len = 14.0
    slide_x = (6.0) * sign
    slide = (
        cq.Workplane("XY")
        .transformed(offset=(slide_x, 0, FACE_T - 0.05))
        .box(slide_len, GUIDE_W - SLIDE_CLEAR - 0.15, 2.4, centered=(True, True, False))
    )

    # Vertical post connecting slide to tooth inside the plug
    post = (
        cq.Workplane("XY")
        .transformed(offset=((PLUG_OD / 2 - 2.2) * sign, 0, TAB_Z0))
        .box(2.4, TAB_WIDTH - 0.4, FACE_T + 1.0, centered=(True, True, False))
    )

    # Locking tooth — lead-in chamfer on open (bottom) side for push-on install
    tip_r = TAB_TIP_OD / 2
    tooth_root_r = PLUG_OD / 2 - 0.3
    # Approximate tooth as a wedge box protruding past plug OD
    tooth_len = tip_r - tooth_root_r + 0.4
    tooth = (
        cq.Workplane("XY")
        .transformed(offset=((tooth_root_r + tooth_len / 2) * sign, 0, TAB_Z0))
        .box(tooth_len, TAB_WIDTH - 0.6, TAB_THICK, centered=(True, True, False))
    )
    # Lead-in: cut a chamfer wedge on the bottom outer edge
    lead = (
        cq.Workplane("XY")
        .transformed(
            offset=((tip_r - 0.1) * sign, 0, TAB_Z0 - 0.05),
            rotate=(0, -TAB_LEAD_ANGLE * sign, 0),
        )
        .box(3.0, TAB_WIDTH, 3.0, centered=(True, True, False))
    )
    tooth = tooth.cut(lead)

    # Flexure spring: curved cantilever biasing latch outward (+X for pos)
    # Anchors near center, arcs toward pad — printed in XY for strength
    spring = (
        cq.Workplane("XY")
        .transformed(offset=(0, 0, FACE_T + 0.2))
        .moveTo(1.5 * sign, (GUIDE_W / 2 - 0.9))
        .threePointArc((6 * sign, GUIDE_W / 2 + 2.5), (11 * sign, GUIDE_W / 2 - 0.6))
        .lineTo(11 * sign, GUIDE_W / 2 - 1.5)
        .threePointArc((6 * sign, GUIDE_W / 2 + 1.5), (1.5 * sign, GUIDE_W / 2 - 1.8))
        .close()
        .extrude(1.4)
    )

    latch = pad.union(slide).union(post).union(tooth).union(spring)
    return latch


def export_all(out_dir: Path = OUT) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)

    body = make_body()
    latch_a = make_latch("pos")
    latch_b = make_latch("neg")

    body_path = out_dir / "minolta_49mm_pinch_cap_body.stl"
    latch_path = out_dir / "minolta_49mm_pinch_latch.stl"  # print ×2 (or use both)
    latch_b_path = out_dir / "minolta_49mm_pinch_latch_mirror.stl"

    cq.exporters.export(body, str(body_path))
    cq.exporters.export(latch_a, str(latch_path))
    cq.exporters.export(latch_b, str(latch_b_path))

    # Assembled preview (latches in locked / outward position)
    preview = body.union(latch_a).union(latch_b)
    preview_path = out_dir / "minolta_49mm_pinch_cap_PREVIEW_assembled.stl"
    cq.exporters.export(preview, str(preview_path))

    print("Exported:")
    for p in (body_path, latch_path, latch_b_path, preview_path):
        print(f"  {p}  ({p.stat().st_size} bytes)")
    print()
    print(f"Filter: {FILTER_MM}×{PITCH}  minor≈{FILTER_MINOR:.3f}")
    print(f"Plug OD: {PLUG_OD:.2f}  Tab tip OD: {TAB_TIP_OD:.2f}")
    print(f"Pinch travel target: {PINCH_TRAVEL:.2f} mm/side")
    print("Print: 1× body + both latches (or 2× identical if you mirror in slicer).")


if __name__ == "__main__":
    export_all()
