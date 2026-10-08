#!/usr/bin/env python3
"""Parametric front lens cap generator for Minolta Maxxum / AF lenses.

Default size is 49 mm (common Maxxum 5000 kit lens: AF 50mm f/1.7, AF 35-70, etc.).
Check the filter size printed on the front of your lens (e.g. Ø49mm) before printing.

Usage:
  python3 generate_lens_cap.py
  python3 generate_lens_cap.py --size 52
  python3 generate_lens_cap.py --size 49 --style push_on_tight
"""

from __future__ import annotations

import argparse
import math
import struct
from pathlib import Path


def vsub(a, b):
    return (a[0] - b[0], a[1] - b[1], a[2] - b[2])


def vcross(a, b):
    return (
        a[1] * b[2] - a[2] * b[1],
        a[2] * b[0] - a[0] * b[2],
        a[0] * b[1] - a[1] * b[0],
    )


def vnorm(a):
    length = math.sqrt(a[0] * a[0] + a[1] * a[1] + a[2] * a[2]) or 1.0
    return (a[0] / length, a[1] / length, a[2] / length)


def tri(a, b, c):
    n = vnorm(vcross(vsub(b, a), vsub(c, a)))
    return (n, a, b, c)


class Mesh:
    def __init__(self):
        self.tris = []

    def add(self, a, b, c):
        self.tris.append(tri(a, b, c))

    def add_quad(self, a, b, c, d):
        self.add(a, b, c)
        self.add(a, c, d)

    def write_stl(self, path: Path, name: str = "lenscap"):
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("wb") as f:
            header = name.encode("ascii", "ignore")[:80].ljust(80, b"\0")
            f.write(header)
            f.write(struct.pack("<I", len(self.tris)))
            for n, a, b, c in self.tris:
                f.write(
                    struct.pack(
                        "<12fH",
                        n[0],
                        n[1],
                        n[2],
                        a[0],
                        a[1],
                        a[2],
                        b[0],
                        b[1],
                        b[2],
                        c[0],
                        c[1],
                        c[2],
                        0,
                    )
                )


def ring_pts(r, z, n):
    return [
        (r * math.cos(2 * math.pi * i / n), r * math.sin(2 * math.pi * i / n), z)
        for i in range(n)
    ]


def add_disk(m: Mesh, r, z, n, up=True):
    c = (0.0, 0.0, z)
    pts = ring_pts(r, z, n)
    for i in range(n):
        j = (i + 1) % n
        if up:
            m.add(c, pts[i], pts[j])
        else:
            m.add(c, pts[j], pts[i])


def add_tube(m: Mesh, r, z0, z1, n, outward=True):
    a = ring_pts(r, z0, n)
    b = ring_pts(r, z1, n)
    for i in range(n):
        j = (i + 1) % n
        if outward:
            m.add_quad(a[i], a[j], b[j], b[i])
        else:
            m.add_quad(a[i], b[i], b[j], a[j])


def add_cone_band(m: Mesh, r0, z0, r1, z1, n, outward=True):
    a = ring_pts(r0, z0, n)
    b = ring_pts(r1, z1, n)
    for i in range(n):
        j = (i + 1) % n
        if outward:
            m.add_quad(a[i], a[j], b[j], b[i])
        else:
            m.add_quad(a[i], b[i], b[j], a[j])


def make_push_on_cap(
    filter_mm: float = 49.0,
    cavity_id: float | None = None,
    bead_id: float | None = None,
    wall: float = 1.8,
    rim_h: float = 7.0,
    face_t: float = 2.0,
    bead_h: float = 1.2,
    bead_z_from_open: float = 1.4,
    recess_d: float = 0.9,
    recess_r_ratio: float = 0.52,
    segs: int = 96,
    rib_depth: float = 0.35,
) -> Mesh:
    """Push-on cap that slips over the filter thread barrel."""
    if cavity_id is None:
        cavity_id = filter_mm + 2.2
    if bead_id is None:
        bead_id = filter_mm + 1.4

    r_cav = cavity_id / 2
    r_bead = bead_id / 2
    r_out = r_cav + wall
    z0 = 0.0
    z1 = rim_h
    z2 = rim_h + face_t
    zb0 = bead_z_from_open
    zb1 = bead_z_from_open + bead_h
    r_rec = max(6.0, r_cav * recess_r_ratio)
    z_rec = z2 - recess_d

    m = Mesh()

    def outer_r(i):
        return r_out - (rib_depth if (i % 2 == 0) else 0.0)

    bot_out = [
        (
            outer_r(i) * math.cos(2 * math.pi * i / segs),
            outer_r(i) * math.sin(2 * math.pi * i / segs),
            z0,
        )
        for i in range(segs)
    ]
    top_out = [
        (
            outer_r(i) * math.cos(2 * math.pi * i / segs),
            outer_r(i) * math.sin(2 * math.pi * i / segs),
            z2,
        )
        for i in range(segs)
    ]
    for i in range(segs):
        j = (i + 1) % segs
        m.add_quad(bot_out[i], bot_out[j], top_out[j], top_out[i])

    bead_bot = ring_pts(r_bead, z0, segs)
    for i in range(segs):
        j = (i + 1) % segs
        m.add_quad(bead_bot[i], bead_bot[j], bot_out[j], bot_out[i])

    add_tube(m, r_bead, z0, zb0, segs, outward=False)
    add_cone_band(m, r_bead, zb0, r_cav, zb1, segs, outward=False)
    add_tube(m, r_cav, zb1, z1, segs, outward=False)
    add_disk(m, r_cav, z1, segs, up=False)

    rec_top = ring_pts(r_rec, z2, segs)
    for i in range(segs):
        j = (i + 1) % segs
        m.add_quad(rec_top[i], top_out[i], top_out[j], rec_top[j])
    add_tube(m, r_rec, z_rec, z2, segs, outward=False)
    add_disk(m, r_rec, z_rec, segs, up=True)
    return m


def make_snap_bead_cap(
    filter_mm: float = 49.0,
    wall: float = 1.7,
    rim_h: float = 5.8,
    face_t: float = 2.0,
    segs: int = 100,
) -> Mesh:
    """Snap-in style with a retention bead that seats in the filter threads."""
    skirt_od = filter_mm - 0.30
    bead_od = filter_mm + 0.50
    r_skirt = skirt_od / 2
    r_bead = bead_od / 2
    r_out = filter_mm / 2 + wall + 1.5
    z0 = 0.0
    zb0 = 1.1
    zb1 = 2.3
    z1 = rim_h
    z2 = rim_h + face_t
    r_rec = r_out * 0.48
    z_rec = z2 - 0.85

    m = Mesh()

    def outer_r(i):
        return r_out - (0.3 if i % 2 == 0 else 0.0)

    bot_out = [
        (
            outer_r(i) * math.cos(2 * math.pi * i / segs),
            outer_r(i) * math.sin(2 * math.pi * i / segs),
            z0,
        )
        for i in range(segs)
    ]
    top_out = [
        (
            outer_r(i) * math.cos(2 * math.pi * i / segs),
            outer_r(i) * math.sin(2 * math.pi * i / segs),
            z2,
        )
        for i in range(segs)
    ]
    for i in range(segs):
        j = (i + 1) % segs
        m.add_quad(bot_out[i], bot_out[j], top_out[j], top_out[i])

    skirt_bot = ring_pts(r_skirt, z0, segs)
    for i in range(segs):
        j = (i + 1) % segs
        m.add_quad(skirt_bot[i], skirt_bot[j], bot_out[j], bot_out[i])

    add_tube(m, r_skirt, z0, zb0, segs, outward=False)
    add_cone_band(m, r_skirt, zb0, r_bead, (zb0 + zb1) / 2, segs, outward=False)
    add_cone_band(m, r_bead, (zb0 + zb1) / 2, r_skirt, zb1, segs, outward=False)
    add_tube(m, r_skirt, zb1, z1, segs, outward=False)
    add_disk(m, r_skirt, z1, segs, up=False)

    rec = ring_pts(r_rec, z2, segs)
    for i in range(segs):
        j = (i + 1) % segs
        m.add_quad(rec[i], top_out[i], top_out[j], rec[j])
    add_tube(m, r_rec, z_rec, z2, segs, outward=False)
    add_disk(m, r_rec, z_rec, segs, up=True)
    return m


def main():
    parser = argparse.ArgumentParser(description="Generate Minolta Maxxum front lens cap STLs")
    parser.add_argument(
        "--size",
        type=float,
        default=49.0,
        help="Filter thread diameter in mm (look for Ø49mm on the lens)",
    )
    parser.add_argument(
        "--style",
        choices=("all", "push_on", "push_on_tight", "snap_in"),
        default="all",
        help="Which variant to generate",
    )
    parser.add_argument(
        "--out",
        type=Path,
        default=Path(__file__).resolve().parent,
        help="Output directory",
    )
    args = parser.parse_args()
    size = args.size
    out: Path = args.out
    out.mkdir(parents=True, exist_ok=True)

    jobs = []
    if args.style in ("all", "push_on"):
        jobs.append(
            (
                f"minolta_maxxum_{int(size)}mm_push_on_lens_cap.stl",
                make_push_on_cap(filter_mm=size),
            )
        )
    if args.style in ("all", "push_on_tight"):
        jobs.append(
            (
                f"minolta_maxxum_{int(size)}mm_push_on_lens_cap_tight.stl",
                make_push_on_cap(
                    filter_mm=size,
                    cavity_id=size + 1.9,
                    bead_id=size + 1.15,
                ),
            )
        )
    if args.style in ("all", "snap_in"):
        jobs.append(
            (
                f"minolta_maxxum_{int(size)}mm_snap_in_lens_cap.stl",
                make_snap_bead_cap(filter_mm=size),
            )
        )

    for name, mesh in jobs:
        path = out / name
        mesh.write_stl(path, name.replace(".stl", ""))
        print(f"Wrote {path} ({len(mesh.tris)} triangles)")


if __name__ == "__main__":
    main()
