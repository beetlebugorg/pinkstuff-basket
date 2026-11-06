#!/usr/bin/env python3
"""Desiccant basket: build the parts, check the fit, and write the files.
Run with: uv run --no-project --with build123d python model.py

Fit check:
  - The collar touches the jug only near the roof of the groove (the wedge). The wedge must grip.
  - The collar slides down over the jug with no contact until the last few millimetres.
  - The basket sits on the seat of the collar. It goes in from above with no contact.
    It does not touch the jug.
  - The lid is clear of the collar and the basket when it is on. On the way off, the bead
    goes over the ridge (the snap). Higher up, the lid is clear.
  - The bending strain of the lid skirt is below the PLA limit.
Output:
  cad/<part>.step, cad/desiccant-assembly.step
  stl/<part>.stl                each printed part, in its print orientation
  build/mesh/*.stl, build/manifest.json, build/parts.json
"""

import json
import os
import sys

from build123d import Box, Color, Compound, Pos, Rot, export_step, export_stl

import parts as P
import shape as S

HERE = os.path.dirname(os.path.abspath(__file__))
BUILD = os.path.join(HERE, "build")

COLOURS = {"pla": "#f4f4f2", "jug": "#e9a3c0", "steel": "#b8bcc0"}
# The section: the half of the model at +Y, for the side view from -Y.
SECTION = Pos(0, 100 + 0.01, -50) * Box(300, 200, 200)
# The detail: the rim at +X, in the same section, for the close-up of the groove, the seat and the snap.
DETAIL = Pos(S.JUG_W / 2 - 14, 0.01, -15) * Box(26, 30, 29, align=None)


def hex_rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) / 255 for i in (0, 2, 4))


def log(msg):
    print(msg, flush=True)


# The kernel can fail on the intersection of two full parts, and give an empty result. So
# intersect in tiles: 3 x 3 boxes, with cut planes away from the symmetry planes.
TILES = [Pos(x0, y0, -300) * Box(x1 - x0, y1 - y0, 600, align=None)
         for x0, x1 in ((-400, -40.3), (-40.3, 40.7), (40.7, 400))
         for y0, y1 in ((-400, -40.9), (-40.9, 40.1), (40.1, 400))]


def overlap(a, b):
    total = 0.0
    for t in TILES:
        at, bt = a & t, b & t
        if not at.solids() or not bt.solids():
            continue
        common = at & bt
        total += common.volume if common is not None else 0.0
    return total


def print_pose(shape, flip):
    """The part in print orientation, centred on X and Y, on the bed.
    flip True: upside down. flip "end": on its +X end, the open end of the blade slot down."""
    if flip == "end":
        shape = Rot(0, 90, 0) * shape
    elif flip:
        shape = Rot(180, 0, 0) * shape
    bb = shape.bounding_box()
    return Pos(-(bb.min.X + bb.max.X) / 2, -(bb.min.Y + bb.max.Y) / 2, -bb.min.Z) * shape


def strain():
    """Each finger of the lid skirt is a cantilever from the top of the slits. The bead deflects
    it by SNAP at the lever L. A round ring with no slits would have to stretch instead."""
    lever = S.SLIT_TOP - S.SNAP_Z
    return 1.5 * S.LID_SKIRT_T * S.SNAP / lever ** 2 * 100, lever


PRESS = 1.0   # mm: the collar goes this much lower than its seat when you push it on


def wedge_depth(t=S.JUG_T):
    """The depth below the roof of the groove where a wall of thickness t seats."""
    return P.seat_depth(t)


def check(problems):
    collar, basket, lid, jug = P.collar(), P.basket(), P.lid(), P.jug()
    info = {}
    # The collar on the jug. The jug is at its seat: the edge is where the groove is as wide as
    # the wall plus the inner gap. A push of PRESS mm more wedges the wall into the groove.
    seated = overlap(collar, jug)
    if seated > 0.05:
        problems.append(f"the collar touches the jug at the seat: {seated:.2f} mm3")
    grip = overlap(collar, Pos(0, 0, PRESS) * jug)
    if grip < 1.0:
        problems.append("the collar does not grip the jug (no wedge contact)")
    for dz in (1, 3, 6, 9, 12):
        if overlap(Pos(0, 0, dz) * collar, jug) > 0.01:
            problems.append(f"the collar touches the jug {dz} mm above its seat")
    info["collar_grip_mm3"] = round(grip, 1)
    # The basket on the seat.
    if overlap(basket, collar) > 0.05:
        problems.append(f"the basket goes into the collar: {overlap(basket, collar):.2f} mm3")
    if overlap(Pos(0, 0, -0.2) * basket, collar) < 1.0:
        problems.append("the basket does not sit on the seat of the collar")
    if overlap(basket, jug) > 0.01:
        problems.append("the basket touches the jug")
    for dz in (0.3, 2, 5, 10, 20, 40, 60, 80, 90):
        if overlap(Pos(0, 0, dz) * basket, collar) > 0.01:
            problems.append(f"the basket touches the collar {dz} mm above its seat")
            break
    # The lid.
    for name, other in (("collar", collar), ("basket", basket), ("jug", jug)):
        v = overlap(lid, other)
        if v > 0.05:
            problems.append(f"the lid touches the {name}: {v:.2f} mm3")
    h = S.LID_IN - S.BEAD_APEX
    snap = max(overlap(Pos(0, 0, dz) * lid, collar) for dz in (h * 0.5, h, h * 1.5))
    if snap < 1.0:
        problems.append("the lid has no snap: the bead does not go over the ridge")
    for dz in (3, 6, 10, 15):
        if overlap(Pos(0, 0, dz) * lid, collar) > 0.01:
            problems.append(f"the lid touches the collar {dz} mm above its seat")
    # The cutting collar: the ring, the two cartridge plates, the screws and the blade are clear of
    # the jug and of each other. The clamp plate presses the blade. The blade screw and the slot
    # in the clamp plate hold the blade.
    jig, cart, clamp, blade, full, ins = P.jig(), P.cart_base(), P.cart_clamp(), P.blade(), P.jug_full(), P.insert()
    sb, sk = P.screw_base(), P.screw_blade()
    pin = sb + sk
    for name, a, b in (("the ring touches the jug", jig, full), ("the base touches the jug", cart, full),
                       ("the clamp plate touches the jug", clamp, full), ("the base touches the ring", cart, jig),
                       ("the clamp plate touches the ring", clamp, jig), ("the clamp plate touches the base", clamp, cart),
                       ("the blade does not fit the base", cart, blade), ("the blade does not fit the clamp plate", clamp, blade),
                       ("the blade touches the ring", blade, jig),
                       ("the lock screw does not fit the base", sb, cart), ("the lock screw touches the blade", sb, blade),
                       ("the lock screw does not fit the clamp plate", sb, clamp),
                       ("the blade screw does not fit the clamp plate", sk, clamp), ("the blade screw does not fit the base", sk, cart),
                       ("the blade screw does not go through the blade hole", sk, blade), ("the screws touch the ring", pin, jig),
                       ("the inserts touch the blade", ins, blade), ("the inserts touch the clamp plate", ins, clamp)):
        v = overlap(a, b)
        if v > 0.01:
            problems.append(f"{name}: {v:.2f} mm3")
    if overlap(sb, ins) < 1.0 or overlap(sk, ins) < 1.0:
        problems.append("a screw does not reach its insert")
    tip = P.jig_x()["top"] + S.CART_H - S.BLADE_SCREW_L              # the tip of the blade screw
    grip = S.CUT_H - S.BLADE_T / 2 - tip
    if not 3.0 <= grip <= S.INSERT_L or tip < P.jig_x()["top"]:
        problems.append(f"the blade screw goes {grip:.2f} mm into the insert")
    k = P.jig_x()
    uh, vh = k["uh"], k["vh"]
    # The clamp: 0.05 mm down, the plate presses the blade, and it is still clear of the base.
    down = Pos(0, 0, -0.05) * clamp
    if overlap(down, blade) < 0.1:
        problems.append("the clamp plate does not press the blade")
    if overlap(down, cart) > 0.01:
        problems.append("the clamp plate touches the base before the blade")
    # The blade cannot move: 0.3 mm in each direction along and across the edge hits a stop.
    for name, d in (("forward", (-vh[0], -vh[1])), ("back", vh), ("along the edge", uh), ("along the edge", (-uh[0], -uh[1]))):
        moved = Pos(d[0] * 0.3, d[1] * 0.3, 0) * blade
        if overlap(moved, clamp) + overlap(moved, sk) < 0.002:
            problems.append(f"nothing stops the blade {name}")
    if overlap(Pos(1.5, 0, 0) * cart, sb) < 0.1:
        problems.append("the lock screw does not stop the base")
    for dx in (3, 6, 9, 12, 15):
        if overlap(Pos(dx, 0, 0) * cart, jig) > 0.01:
            problems.append(f"the base does not slide out: contact at {dx} mm")
    if overlap(Pos(0, 0, 10) * clamp, cart) > 0.01:
        problems.append("the clamp plate does not lift off")
    gap = S.SPINE_CLR
    if overlap(Pos(13, 0, 0) * blade, full) > 0.01:
        problems.append("the blade does not clear the jug when the base is pulled back 13 mm")
    # The edge must cross both faces of the jug wall, 2 mm or more from the blade ends, with the
    # blade back against the screw and the jug at either side of the ring.
    lim = S.BLADE_L / 2 - 2.0
    worst = []
    for shift in (-S.RING_CLR, 0.0, S.RING_CLR):
        uo, ui = P.edge_crossings(S.BLADE_D, gap, shift)
        if uo is None or ui is None or not (-lim < ui < uo < lim):
            problems.append(f"the edge does not cut through the wall: jug at {shift:+.1f} mm (crossings {uo}, {ui})")
        else:
            worst.append(min(lim - uo, ui + lim))
    info["blade_yaw"] = S.YAW
    info["blade_margin"] = round(min(worst), 1) if worst else 0.0
    eps, lever = strain()
    if eps > S.STRAIN_LIMIT:
        problems.append(f"the lid skirt bends too far: {eps:.2f} % strain")
    info.update({"snap_mm3": round(snap, 1), "strain_pct": round(eps, 2), "lever": lever})
    return collar, basket, lid, jug, info, (jig, cart, clamp, pin, blade, full)


def main():
    problems = []
    collar, basket, lid, jug, info, (jig, cart, clamp, pin, blade, full) = check(problems)
    for p in problems:
        log("  CLASH: " + p)
    if not problems:
        log("  fit check: the collar wedges on the jug, the basket sits on the seat, the lid snaps on. "
            "The install paths are clear.")
    res = P.jug_inner_area() * (S.CUT_H - S.JUG_FLOOR - S.DEPTH) / 1e6
    vol = P.basket_inner_area() * (S.DEPTH - S.FLOOR_T + S.BAND_H) / 1e6
    wd = wedge_depth()
    lo, hi = P.wall_range()
    log(f"  collar: a {S.JUG_T:.1f} mm wall seats {wd:.1f} mm below the roof of the groove; walls from {lo:.1f} to "
        f"{hi:.1f} mm fit. A {PRESS:.0f} mm push gives {info['collar_grip_mm3']} mm3 of wedge overlap")
    log(f"  lid snap: {S.SNAP:.2f} mm, skirt lever {info['lever']:.1f} mm, strain {info['strain_pct']:.2f} % "
        f"(limit {S.STRAIN_LIMIT} %)")
    log(f"  basket: {vol:.2f} L of pellets; brine space below it {res:.2f} L; the floor and the lid plate print as an "
        f"open grid ({S.GRID_PITCH} mm pitch)")
    log(f"  cutting ring: the edge at {S.YAW:.0f} deg cuts through the wall {info['blade_margin']:.1f} mm or more "
        f"from the blade ends (jug off centre), at Z = {S.CUT_H:.0f} mm. The blade screw goes through the blade hole")
    if "--no-export" in sys.argv:
        log("RESULT: " + ("CLASHES" if problems else "OK"))
        return

    mesh_dir = os.path.join(BUILD, "mesh")
    for d in ("cad", "stl", mesh_dir):
        os.makedirs(os.path.join(HERE, d), exist_ok=True)
    for d in (mesh_dir, os.path.join(HERE, "cad"), os.path.join(HERE, "stl")):
        for f in os.listdir(d):
            os.remove(os.path.join(d, f))
    manifest, children, summary = [], [], {"parts": {}}

    def mesh(name, shape, mat, group, tol=0.02):
        export_stl(shape, os.path.join(mesh_dir, name + ".stl"), tolerance=tol, angular_tolerance=0.1)
        manifest.append({"name": name, "file": name + ".stl", "material": mat, "group": group})

    printed = {"collar": (collar, True), "basket": (basket, False), "lid": (lid, True),
               "fit_arc": (P.fit_arc(), True), "jig": (jig, True), "jig_cart": (cart, True), "jig_clamp": (clamp, True)}
    for name, (shape, flip) in printed.items():
        export_step(shape, os.path.join(HERE, "cad", name + ".step"))
        pose = print_pose(shape, flip)
        export_stl(pose, os.path.join(HERE, "stl", name + ".stl"), tolerance=0.01, angular_tolerance=0.08)
        bb = pose.bounding_box()
        summary["parts"][name] = {"size": [round(bb.size.X, 1), round(bb.size.Y, 1), round(bb.size.Z, 1)],
                                  "volume_cm3": round(shape.volume / 1000, 1)}
        log(f"  {name:10s} print size {bb.size.X:5.1f} x {bb.size.Y:5.1f} x {bb.size.Z:4.1f} mm, "
            f"volume {shape.volume / 1000:5.1f} cm3, valid {pose.is_valid}, {len(pose.solids())} solid")

    for name, shape, mat in (("collar", collar, "pla"), ("basket", basket, "pla"), ("lid", lid, "pla"), ("jug", jug, "jug")):
        mesh(name, shape, mat, name)
        mesh("sec_" + name, shape & SECTION, mat, "sec_" + name)
        mesh("det_" + name, shape & DETAIL, mat, "det_" + name, 0.005)
        c = Pos(0, 0, 0) * shape
        c.label, c.color = name, Color(*hex_rgb(COLOURS[mat]))
        children.append(c)
    for name, shape, mat in (("jig", jig, "pla"), ("jig_cart", cart, "pla"), ("jig_clamp", clamp, "pla"), ("screw", pin, "steel"),
                            ("insert", P.insert(), "steel"), ("blade", blade, "steel"), ("jug_full", full, "jug")):
        mesh(name, shape, mat, name)
    export_step(Compound(children=children, label="desiccant"), os.path.join(HERE, "cad", "desiccant-assembly.step"))
    tools = []
    for name, shape, mat in (("cutting_ring", jig, "pla"), ("cartridge_base", cart, "pla"), ("clamp_plate", clamp, "pla"), ("m2_5_screw", pin, "steel"), ("m2_5_insert", P.insert(), "steel"),
                             ("razor_blade", blade, "steel")):
        c = Pos(0, 0, 0) * shape
        c.label, c.color = name, Color(*hex_rgb(COLOURS[mat]))
        tools.append(c)
    export_step(Compound(children=tools, label="cutting_ring"), os.path.join(HERE, "cad", "cutting-ring-assembly.step"))

    summary["fit"] = {**info, "wedge_depth": round(wd, 1), "pellet_l": round(vol, 2), "brine_l": round(res, 2), "wall_range": [round(v, 1) for v in P.wall_range()],
                      "grid_pitch": S.GRID_PITCH}
    with open(os.path.join(BUILD, "parts.json"), "w") as fh:
        json.dump(summary, fh, indent=1)
    with open(os.path.join(BUILD, "manifest.json"), "w") as fh:
        json.dump({"parts": manifest}, fh, indent=1)
    log("RESULT: " + ("CLASHES" if problems else "OK"))


if __name__ == "__main__":
    main()
