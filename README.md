# Pink Stuff desiccant basket

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="docs/hero-dark.png">
  <img src="docs/hero-light.png" alt="The collar, the basket and the lid on the cut jug" width="420">
</picture>

A desiccant basket for the bottom half of the round West Marine -50°F antifreeze gallon jug
("the pink stuff"), and a cutting ring that cuts the jug with a razor blade. The basket holds
calcium chloride pellets (for example DampRid refills). The pellets take water from the air.
The brine drips through the slots of the basket and collects in the jug.

- **Cutting ring.** A ring on three legs holds the jug centred, and holds a razor blade level
  100 mm above the table. The blade sits in a cartridge on a shelf of the ring. Push the
  cartridge in, drop in the lock pin, and turn the jug. Each jug gets the same cut.
- **Collar.** A tapered groove goes over the cut edge of the jug. The edge wedges into it.
  Walls from 0.6 to 2.4 mm fit. A 45° seat above the cut holds the basket.
- **Basket.** 0.6 L of pellets, 40 mm tall. The flared rim sits on the seat. A 1 mm wall with
  260 side slots and 158 floor slots, all 2 mm wide, and two floor ribs. The jug holds 1.1 L of
  brine below it. Lift it out by the two finger notches in the collar.
- **Lid.** A bead in the skirt snaps over a ridge on the collar. 16 slits cut the skirt into
  fingers (0.5 mm snap, 1.17 % strain in PLA). The skirt also clamps the collar onto the jug.
  The plate sits on the basket rim. The air slots are 1.5 mm wide, so the pellets stay in.
- No supports, no hardware, no glue. White PLA, to match the pellets.

`pinkstuff-basket.pdf` has the parts list, the print settings, and the steps.

## Status

The jug diameter is **measured**: 480 mm around the middle of a sample jug, so 152.8 mm.
The 1.0 mm wall is an **estimate**. The razor blade size
is an estimate too. Print `stl/fit_arc.stl` first. `MEASURE.md` lists the measurements to take.

## Files

| File | Content |
|---|---|
| `shape.py` | All dimensions. `ESTIMATE` marks the values that are not measured. |
| `parts.py` | The collar, the basket, the lid, the cutting ring, the cartridge, the pin, the fit test arc, the jug, and the blade, in build123d. |
| `model.py` | The fit check, then `cad/*.step`, `stl/*.stl` (print orientation), and the meshes for the images. |
| `stl/` | `collar.stl`, `basket.stl`, `lid.stl`, `jig.stl`, `jig_cart.stl`, `jig_pin.stl`, `fit_arc.stl`, in print orientation. |
| `cad/` | A STEP file for each part, and `desiccant-assembly.step`. |
| `cura/make_profiles.py` | A Cura profile for each part, the filament use, and the support check. |
| `printdeck.yml`, `profiles/` | The Printdeck build: the parts, the TAZ Workhorse profiles, and the PDF. |
| `lineart/render.mjs` | The line-art images. |
| `printdeck_slice.py` | The Printdeck slice of each part: the print time and the filament. |
| `make_pdf.py` | The PDF. |
| `make.sh` | Runs all steps. |

## Build

```
./make.sh
```

The script stops if the fit check, the mesh check, or the support check fails. It needs `uv`,
`node`, Chromium, ImageMagick, and CuraEngine in `/opt/ultimaker-cura`.

## Print

The print times and the filament come from the Printdeck slice (`printdeck_slice.py`): the
Printdeck slicer with the TAZ Workhorse SE profile `pla-0.20-standard`, white PLA (`roll-5`).

| Part | Count | Orientation | Filament | Time |
|---|---|---|---|---|
| `fit_arc.stl` | 1 | top face on the bed | 2 g | 15 min |
| `jig.stl` (cutting ring) | 1 | upside down, the ring top on the bed | 36 g | 3 h 30 min |
| `jig_cart.stl` (cartridge) | 1 | on its back end | 9 g | 47 min |
| `jig_pin.stl` (lock pin) | 1 | cap on the bed | 0.4 g | 6 min |
| `collar.stl` | 6 | top face on the bed (upside down) | 19 g | 1 h 40 min |
| `basket.stl` | 6 | floor on the bed | 33 g | 5 h 06 min |
| `lid.stl` | 6 | top face on the bed (upside down) | 28 g | 3 h 34 min |

One set (collar, basket, lid) is 80 g and 10 h 20 min. Six sets are 480 g and 62 h. The tools
are 48 g and 4 h 40 min, once. The `roll-5` white PLA entry is new in
`profiles/taz-workhorse-se/cura.json`. It copies the black MatterHackers PLA settings.
