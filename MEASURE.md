# Measurements

The jug wall and the blade size in `shape.py` are estimates. The jug diameter is measured. Take these measurements, then
change `shape.py` and run `make.sh`.

## The jug

| # | Value in `shape.py` | Now | How to measure |
|---|---|---|---|
| J1 | `JUG_DIA` | 152.8 (MEASURED: 480 mm circumference) | Put a tape measure or a paper strip around the jug, 100 mm above the table. Read the circumference. Divide it by 3.1416. |
| J2 | `JUG_T` | 1.0 (ESTIMATE) | The wall thickness. Cut the jug, then measure the cut edge with the big outside jaws of the calipers, at three points. Use the largest value. |

Also check:

- The body must be round and vertical at 100 mm above the table. If the handle or a label
  recess is there, change `CUT_H` (for example 120). The jig, the images, and the brine volume
  follow it.

## The razor blade

| # | Value in `shape.py` | Now | How to measure |
|---|---|---|---|
| B1 | `BLADE_T` | 0.25 (ESTIMATE) | OUTSIDE: the thickness of the blade, near the edge. Use the outside jaws. |
| B2 | `SPINE_T`, `SPINE_D` | 0.9, 5.5 (ESTIMATE) | OUTSIDE: the thickness of the folded spine, and its depth from the back. |
| B3 | `BLADE_L`, `BLADE_D` | 38.5, 19.0 (ESTIMATE) | OUTSIDE: the length of the edge, and the width from the edge to the back of the spine. |

After a change, print `stl/fit_arc.stl` again before the full collar.
