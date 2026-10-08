#!/usr/bin/env python3
"""
OEM-style Minolta front lens cap: rigid shell + inward-pinch spring clip.

Matches the classic Maxxum / LF-1349 architecture described by repair docs and
replacement-spring makers (Philip Stanz, Interesting_Bear_184, Photrio):

  - Squeeze the two end pads inward
  - Side arches retract from the 49×0.75 filter thread
  - Release → arches spring outward and lock in the thread

Target lens: Minolta AF 50mm f/1.7 (Maxxum 5000 kit), filter Ø49 mm, P=0.75.
"""

from __future__ import annotations

import math
from pathlib import Path

import cadquery as cq

FILTER = 49.0
PITCH = 0.75
MINOR = FILTER - 1.082532 * PITCH  # ~48.188

# Shell (lid) — typical 49 mm Minolta front cap envelope
SHELL_OD = 54.6
SHELL_ID = 51.6  # spring seat bore
FACE_T = 1.8
RIM_H = 6.2
LIP_ID = MINOR - 0.35  # short lip that pilots into the filter bore (~47.8)

# Spring clip — dual side arches + two pinch pads
# Expanded tip OD must exceed filter major to catch thread
ARCH_TIP_OD = FILTER + 0.70  # ~49.7 locked
# Compressed tip OD must clear filter minor to insert/remove
ARCH_COMPRESSED_OD = MINOR - 0.9  # ~47.3
ARCH_THICK = 1.35
ARCH_H = 2.4
PAD_W = 9.0
PAD_T = 2.2
SPRING_Z = 1.35  # height of arch centerline from open end

OUT = Path(__file__).resolve().parent / "stl" / "oem_spring"


def make_shell() -> cq.Workplane:
    r_out = SHELL_OD / 2
    r_seat = SHELL_ID / 2
    r_lip = LIP_ID / 2

    # Outer cylinder + face
    shell = cq.Workplane("XY").circle(r_out).extrude(RIM_H + FACE_T)

    # Hollow seat for spring (from open end up to underside of face)
    shell = (
        shell.faces("<Z").workplane()
        .circle(r_seat)
        .cutBlind(-(RIM_H - 0.2))
    )

    # Pilot lip (smaller ring) that enters filter minor diameter
    # Rebuild open end: add inner lip ring by cutting a step
    # Cut center through lip region so glass is clear, leave annular lip wall
    shell = (
        shell.faces("<Z").workplane()
        .circle(r_lip - 0.9)
        .cutBlind(-(RIM_H - 0.2))
    )

    # Two slots in the face for pinch pads to protrude / be pressed
    for ang in (0, 180):
        slot = (
            cq.Workplane("XY")
            .transformed(rotate=(0, 0, ang), offset=(SHELL_OD / 2 - 6.5, 0, RIM_H + FACE_T / 2))
            .box(8.5, PAD_W + 0.6, FACE_T + 0.4, centered=True)
        )
        shell = shell.cut(slot)

    # Retention ledges inside seat so spring clips under the face (two rails)
    # Implemented as thin rings interrupted — use two opposite shelves
    for ang in (90, 270):
        ledge = (
            cq.Workplane("XY")
            .transformed(rotate=(0, 0, ang), offset=(0, 0, RIM_H - 0.55))
            .box(SHELL_ID - 1.0, 4.0, 0.7, centered=(True, True, False))
        )
        # keep only outer portion of ledge (cut center)
        ledge = ledge.cut(cq.Workplane("XY").circle(r_lip + 0.5).extrude(RIM_H + FACE_T))
        shell = shell.union(ledge)

    # Face recess / logo well
    shell = (
        shell.faces(">Z").workplane()
        .circle(14)
        .cutBlind(-0.55)
    )

    shell = shell.edges("<Z").chamfer(0.35)
    return shell


def make_spring() -> cq.Workplane:
    """
    Dual-arch spring: two outward locking arches on Y axis,
    two pinch pads on X axis. Squeezing pads reduces arch OD.
    """
    tip_r = ARCH_TIP_OD / 2
    mid_r = (FILTER + MINOR) / 4  # ~24.3
    pad_r = SHELL_ID / 2 - 1.2

    # Build as a 2D profile extruded, then add pads
    # Approximate OEM "racetrack" spring with four arcs
    def arc_pts(r, a0, a1, n=24):
        pts = []
        for i in range(n + 1):
            a = math.radians(a0 + (a1 - a0) * i / n)
            pts.append((r * math.cos(a), r * math.sin(a)))
        return pts

    # Outer path: large radius at arch tips (±Y), smaller near pads (±X)
    # Use ellipse-like: r(theta) = tip on Y, slightly less on X for pad seats
    outer = []
    inner = []
    n = 96
    for i in range(n):
        a = 2 * math.pi * i / n
        # Arch peaks at 90° and 270° (Y)
        # Blend: tip_r at Y, (tip_r - 0.9) at X so pads sit inward
        w = abs(math.sin(a))  # 1 at Y, 0 at X
        r_o = (tip_r - 0.85) + 0.85 * w
        r_i = r_o - ARCH_THICK
        outer.append((r_o * math.cos(a), r_o * math.sin(a)))
        inner.append((r_i * math.cos(a), r_i * math.sin(a)))

    # CadQuery wire from outer then reverse inner
    pts = outer + list(reversed(inner))
    spring = (
        cq.Workplane("XY")
        .transformed(offset=(0, 0, SPRING_Z - ARCH_H / 2))
        .polyline(pts)
        .close()
        .extrude(ARCH_H)
    )

    # Pinch pads at ±X — thick tabs you squeeze inward
    for sign in (1, -1):
        pad = (
            cq.Workplane("XY")
            .transformed(offset=(sign * (pad_r - 1.0), 0, SPRING_Z - ARCH_H / 2))
            .box(PAD_T + 1.2, PAD_W, ARCH_H + 1.6, centered=(True, True, False))
            .edges("|Z").fillet(0.5)
        )
        spring = spring.union(pad)

        # Raised finger bumps that poke through shell face slots
        bump = (
            cq.Workplane("XY")
            .transformed(offset=(sign * (SHELL_OD / 2 - 6.0), 0, RIM_H - 0.2))
            .box(3.2, PAD_W - 1.2, FACE_T + 1.0, centered=(True, True, False))
            .edges(">Z").fillet(0.4)
        )
        spring = spring.union(bump)

    # Lead-in chamfers on arch outer bottom edges (approximate with bottom cone cut)
    lead = (
        cq.Workplane("XY")
        .circle(tip_r + 1)
        .circle(tip_r - 0.55)
        .extrude(SPRING_Z - 0.15)
    )
    # Cut a taper from outside: use a larger cone-ish box ring — skip if fragile
    # Instead chamfer bottom outer edges of spring body
    try:
        spring = spring.edges("<Z").chamfer(0.35)
    except Exception:
        pass

    return spring


def export_all(out_dir: Path = OUT) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    shell = make_shell()
    spring = make_spring()

    shell_p = out_dir / "minolta_49mm_oem_shell.stl"
    spring_p = out_dir / "minolta_49mm_oem_spring_clip.stl"
    prev_p = out_dir / "minolta_49mm_oem_PREVIEW_assembled.stl"

    cq.exporters.export(shell, str(shell_p))
    cq.exporters.export(spring, str(spring_p))
    cq.exporters.export(shell.union(spring), str(prev_p))

    print("Exported OEM-style shell + spring:")
    for p in (shell_p, spring_p, prev_p):
        print(f"  {p} ({p.stat().st_size} bytes)")
    print(f"Filter {FILTER}×{PITCH}  minor={MINOR:.3f}")
    print(f"Arch tip OD locked≈{ARCH_TIP_OD:.2f}  compressed target≈{ARCH_COMPRESSED_OD:.2f}")
    print("Print shell in PLA/PETG; spring in PETG 100% infill, 0.12–0.16 mm layers.")


if __name__ == "__main__":
    export_all()
