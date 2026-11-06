"""Desiccant basket: the printed parts and the context (the cut jug), in build123d.
All parts are made in world coordinates (in use). model.py turns them to print orientation.
A horizontal size is an offset o from the outer face of the jug (see shape.py)."""

import math

from build123d import (Align, Axis, Box, Circle, Cone, Plane, Polygon, Pos, Rectangle, Rot, Sketch, SlotOverall,
                       extrude, loft, revolve)

import shape as S


def rr(o):
    """The circle at offset o from the outer face of the jug."""
    return Circle(S.JUG_DIA / 2 + o)


def slab(o, z0, z1):
    """A prism of the rounded square at offset o, from z0 to z1."""
    return extrude(Pos(0, 0, z0) * rr(o), z1 - z0, dir=(0, 0, 1))


def frustum(o0, z0, o1, z1):
    """A loft from offset o0 at z0 to offset o1 at z1. Equal steps give 45 deg faces."""
    return loft([Plane.XY.offset(z0) * rr(o0), Plane.XY.offset(z1) * rr(o1)])


def bars(o, width, z0, z1, keep_out):
    """Long slots along X inside the circle at offset o: one row each SLOT_PITCH. The slots stop at
    the cross ribs (X = 0 and X = +-CROSS_X, width keep_out * 2) and skip the rib at Y = 0. Long
    straight bars print fast. Return the cutter and the count."""
    r = S.JUG_DIA / 2 + o
    cuts = [-S.CROSS_X, 0.0, S.CROSS_X]
    faces = []
    n = int((2 * r - width) // S.SLOT_PITCH)
    for i in range(n + 1):
        y = -n * S.SLOT_PITCH / 2 + i * S.SLOT_PITCH
        if abs(y) < keep_out + width / 2 + 0.5:
            continue
        yy = abs(y) + width / 2
        if yy >= r:
            continue
        c = (r * r - yy * yy) ** 0.5
        edges = [-c] + [e for x in cuts if -c < x < c for e in (x - keep_out, x + keep_out)] + [c]
        for a, b in zip(edges[0::2], edges[1::2]):
            if b - a >= 2 * width:
                faces.append(Pos((a + b) / 2, y) * SlotOverall(b - a, width))
    sk = Sketch() + faces
    return extrude(Pos(0, 0, z0) * sk, z1 - z0, dir=(0, 0, 1)), len(faces)


def v_ring(o_face, o_apex, zc):
    """The solid inside a 45 deg V profile: offset o_face at zc +- h, o_apex at zc (h = o_face - o_apex)."""
    h = o_face - o_apex
    return frustum(o_face, zc - h, o_apex, zc) + frustum(o_apex, zc, o_face, zc + h)


# --- Collar ---------------------------------------------------------------------------------

def collar():
    zg, g = S.SNAP_Z, S.SNAP_G
    # The outer profile from the bottom up: the skirt, the snap groove, the ridge, the narrow band.
    body = (slab(S.SKIRT_O, -S.SKIRT_H, zg - g)
            + frustum(S.SKIRT_O, zg - g, S.SKIRT_O - g, zg)
            + frustum(S.SKIRT_O - g, zg, S.SKIRT_O, zg + g)
            + frustum(S.SKIRT_O, zg + g, S.BAND_O, zg + g + (S.SKIRT_O - S.BAND_O))
            + slab(S.BAND_O, zg + g + (S.SKIRT_O - S.BAND_O), S.BAND_H))
    m, hm, hr, z0 = S.G_MID, S.G_HALF_MOUTH, S.G_HALF_ROOF, -S.SKIRT_H
    # Extend both faces 0.1 mm below the mouth, so the cut goes through the bottom face.
    k = (hm - hr) / S.SKIRT_H * 0.1
    groove = (frustum(m + hm + k, z0 - 0.1, m + hr, 0) - frustum(m - hm - k, z0 - 0.1, m - hr, 0))
    body -= groove
    body -= slab(S.A, -S.SKIRT_H - 1, 0.001)
    body -= frustum(S.A, 0, S.A + S.CONE, S.CONE)
    body -= slab(S.A + S.CONE, S.CONE - 0.001, S.BAND_H + 1)
    # Finger notches at both X sides: a 45 deg V from the top of the band.
    h = S.NOTCH_W / 2
    tri = Polygon((-h, S.BAND_H + 0.01), (h, S.BAND_H + 0.01), (0, S.BAND_H - h), align=None)
    notch = extrude(Plane.YZ * tri, S.JUG_W / 2 + 10, both=True)
    body -= notch
    return body


def fit_arc():
    """A short arc of the collar at +X, for the first print."""
    c = collar()
    box = Pos(S.JUG_DIA / 2 - 15, -S.FIT_SIZE / 2, -S.SKIRT_H - 1) * Box(
        25, S.FIT_SIZE, S.SKIRT_H + S.BAND_H + 2, align=None)
    return c & box


# --- Basket ---------------------------------------------------------------------------------

def rim_o():
    """The outer face of the basket rim, above the flare."""
    return S.A + S.CONE - S.RIM_CLR


def wall_slots():
    """The side slots of the basket: vertical, with a 45 deg pointed top. Return the cutter and the count."""
    r = S.JUG_DIA / 2 + S.BASKET_O
    n = int(2 * 3.14159265 * r // S.WSLOT_PITCH)
    w, h = S.WSLOT_W, S.WSLOT_H
    prof = Polygon((-w / 2, 0), (w / 2, 0), (w / 2, h), (0, h + w / 2), (-w / 2, h), align=None)
    one = extrude(Plane.YZ * prof, S.BASKET_T + 2)       # along +X, through the wall
    one = Pos(r - S.BASKET_T - 1, 0, 0) * one
    cutters = []
    for row in range(S.WSLOT_ROWS):
        z = S.WSLOT_Z0 + row * (h + w / 2 + S.WSLOT_GAP)
        shift = 0.5 if row % 2 else 0.0
        for i in range(n):
            cutters.append(Rot(0, 0, 360 / n * (i + shift)) * Pos(0, 0, z) * one)
    from build123d import Compound
    return Compound(children=cutters), n * S.WSLOT_ROWS


def basket():
    ro = rim_o()
    t = S.BASKET_T
    # The flare is on the cone of the collar: o = A + z. It starts at the basket wall.
    z_a = S.BASKET_O - S.A
    z_b = ro - S.A
    outer = (slab(S.BASKET_O, -S.DEPTH, z_a)
             + frustum(S.BASKET_O, z_a, ro, z_b)
             + slab(ro, z_b, S.BAND_H))
    # The inner face follows the flare, so the wall keeps its thickness.
    inner = (slab(S.BASKET_IN, -S.DEPTH + S.FLOOR_T, z_a + 0.001)
             + frustum(S.BASKET_IN, z_a, ro - t, z_b)
             + slab(ro - t, z_b - 0.001, S.BAND_H + 1))
    body = outer - inner
    # The floor ribs: a star of spokes from the centre. The star stops RIB_GAP from the wall, so
    # each layer of the ribs is 2 islands (the wall and the star) with a short travel between them.
    span = S.JUG_DIA + 2 * S.BASKET_IN
    zr = -S.DEPTH + S.FLOOR_T - 0.1
    al = (Align.CENTER, Align.CENTER, Align.MIN)
    ribs = None
    for i in range(S.RIB_SPOKES):
        rib = Rot(0, 0, 180 / S.RIB_SPOKES * i) * Pos(0, 0, zr) * Box(span, S.RIB_T, S.RIB_H + 0.1, align=al)
        ribs = rib if ribs is None else ribs + rib
    body += ribs & slab(S.BASKET_IN - S.RIB_GAP, -S.DEPTH, 0)
    # The floor stays solid in the model. The slicer prints it as an open grid (see GRID_PITCH).
    if S.WSLOT_ROWS:
        body -= wall_slots()[0]
    return body


def floor_slot_count():
    return bars(S.BASKET_IN - S.SLOT_EDGE, S.FLOOR_SLOT, 0, 1, S.RIB_T / 2)[1]


# --- Lid ------------------------------------------------------------------------------------

def lid():
    top = S.BAND_H
    body = slab(S.LID_O, top, top + S.LID_T)
    body += slab(S.LID_O, S.LID_SKIRT_Z0, top + 0.01) - slab(S.LID_IN, S.LID_SKIRT_Z0 - 1, top + 0.001)
    # The bead: the ring between the 45 deg V (apex BEAD_APEX at SNAP_Z) and the skirt face.
    h = S.LID_IN - S.BEAD_APEX
    bead = slab(S.LID_IN + 0.01, S.SNAP_Z - h, S.SNAP_Z + h) - v_ring(S.LID_IN, S.BEAD_APEX, S.SNAP_Z)
    body += bead
    # The pull tab at +Y: a 45 deg wedge at the bottom of the skirt. It follows the curve of
    # the skirt, so the full length of the tab bonds to the skirt.
    r0 = S.JUG_DIA / 2 + S.LID_O - 0.2
    z0 = S.LID_SKIRT_Z0
    wedge = Polygon((r0, z0), (r0 + S.TAB_OUT + 0.2, z0), (r0, z0 + S.TAB_OUT + 0.2), align=None)
    span = math.degrees(S.TAB_W / r0)
    body += Rot(0, 0, 90 - span / 2) * revolve(Plane.XZ * wedge, Axis.Z, span)
    # Slits in the skirt, open at its bottom edge, between the tab and the next finger.
    # The slits go from 1 mm inside the bead to outside the skirt.
    r0 = S.JUG_DIA / 2 + S.BEAD_APEX - 1
    length = S.LID_O - S.BEAD_APEX + 3
    for i in range(S.SLITS):
        a = 360 / S.SLITS * (i + 0.5)
        cut = Pos(r0, 0, S.LID_SKIRT_Z0 - 1) * Box(length, S.SLIT_W, S.SLIT_TOP - S.LID_SKIRT_Z0 + 1,
                                                   align=(Align.MIN, Align.CENTER, Align.MIN))
        body -= Rot(0, 0, a) * cut
    return body             # the plate is an open grid in the print (see GRID_PITCH)


def _vents(body, top):
    cut, _ = bars(S.BASKET_IN - S.VENT_EDGE, S.VENT_SLOT, top - 1, top + S.LID_T + 1, S.CROSS_W / 2)
    return body - cut


def vent_slot_count():
    return bars(S.BASKET_IN - S.VENT_EDGE, S.VENT_SLOT, 0, 1, S.CROSS_W / 2)[1]


# --- Cutting collar -------------------------------------------------------------------------
# The jug axis is the Z axis, Z = 0 on the table. The shelf and the cartridge are at +X.

def jig_x():
    """The cutting collar layout. The blade frame: the origin O is on the edge, at the middle of
    the blade, where the edge crosses the middle of the jug wall. u is along the edge, v goes back
    to the spine. The edge is at YAW to the jug wall."""
    R = S.JUG_DIA / 2
    ri = R + S.RING_CLR
    a = math.radians(S.YAW)
    uh = (math.sin(a), math.cos(a))
    vh = (math.cos(a), -math.sin(a))
    # The ring is printed: its layout (o, pin) uses JIG_BLADE_D, not the newer blade values.
    o = (R - S.JUG_T / 2, S.JIG_BLADE_D * math.sin(a) / 2)   # centres the blade on Y = 0
    hd = S.SCREW_CLR / 2 ** 0.5                                 # half the diagonal of the screw hole
    # The screw shank is 0.05 mm behind the back of the spine (of a JIG_BLADE_D blade).
    pv = S.JIG_BLADE_D + 0.05 + S.SCREW_D / 2
    pin = (o[0] + vh[0] * pv, o[1] + vh[1] * pv)
    corners = [(o[0] + uh[0] * u + vh[0] * v, o[1] + uh[1] * u + vh[1] * v)
               for u in (-39.7 / 2, 39.7 / 2) for v in (0, S.JIG_BLADE_D)]
    out = max(max(c[0] for c in corners) + 3.0, pin[0] + hd + 4.0)
    return {"R": R, "ri": ri, "ro": ri + S.RING_T, "a": a, "uh": uh, "vh": vh, "o": o, "pin": pin, "pv": pv,
            "hd": hd, "out": out, "top": S.CUT_H - S.CART_LOW, "corners": corners}


def blade_frame(k, shape):
    """Move a shape from the blade frame (X = v, Y = u, Z = 0 at the cut) to the world."""
    return Pos(k["o"][0], k["o"][1], S.CUT_H) * Rot(0, 0, -S.YAW) * shape


def v_groove(p0, p1, z, w):
    """A V-groove from p0 to p1 in the face at height z: a square prism at 45 deg about its axis."""
    dx, dy = p1[0] - p0[0], p1[1] - p0[1]
    length = math.hypot(dx, dy)
    ang = math.degrees(math.atan2(dy, dx))
    return Pos((p0[0] + p1[0]) / 2, (p0[1] + p1[1]) / 2, z) * Rot(0, 0, ang) * Rot(45, 0, 0) * Box(length, w, w)


def diamond(side, z0, z1, x, y=0.0):
    """A square prism, set at 45 deg about the Z axis (its corners on X and Y)."""
    sq = Rot(0, 0, 45) * Rectangle(side, side)
    return extrude(Pos(x, y, z0) * sq, z1 - z0, dir=(0, 0, 1))


def box(x0, x1, y0, y1, z0, z1):
    return Pos(x0, y0, z0) * Box(x1 - x0, y1 - y0, z1 - z0, align=None)


def jig():
    """The ring, the shelf and the three legs."""
    k = jig_x()
    zt = k["top"]
    zb = zt - S.RING_H
    body = extrude(Pos(0, 0, zb) * Circle(k["ro"]), S.RING_H)
    body += box(k["R"], k["R"] + S.SHELF_L, -S.SHELF_W / 2, S.SHELF_W / 2, zt - S.SHELF_T, zt)
    # One leg is under the shelf. Its fin goes out under the shelf as a brace. The fin edges
    # slope up and away from the bed in the print (upside down), so they need no support.
    x0 = k["ro"] - 1.0
    xf = x0 + S.LEG_T + S.LEG_FIN
    for a in (0, 120, 240):
        leg = box(x0, x0 + S.LEG_T, -S.LEG_W / 2, S.LEG_W / 2, 0, zt)
        pts = [(x0, 0), (x0 + S.LEG_T + S.FOOT, 0), (xf, S.FOOT_H)]
        if a == 0:
            zs = zt - S.SHELF_T
            pts += [(xf, zs - 10.0), (k["R"] + S.SHELF_L - 2.0, zs), (k["R"] + S.SHELF_L - 2.0, zt)]
        else:
            pts += [(xf, zt)]
        pts += [(x0, zt)]
        leg += extrude(Plane.XZ * Polygon(*pts, align=None), S.FIN_T / 2, both=True)
        body += Rot(0, 0, a) * leg
        for sgn in (1, -1):
            body += brace(k, a, sgn)
    body -= Pos(0, 0, -1) * Cylinder_(k["ri"], S.JUG_H + 2)
    # The hole for the M2.5 heat-set insert goes through the shelf: the melted PLA can flow out.
    body -= Pos(*k["pin"], zt - S.SHELF_T - 1) * Cylinder_(S.INSERT_D / 2, S.SHELF_T + 2)
    return body


def brace(k, a, sgn):
    """A straight strut at 45 deg: from the side of the leg at angle a up to the bottom of the ring.
    The bore cut trims its inner face. In the print (upside down) its lower face is at 45 deg."""
    rc = k["ro"] + 1.0
    zb = k["top"] - S.RING_H
    a1 = math.radians(a) + sgn * (S.LEG_W / 2) / rc
    a2 = a1 + sgn * S.BRACE_REACH / rc
    p1 = (rc * math.cos(a1), rc * math.sin(a1), zb + 2.0 - S.BRACE_REACH)
    p2 = (rc * math.cos(a2), rc * math.sin(a2), zb + 2.0)
    d = tuple(q - p for p, q in zip(p1, p2))
    length = math.sqrt(sum(c * c for c in d))
    am = (a1 + a2) / 2
    mid = tuple((p + q) / 2 for p, q in zip(p1, p2))
    pl = Plane(origin=mid, x_dir=d, z_dir=(math.cos(am), math.sin(am), 0))
    return pl * Box(length + 6.0, S.BRACE_W, S.BRACE_T)


def blade_hole_xy(k):
    """The centre of the slot hole in the blade, in the world (the blade screw axis)."""
    vb = S.BLADE_D - S.HOLE_C
    return (k["o"][0] + k["vh"][0] * vb, k["o"][1] + k["vh"][1] * vb)


def cart_base():
    """The base of the cartridge. It sits on the ring top and the shelf. The cheeks go down beside
    the shelf. The top is flat: the blade lies on it. A V-groove takes the lower half of the spine.
    An insert under the blade hole takes the blade screw. The lock screw goes through it into the
    insert in the shelf. The base prints upside down (the top on the bed)."""
    k = jig_x()
    zt = k["top"]
    z1 = S.CUT_H - S.BLADE_T / 2                          # the top face: the blade lies on it
    body = box(k["R"], k["out"], -S.CART_W / 2, S.CART_W / 2, zt, z1)
    y0 = S.SHELF_W / 2 + S.CART_CLR
    for sgn in (1, -1):
        ya, yb = sorted((sgn * y0, sgn * (y0 + S.CHEEK_T)))
        body += box(k["ro"] + 1.0, k["out"], ya, yb, zt - S.SHELF_T, zt + 0.01)
    body -= Pos(0, 0, -1) * Cylinder_(k["ri"], S.JUG_H + 2)
    # The V-groove for the spine: 45 deg faces, so the base prints upside down with no support.
    v0 = S.BLADE_D - S.SPINE_D - S.GROOVE_CLR
    v1 = S.BLADE_D + S.GROOVE_CLR
    zg = z1 - S.CUT_H + 0.01
    prof = Polygon((v0, zg), (v1, zg), ((v0 + v1) / 2, zg - (v1 - v0) / 2), align=None)
    body -= blade_frame(k, extrude(Plane.XZ * prof, 60, both=True))
    # The insert for the blade screw: the hole goes through, so the melted PLA can flow out.
    hx, hy = blade_hole_xy(k)
    body -= Pos(hx, hy, zt - 1) * Cylinder_(S.INSERT_D / 2, S.CART_LOW + 2)
    # The lock screw goes through the base into the insert in the shelf.
    body -= Pos(*k["pin"], zt - 1) * Cylinder_(S.SCREW_CLR / 2, S.CART_LOW + 2)
    return body


def cart_clamp():
    """The clamp plate. It presses the blade flat on the base. A slot in its bottom face fits the
    spine, so the blade goes in one way only. The blade screw goes through it and the blade hole
    into the insert in the base. The lock screw goes through it and the base into the shelf. A lip at each side goes down over the sides of the base. The plate
    prints upside down."""
    k = jig_x()
    z2 = S.CUT_H + S.BLADE_T / 2                          # the bottom face: on the blade
    ztop = k["top"] + S.CART_H
    w = S.CART_W / 2 + S.LIP_CLR
    body = box(k["R"], k["out"], -w - S.LIP_T, w + S.LIP_T, z2, ztop)
    for sgn in (1, -1):
        ya, yb = sorted((sgn * w, sgn * (w + S.LIP_T)))
        body += box(k["ro"] + 1.0, k["out"], ya, yb, z2 - S.LIP_H, ztop)
    body -= Pos(0, 0, -1) * Cylinder_(k["ri"], S.JUG_H + 2)
    # The slot for the upper half of the spine: SPINE_CLR at each wall and at each end.
    hu = S.SPINE_L / 2 + S.SPINE_CLR
    slot = box(S.BLADE_D - S.SPINE_D - S.SPINE_CLR, S.BLADE_D + S.SPINE_CLR, -hu, hu, -1, S.SPINE_T / 2 + 0.2)
    body -= blade_frame(k, slot)
    for x, y in (blade_hole_xy(k), k["pin"]):
        body -= Pos(x, y, z2 - 1) * Cylinder_(S.SCREW_CLR / 2, S.CART_H + 2)
    # The turn arrow on the top: the near side of the jug moves this way (-Y).
    x = k["ri"] + 5.5
    tip = (x, -9.0)
    for p0, p1 in (((x, 9.0), tip), ((x - 4.0, -5.0), tip), ((x + 4.0, -5.0), tip)):
        body -= v_groove(p0, p1, ztop, S.ARROW_W)
    return body


def insert():
    """The two M2.5 heat-set inserts (the model only): one in the shelf, one in the base. Both flush."""
    k = jig_x()
    out = None
    for (x, y), z in ((k["pin"], k["top"]), (blade_hole_xy(k), S.CUT_H - S.BLADE_T / 2)):
        p = Pos(x, y, z - S.INSERT_L)
        part = p * Cylinder_(S.INSERT_OD / 2, S.INSERT_L) - p * Pos(0, 0, -1) * Cylinder_(S.SCREW_D / 2 - 0.2, S.INSERT_L + 2)
        out = part if out is None else out + part
    return out


def screw_base():
    """The lock screw: through both plates into the insert in the shelf (the model only)."""
    k = jig_x()
    zt = k["top"] + S.CART_H
    px, py = k["pin"]
    sc = Pos(px, py, zt - S.SCREW_L) * Cylinder_(S.SCREW_D / 2, S.SCREW_L + 0.01)
    return sc + Pos(px, py, zt) * Cylinder_(S.SCREW_HEAD_D / 2, S.SCREW_HEAD_H)


def screw_blade():
    """The cap screw: through the clamp plate and the blade hole into the insert in the base."""
    k = jig_x()
    zt = k["top"] + S.CART_H
    px, py = blade_hole_xy(k)
    sc = Pos(px, py, zt - S.BLADE_SCREW_L) * Cylinder_(S.SCREW_D / 2, S.BLADE_SCREW_L + 0.01)
    return sc + Pos(px, py, zt) * Cylinder_(S.SCREW_HEAD_D / 2, S.SCREW_HEAD_H)


def screw():
    return screw_base() + screw_blade()


def blade(gap=0.0):
    """The razor blade in the cartridge, edge toward the jug, at YAW. gap: a move back (+v)."""
    k = jig_x()
    hu = S.BLADE_L / 2
    width = S.BLADE_D
    v0 = gap
    b = box(v0, v0 + width - S.SPINE_D, -hu, hu, -S.BLADE_T / 2, S.BLADE_T / 2)
    b += box(v0 + width - S.SPINE_D, v0 + width, -S.SPINE_L / 2, S.SPINE_L / 2, -S.SPINE_T / 2, S.SPINE_T / 2)
    hole = Pos(v0 + width - S.HOLE_C, 0, -1) * SlotOverall(S.HOLE_H, S.HOLE_W)
    b -= extrude(hole, 2)
    return blade_frame(k, b)


def edge_crossings(width=S.BLADE_D, gap=0.0, shift=0.0):
    """Where the edge crosses the outer and the inner face of the jug wall, as u along the edge.
    shift: the jug centre moves this much along X. Return (u_outer, u_inner) or None."""
    k = jig_x()
    v0 = S.BLADE_D - width + gap
    ox, oy = k["o"][0] + k["vh"][0] * v0, k["o"][1] + k["vh"][1] * v0
    res = []
    for r in (k["R"], k["R"] - S.JUG_T):
        hit = None
        for i in range(-2000, 2001):
            u = i * S.BLADE_L / 4000
            x, y = ox + k["uh"][0] * u - shift, oy + k["uh"][1] * u
            if math.hypot(x, y) <= r:
                hit = u                 # the last u inside: the deep end is inside, the far end out
        res.append(hit)
    return tuple(res)


def jug_full():
    """The full jug body before the cut (no shoulder, no handle)."""
    return slab(0, 0, S.JUG_H) - slab(-S.JUG_T, S.JUG_FLOOR, S.JUG_H + 1)


def Cylinder_(r, h):
    return extrude(Circle(r), h)


# --- Context --------------------------------------------------------------------------------

def seat_depth(t=S.JUG_T):
    """The depth below the roof of the groove where the groove is as wide as a wall of thickness t."""
    return S.SKIRT_H * (t - 2 * S.G_HALF_ROOF) / (2 * S.G_HALF_MOUTH - 2 * S.G_HALF_ROOF)


def wall_range():
    """The thinnest and the thickest wall that seat in the groove. Keep 1 mm of the groove below the seat."""
    w_roof, w_mouth = 2 * S.G_HALF_ROOF, 2 * S.G_HALF_MOUTH
    return w_roof, w_mouth - (w_mouth - w_roof) / S.SKIRT_H


def jug():
    """The bottom half of the jug, cut at Z = 0, at its seat in the groove of the collar."""
    z = -seat_depth()
    return Pos(0, 0, z) * (slab(0, -S.CUT_H, 0) - slab(-S.JUG_T, -S.CUT_H + S.JUG_FLOOR, 1))


def jug_inner_area():
    """The inside area of the jug, mm2."""
    return rr(-S.JUG_T).area


def basket_inner_area():
    return rr(S.BASKET_IN).area


def wall_slot_count():
    return wall_slots()[1] if S.WSLOT_ROWS else 0
