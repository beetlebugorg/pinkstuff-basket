# Desiccant basket: all dimensions. Units are millimetres.
#
# The basket holds desiccant pellets (calcium chloride, for example DampRid refills) in the
# bottom half of a West Marine -50F antifreeze gallon jug. Cut the jug level, CUT_H above its
# bottom. The pellets take water from the air and drip brine through the floor of the basket.
# The brine collects in the jug, below the basket.
#
# Three printed parts:
# - The collar. A tapered groove goes over the cut edge of the jug. The edge wedges into the
#   groove, so the collar grips walls from about 0.7 to 1.8 mm thick. Above the cut, a 45 deg
#   seat holds the basket. The outer face has a ridge and a groove for the lid snap.
# - The basket. A round box with a 45 deg flared rim. The rim sits on the seat of the
#   collar. Slots in the floor let the brine drip out. Two ribs stiffen the floor. Side slots save filament.
# - The lid. A cap with a skirt and a bead that snaps over the ridge of the collar. The plate
#   sits on the basket rim. Narrow slots let air in and keep the pellets in. A tab at the
#   skirt lets you pull the lid off. The lid skirt also presses the collar skirt onto the jug.
#   Slits cut the lid skirt into fingers, so each finger bends over the ridge by itself.
#
# World coordinates (the parts in use): Z = 0 at the cut edge of the jug, Z up. The jug axis is
# the Z axis. The jug is round. All horizontal sizes are OFFSETS from the outer face of the
# jug: an offset o gives the circle of radius JUG_DIA / 2 + o.
#
# Print orientation: the basket prints as it sits (floor on the bed). The collar and the lid
# print upside down (the top face on the bed). No part needs supports.

# --- The jug (diameter measured on a sample jug; the other values are estimates) ---
JUG_DIA = 152.8      # MEASURED: 480 mm circumference at the middle / pi
JUG_W = JUG_D = JUG_DIA  # the bounding box of the jug (for the slots and the images)
JUG_T = 1.0          # ESTIMATE: wall thickness of the jug at the cut (HDPE)
JUG_FLOOR = 1.5      # ESTIMATE: floor thickness of the jug (the context model only)
CUT_H = 100.0        # the height of the cut above the bottom of the jug (your choice)

# --- The collar: the groove over the cut edge ---
# The groove tapers on both faces, about the centre of the jug wall. The wall wedges in where
# the groove is as wide as the wall. A wrong estimate of the jug size moves the wall to one
# side; the thin HDPE wall bends to the centre.
SKIRT_H = 8.0        # depth of the groove: the collar goes 8 mm down over the jug
G_MID = -JUG_T / 2   # the centre of the groove: the centre of the jug wall
G_HALF_MOUTH = 1.3   # half width of the groove at its mouth (2.6 mm wide)
G_HALF_ROOF = 0.3    # half width of the groove at its roof (0.6 mm wide)
COLLAR_IN_T = 1.2    # wall of the collar inside the jug, at the mouth of the groove
A = G_MID - G_HALF_MOUTH - COLLAR_IN_T   # inner face of the collar, below the seat
SKIRT_O = 2.0        # outer face of the collar skirt

# --- The collar band above the cut, the basket seat ---
BAND_H = 5.0         # the band goes 5 mm above the cut edge
CONE = 2.5           # the 45 deg seat: it goes out 2.5 mm from A, from Z = 0 to Z = CONE
BAND_O = 1.3         # outer face of the band, above the snap ridge
NOTCH_W = 12.0       # finger notch at each X side, width at the top (a 45 deg V)

# --- The lid snap on the collar skirt (45 deg flanks) ---
SNAP_Z = -4.5        # the centre of the snap groove
SNAP_G = 0.7         # depth of the groove into the skirt (from SKIRT_O)

# --- The basket ---
BASKET_CLR = 0.5     # gap from the basket wall to the collar inner face
BASKET_O = A - BASKET_CLR      # outer face of the basket wall
BASKET_T = 1.0       # wall (2 lines of 0.5 mm)
BASKET_IN = BASKET_O - BASKET_T
RIM_CLR = 0.3        # gap from the basket rim to the band bore
DEPTH = 35.0         # the floor of the basket is 35 mm below the cut: the basket is 40 mm tall
FLOOR_T = 0.9        # floor thickness (3 layers of 0.3 mm)
RIB_T = 1.5          # the two floor ribs (a cross)
RIB_H = 6.0          # height of the ribs above the floor
FLOOR_SLOT = 2.0     # width of the drain slots (pellets are larger, about 3 to 8 mm)
SLOT_PITCH = 3.0     # row pitch (1 mm bars, 2 lines)
SLOT_EDGE = 1.5      # the slots stay 1.5 mm from the wall
CROSS_X = 36.0       # the slots stop at the cross ribs at X = 0 and X = +-36 mm
CROSS_W = 2.0        # width of the cross bands in the lid
# Side slots in the basket wall: less filament, and more air to the pellets. Each slot is
# vertical with a 45 deg pointed top, so it prints with no support.
WSLOT_W = 2.0        # width
WSLOT_H = 8.0        # height of the straight part
WSLOT_PITCH = 3.5    # pitch around the wall (1.5 mm bars)
WSLOT_ROWS = 0       # rows (0: no side slots; they add print time)
WWSLOT_Z0 = -DEPTH + FLOOR_T + RIB_H + 2   # bottom of the lowest row

# --- The lid ---
LID_CLR = 0.25       # gap from the lid skirt to the collar skirt
LID_SKIRT_T = 1.0    # lid skirt (2 lines): it flexes over the ridge
SLITS = 16           # slits in the lid skirt: they make 16 fingers
SLIT_W = 1.0         # width of a slit
SLIT_TOP = BAND_H - 1.5  # the slits stop 1.5 mm below the lid plate
LID_IN = SKIRT_O + LID_CLR
LID_O = LID_IN + LID_SKIRT_T
LID_T = 0.9          # lid plate thickness (3 layers of 0.3 mm)
LID_SKIRT_Z0 = -6.0  # bottom of the lid skirt
SNAP = 0.5           # the bead goes 0.5 mm inside the ridge: the snap interference
BEAD_APEX = SKIRT_O - SNAP
VENT_SLOT = 2.0      # width of the air slots in the lid
VENT_EDGE = 3.0      # the vents stay inside BASKET_IN - VENT_EDGE
TAB_W = 30.0         # pull tab at +Y, at the bottom of the skirt
TAB_OUT = 3.0        # the tab goes 3 mm out, at 45 deg

# --- Cutting collar: a ring on three legs that holds a razor blade at CUT_H ---
# Stand the ring on a flat table. Put the jug into the ring from above. Put the blade into the
# cartridge, push the cartridge in on the shelf (the blade goes through the jug wall), and drop
# in the pin. The pin locks the blade in the cartridge and the cartridge on the shelf. Turn the
# jug in the ring. The ring and the legs print upside down, the cartridge on its back end.
JUG_H = 260.0        # ESTIMATE: height of the full jug body (the context model only)
BLADE_L = 38.9       # MEASURED: single-edge razor blade, length of the edge
BLADE_D = 19.4       # MEASURED: from the edge to the back of the spine
BLADE_D_MIN = 17.5   # a narrower blade also fits: 11/16 in (Stanley 11-515 type)
HOLE_W = 2.71        # MEASURED: the slot hole in the middle of the blade, across
HOLE_H = 6.00        # MEASURED: its length, from the edge toward the spine (round ends)
HOLE_C = 10.5        # MEASURED: its centre, from the back of the spine
BLADE_T = 0.25       # MEASURED: blade thickness
SPINE_T = 1.0        # MEASURED: thickness of the folded steel spine
SPINE_L = 39.7       # MEASURED: length of the spine (longer than the edge)
SPINE_D = 5.5        # ESTIMATE: depth of the spine
SLOT_CLR = 0.75      # the blade slot is BLADE_T + SLOT_CLR thick (1.0 mm). A 0.6 mm slot closes up in the print
POCKET_CLR = 0.5     # the spine pocket is SPINE_T + POCKET_CLR thick (1.5 mm)
RING_CLR = 0.6       # gap from the ring to the jug, on each side
RING_T = 3.0         # radial wall of the ring
RING_H = 8.0         # height of the ring; its top is CART_LOW below CUT_H
YAW = 30.0           # the blade edge is at 30 deg to the jug wall (seen from above): the deep tip
                     # pierces the wall, then the wall crosses the edge at the middle of the blade
CART_LOW = 4.0       # the blade is 4 mm above the bottom of the cartridge (the shelf top)
CART_H = 8.0         # height of the cartridge
CART_W = 48.0        # width of the cartridge (the angled blade spans 43 mm)
CART_CLR = 0.3       # gap from the cheeks of the cartridge to the shelf
CHEEK_T = 2.4        # the cheeks go down beside the shelf and guide the cartridge
SHELF_W = 42.0       # width of the shelf
SHELF_T = 5.0        # thickness of the shelf
SHELF_L = 34.0       # the shelf goes to R + SHELF_L
ARROW_W = 1.2        # the turn arrow on the cartridge: V-grooves (45 deg faces print with no support)
SCREW_D = 2.5        # the lock screw: M2.5 x 12 socket head cap screw (2 mm hex key)
SCREW_L = 12.0       # length under the head: 8 mm through the cartridge, 4 mm into the insert
SCREW_HEAD_D = 4.5   # head of the screw (the model only)
SCREW_HEAD_H = 2.5
SCREW_CLR = 2.9      # the hole in the cartridge: a diamond with a 2.9 mm inner circle (no support)
INSERT_D = 3.6       # ESTIMATE: M2.5 heat-set insert, 4 mm long (CNC Kitchen type): hole diameter. Check the data sheet
INSERT_L = 4.0       # length of the insert; it goes in from the shelf top, flush
INSERT_OD = 3.9      # outer diameter of the insert (the model only)
LEG_W = 14.0         # three legs: a plate LEG_W wide and LEG_T thick, and a radial fin
LEG_T = 2.4
LEG_FIN = 8.0        # the fin goes LEG_FIN out from the plate, FIN_T thick
FIN_T = 2.4
FOOT = 30.0          # at the table the fin flares out to FOOT, over FOOT_H (49 deg, no support)
FOOT_H = 25.0
BRACE_REACH = 40.0   # two struts at 45 deg on each leg: from the leg, 40 mm along the ring and 40 mm up to it
BRACE_W = 4.0        # the strut section: BRACE_W wide (in the plane of the strut), BRACE_T radial
BRACE_T = 3.0

# --- Fit test: a short arc of the collar, at +X ---
FIT_SIZE = 50.0      # the chord of the arc

# --- The bending strain of the lid skirt, PLA limit ---
STRAIN_LIMIT = 1.5   # percent
