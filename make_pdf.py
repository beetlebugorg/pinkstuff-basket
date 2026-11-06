#!/usr/bin/env python3
"""Desiccant basket: write the build instructions PDF (pinkstuff-basket.pdf).
Run after model.py, cura/make_profiles.py, and lineart/render.mjs. Needs Chromium."""

import json
import subprocess
from pathlib import Path

import shape as S

HERE = Path(__file__).resolve().parent
BUILD = HERE / "build"
IMG = BUILD / "img"
OUT = HERE / "pinkstuff-basket.pdf"

SUMMARY = json.loads((BUILD / "parts.json").read_text())
# The Printdeck slice (printdeck_slice.py): the same slicer and profiles as the service.
FILAMENT = json.loads((BUILD / "printdeck_slice.json").read_text())


def hm(seconds):
    h, m = divmod(round(seconds / 60), 60)
    return f"{h} h {m:02d} min" if h else f"{m} min"
SUPPORTS = json.loads((BUILD / "supports.json").read_text())
FIT = SUMMARY["fit"]
PRICE_PER_KG = 19.99                 # USD, PLA

CSS = """
  @page { size: A4; margin: 0; }
  * { box-sizing: border-box; }
  :root { --ink: #16181a; --ink-2: #4a4f55; --accent: #0a7f63; --bg: #fbfbf9; --grid: #ececE6; --line: #e2e2dc;
          --mono: "JetBrains Mono", "JetBrainsMono Nerd Font", ui-monospace, monospace; }
  body { margin: 0; font-family: "Inter", "Helvetica Neue", Helvetica, Arial, "Liberation Sans", sans-serif; color: var(--ink); }
  .page { width: 210mm; height: 297mm; padding: 16mm 16mm 14mm; page-break-after: always; position: relative; overflow: hidden; }
  .page:last-child { page-break-after: auto; }
  h1 { font-size: 50pt; letter-spacing: 2pt; margin: 0; font-weight: 800; }
  h2 { font-size: 20pt; margin: 0 0 5mm; font-weight: 700; }
  .sub { font-size: 24pt; font-weight: 700; margin-top: 2mm; color: var(--accent); }
  .num { font: 800 72pt/1 var(--mono); color: var(--accent); }
  .head { display: flex; align-items: flex-end; gap: 8mm; border-bottom: 0.6mm solid var(--ink); padding-bottom: 4mm; }
  .head .title { font-size: 22pt; font-weight: 700; padding-bottom: 3mm; }
  .fig { width: 100%; margin: 4mm 0; padding: 4mm; text-align: center; border: 0.3mm solid var(--line); border-radius: 3mm;
         background-color: var(--bg); background-size: 6mm 6mm;
         background-image: linear-gradient(var(--grid) 0.15mm, transparent 0.15mm), linear-gradient(90deg, var(--grid) 0.15mm, transparent 0.15mm); }
  .fig img { max-width: 100%; max-height: 130mm; vertical-align: middle; }
  .need { display: flex; flex-wrap: wrap; gap: 3mm; margin: 4mm 0; }
  .chip { border: 0.4mm solid var(--ink); border-radius: 999px; padding: 1.5mm 4mm; font: 600 10pt var(--mono); }
  ol, ul { font-size: 12pt; line-height: 1.5; padding-left: 6mm; margin: 2mm 0; }
  p { font-size: 12pt; line-height: 1.5; margin: 2mm 0; }
  .note { border: 0.4mm solid var(--accent); border-radius: 3mm; padding: 3mm 5mm; margin-top: 4mm; font-size: 11.5pt; background: #e3f3ee; }
  .note b { color: var(--accent); }
  table { border-collapse: collapse; width: 100%; font-size: 10.5pt; }
  td, th { border-bottom: 0.2mm solid #999; padding: 1.4mm 2mm; vertical-align: middle; text-align: left; }
  th { border-bottom: 0.6mm solid #111; }
  td.q { font-weight: 800; font-size: 13pt; width: 12mm; }
  td.n, th.n { text-align: right; white-space: nowrap; }
  tr.total td { font-weight: 800; border-top: 0.6mm solid #111; border-bottom: none; }
  .thumb { width: 18mm; height: 12mm; object-fit: contain; display: block; }
  .grid3 { display: grid; grid-template-columns: repeat(3, 1fr); gap: 4mm; }
  .card { border: 0.3mm solid var(--line); background: var(--bg); border-radius: 3mm; padding: 2.5mm; font-size: 8.8pt; line-height: 1.3; }
  .card img { width: 100%; height: 20mm; object-fit: contain; }
  .card b { display: block; font-size: 11pt; margin: 1mm 0; }
  .sw { display: inline-block; width: 3.5mm; height: 3.5mm; border-radius: 1mm; vertical-align: -0.5mm; margin-right: 1.5mm; }
  .cols { display: grid; grid-template-columns: 1fr 1fr; gap: 8mm; }
  code { font-size: 0.92em; }
  .foot { position: absolute; bottom: 8mm; left: 16mm; right: 16mm; font-size: 9.5pt; color: #555; display: flex; justify-content: space-between; }
"""

SWATCH = {"White": "#f4f4f2"}


def cost(grams):
    return grams / 1000 * PRICE_PER_KG


# Name, colour, count, print notes. The order is the print order.
N_SETS = 1

PRINTS = [
    ("jig", "White", 1, "Upside down, the ring top on the bed. Print it once for all the jugs."),
    ("jig_cart", "White", 1, "Upside down, the flat top face on the bed. The cheeks point up."),
    ("jig_clamp", "White", 1, "Upside down, the top face with the arrow on the bed."),
    ("fit_arc", "White", 1, "Top face on the bed. Print this first. It tests the groove and the diameter on the jug."),
    ("collar", "White", N_SETS, "Top face on the bed (upside down). The groove opens to the top."),
    ("basket", "White", N_SETS, "Floor on the bed. The rim flares out at 45°."),
    ("lid", "White", N_SETS, "Top face on the bed (upside down). The skirt goes up."),
]

SETTINGS = [
    ("Profiles", "Printdeck: <code>taz-workhorse-se/pla-0.30-fast</code>, roll-5, with the part settings in printdeck.yml. Or in Cura: run "
                 "<code>python3 cura/make_profiles.py --install</code> with Cura closed, then pick “Desiccant - …”."),
    ("Material", "PLA, 2.85 mm, 0.5 mm nozzle. Calcium chloride brine does not attack PLA, PETG, or the HDPE jug. "
                 "Keep the brine away from metal."),
    ("Layers", f"0.3 mm layers (Printdeck profile pla-0.30-fast). Basket: {S.BASKET_T:.2f} mm wall (one line), "
               f"{S.FLOOR_T:.1f} mm floor (4 layers). Lid: {S.LID_T:.1f} mm plate (4 layers). A 10-line brim on the outside. "
               "Hole expansion off on the collar, the basket, and the lid: their inner faces are holes in each layer."),
    ("Open grid", f"The basket floor and the lid plate are solid in the model. The basket and lid settings print them as "
                  f"an open grid: no top or bottom skin, lines infill {S.GRID_PITCH} mm apart, connected lines. The "
                  f"openings are {S.GRID_PITCH - 0.5:.1f} mm square. Use these settings. A normal profile prints a "
                  "solid floor, and the brine cannot drain."),
    ("Speed", "Fast speeds for a functional part: print 80 mm/s, infill 80 mm/s, outer wall 70 mm/s, inner walls "
              "80 mm/s, top and bottom 70 mm/s, first layer and brim 30 mm/s. The flow stays at 12 mm3/s or less. "
              "Accelerations 2000 to 3000 mm/s2. PLA at 220 C for the higher flow. Minimum layer time 5 s."),
    ("Supports", "Off. A slice with supports on (60°, everywhere) adds 0 g of support to each part."),
    ("Tools", "One single-edge razor blade with a folded steel spine (1.5 in long, 11/16 to 3/4 in wide, 0.010 in thick; "
              "for example Personna #9 or Stanley 11-515), a flat table, and sandpaper (120 grit)."),
    ("Hardware", "Two M2.5 heat-set inserts, 4 mm long, for a 3.6 mm hole (CNC Kitchen type). M2.5 socket head "
                 "cap screws: one 12 mm long (the lock screw), one 8 mm long (the blade screw). A 2 mm hex key. "
                 "A soldering iron at 220 °C to set the inserts."),
]

STEPS = [
    ("blade", "Load the blade", ["cartridge base", "clamp plate", "razor blade", "M2.5 x 8 screw", "2 mm hex key"], [
        "One time only: put an insert on the round hole in the middle of the base top. Push it in with the soldering "
        "iron at 220 °C until it is flush with the top. Let it cool.",
        "Put the base on the table, flat top up. The curved end points away from you.",
        "Hold the blade by the spine. Lay it on the base, spine down in the V-groove, edge toward the curved end.",
        "Move the blade until you see the insert through the hole in the blade.",
        "Put the clamp plate on top, arrow up. The spine goes into the slot under the plate. The side lips go "
        "down over the sides of the base. The plate sits flat only when the spine is in the slot.",
        "Put the M2.5 x 8 screw through the front hole of the clamp plate and the blade hole into the insert. Tighten it firmly.",
        f"Look at the curved end. The blade is at {S.YAW:.0f}° and its tip comes out about 10 mm. The edge is now covered "
        "except at the curved end.",
    ], "The front hole is the blade screw. The back hole is the lock screw. It goes in when the cartridge is on the ring. "
       "To change the blade, remove the blade screw and lift off the clamp plate. Hold the blade by the spine only."),
    ("jig", "Cut the jug", ["cutting ring", "loaded cartridge", "M2.5 x 12 screw", "2 mm hex key", "jug", "flat table"], [
        "Empty the jug. Rinse it with water and let it dry.",
        "One time only: put an insert on the hole in the shelf. Push it in with the soldering iron at 220 °C until it is "
        "flush with the shelf top. Let it cool.",
        "Stand the cutting ring on a flat table. Put the jug down into the ring from above.",
        "Put the loaded cartridge on the shelf, behind the ring, edge toward the jug. The side cheeks of the base go down "
        "beside the shelf.",
        "Push the back end of the cartridge with your thumb. The tip of the angled blade goes through the wall first.",
        "Put the M2.5 x 12 lock screw through the back hole into the insert in the shelf. Tighten it.",
        "Turn the jug by its handle CLOCKWISE (seen from above), one full turn. The arrow on the "
        "clamp plate shows the way the near side of the jug moves. The blade cuts a level line.",
        "Remove the lock screw. Pull the cartridge back. Lift off the top half, then lift the jug out.",
        f"Sand the cut edge flat and remove the burrs. The cut is {S.CUT_H:.0f} mm above the table.",
    ], f"The blade is at {S.YAW:.0f}° to the wall, so the wall meets the sharp edge and the edge slices it. "
       "Turn the jug the other way and the wall hits the blunt end of the blade. Take the blade out after use, "
       "or keep the loaded cartridge in a box."),
    ("part_fit_arc", "Fit test", ["fit test arc", "cut jug"], [
        "Push the groove of the fit test arc down over the cut edge.",
        "The edge must go into the groove and stop with a firm push.",
        "Look at the outer face. The skirt must follow the jug wall, with no gap at the ends of the arc.",
    ], "The jug diameter comes from one sample jug. Other jugs can differ. A gap at the ends: the diameter in the model is too large. A gap at the middle: "
       "it is too small. Measure the jug (<code>MEASURE.md</code>), change <code>JUG_DIA</code> in <code>shape.py</code>, run "
       "<code>make.sh</code>, and print the arc again."),
    ("collar", "Put on the collar", ["collar", "jug"], [
        "Turn the collar so that the groove opens down.",
        "Put the groove over the cut edge of the jug. Start at one side and work around.",
        "Push down hard all around. The edge wedges into the groove.",
        "Pull up on the collar. It must stay on the jug.",
    ], f"The groove tapers from {2 * S.G_HALF_MOUTH:.1f} mm at its mouth to {2 * S.G_HALF_ROOF:.1f} mm at its roof. A wall from "
       f"{FIT['wall_range'][0]:.1f} to {FIT['wall_range'][1]:.1f} mm wedges in. The lid snap also presses the collar skirt onto the jug."),
    ("basket", "Put in the basket", ["basket", "desiccant pellets"], [
        "Lower the basket into the collar. Its flared rim sits on the 45° seat of the collar.",
        "Fill the basket with 400 g (0.9 lb) of calcium chloride pellets: about 450 mL (1.9 US cups), 28 mm deep. "
        "This is 11 mm below the rim.",
        f"Do not fill it full. A full basket holds {FIT['pellet_l']:.2f} L, about 560 g. At 70 % humidity, 560 g of pellets "
        f"makes about 1.6 L of brine. The jug holds only {FIT['brine_l']:.2f} L of brine below the basket.",
        "Use calcium chloride pellets, for example DampRid refills. The pellets must be larger than the 2 mm openings in the floor.",
        "To lift the basket out, put your fingers into the two notches in the collar and pull up on the rim.",
    ], "The pellets take water from the air and turn to brine. The brine drips through the open grid of the floor into the jug."),
    ("lid", "Snap on the lid", ["lid"], [
        "Put the lid on the collar, with the pull tab at one side.",
        "Push down on each side of the lid until it clicks. The bead of the skirt goes over the ridge of the collar.",
        "To remove the lid, pull the tab out and up.",
        "Empty the brine when it gets near the basket floor. Remove the collar with the basket and the lid. Pour the brine down a drain with water.",
    ], f"The openings in the lid grid are {S.GRID_PITCH - 0.5:.1f} mm square. Air goes in, and the pellets stay in if the jug falls over. "
       "Brine can come out if the jug falls over: put the jug in a place where it can not fall."),
]

ADJUST = [
    ("The collar is loose on the jug, or it does not go over the edge", "JUG_DIA", f"{S.JUG_DIA:.0f}",
     "Measure the circumference of the jug at the cut, and divide by 3.1416 (MEASURE.md, J1)."),
    ("The blade does not cut through the wall, or it tears it", "YAW", f"{S.YAW:.0f}",
     "Turn the jug clockwise. Change YAW by 5: a larger angle goes deeper, a smaller angle slices more."),
    ("The jug does not go into the cutting ring, or it is loose in it", "RING_CLR, JUG_DIA", f"{S.RING_CLR:.1f}, {S.JUG_DIA:.1f}",
     "Check JUG_DIA (MEASURE.md, J1). Change RING_CLR by 0.2."),
    ("The clamp plate does not sit flat on the blade", "SPINE_CLR", f"{S.SPINE_CLR:.2f}",
     "Add 0.1 to SPINE_CLR: the slot for the spine gets wider. Reprint the clamp plate only."),
    ("The insert is loose in the shelf, or it does not go in", "INSERT_D", f"{S.INSERT_D:.1f}",
     "Set INSERT_D to the hole size on the data sheet of your insert. Reprint the ring."),
    ("The blade moves when the screw is tight", "SPINE_CLR", f"{S.SPINE_CLR:.2f}",
     "Subtract 0.05 from SPINE_CLR: the slot then fits the spine closer. Reprint the clamp plate only."),
    ("The edge stops at the mouth of the groove", "JUG_T, G_HALF_MOUTH", f"{S.JUG_T:.1f}, {S.G_HALF_MOUTH:.1f}",
     "Measure the wall (J2). Set JUG_T to the value. For a wall over 2.2 mm, add 0.3 to G_HALF_MOUTH."),
    ("The collar is loose on a correct jug size", "G_HALF_ROOF", f"{S.G_HALF_ROOF:.1f}",
     "Subtract 0.1 from G_HALF_ROOF. The wall then wedges higher in the groove."),
    ("The lid is too hard to put on, or it is loose", "SNAP", f"{S.SNAP:.2f}",
     "Subtract or add 0.1. The skirt strain must stay below 1.5 % (model.py prints it)."),
    ("The basket sits too high or too low", "DEPTH, CUT_H", f"{S.DEPTH:.0f}, {S.CUT_H:.0f}",
     "Change DEPTH for a deeper or shallower basket. The ring and the cartridge set CUT_H."),
]


def img(name):
    return (IMG / f"{name}-light.png").as_uri()


def foot(n):
    return f'<div class="foot"><span>Desiccant basket · build instructions</span><span>{n}</span></div>'


def cover():
    total = round(sum(FILAMENT[n]["grams"] for n in ("collar", "basket", "lid")))
    hours = hm(sum(FILAMENT[n]["seconds"] for n in ("collar", "basket", "lid")))
    return f"""<section class="page">
  <h1 style="font-size:40pt">PINK STUFF</h1><div class="sub">A desiccant basket for the bottom half of a pink antifreeze jug</div>
  <p style="margin-top:4mm;max-width:170mm">Cut a West Marine -50°F antifreeze gallon jug in half with the cutting ring. A collar goes over the cut
  edge. A basket of desiccant pellets hangs in the collar. A lid snaps onto the collar and keeps the pellets in. The pellets take
  water from the air. The brine drips through the floor of the basket and collects in the jug, below the basket.</p>
  <div class="fig"><img src="{img('hero')}" style="max-height:105mm;max-width:52%"><img src="{img('explode')}" style="max-height:105mm;max-width:44%"></div>
  <p style="font-size:10pt;color:#444">Left: the assembly on the jug. Right: the parts. From the bottom: the jug, the collar, the basket, the lid.</p>
  <div class="note"><b>Measured and estimated.</b> The model uses a {S.JUG_DIA:.1f} mm diameter, from a 480 mm
  circumference on a sample jug. The {S.JUG_T:.1f} mm wall is an estimate.
  Print the fit test arc first. <code>MEASURE.md</code> lists the measurements to take.</div>
  <div class="need"><div class="chip"><span class="sw" style="background:#f4f4f2;border:0.3mm solid #999"></span>White PLA</div>
    <div class="chip">{total} g and {hours} for each jug</div><div class="chip">cutting ring {round(sum(FILAMENT[n]['grams'] for n in ('jig', 'jig_cart', 'jig_clamp')))} g, once</div><div class="chip">No supports</div><div class="chip">Two M2.5 screws, two inserts</div></div>
  {foot(1)}
</section>"""


def print_page():
    rows = []
    tg = ts = 0
    for name, colour, k, _ in PRINTS:
        p = SUMMARY["parts"][name]
        g1, s1 = FILAMENT[name]["grams"], FILAMENT[name]["seconds"]
        tg += g1 * k
        ts += s1 * k
        sx, sy, sz = p["size"]
        rows.append(f'<tr><td><img class="thumb" src="{img("part_" + name)}"></td><td><code>stl/{name}.stl</code></td>'
                    f'<td class="n">{sx:.0f} × {sy:.0f} × {sz:.0f}</td><td class="n">{g1:.0f} g</td><td class="n">{hm(s1)}</td>'
                    f'<td class="n">{k}</td><td class="n">{g1 * k:.0f} g</td><td class="n">{hm(s1 * k)}</td><td class="n">${cost(g1 * k):.2f}</td></tr>')
    rows.append(f'<tr class="total"><td></td><td>Total</td><td></td><td></td><td></td><td></td><td class="n">{tg:.0f} g</td><td class="n">{hm(ts)}</td>'
                f'<td class="n">${cost(tg):.2f}</td></tr>')
    cards = "".join(f'<div class="card"><img src="{img("part_" + n)}"><b>{n.replace("_", " ")}</b>'
                    f'support check {SUPPORTS[n]:.0f} g<br>{t}</div>' for n, c, _, t in PRINTS)
    st = "".join(f"<tr><td>{k}</td><td>{v}</td></tr>" for k, v in SETTINGS)
    return f"""<section class="page">
  <h2>Printed parts</h2>
  <table><tr><th></th><th>File</th><th class="n">Size (mm)</th><th class="n">Each</th><th class="n">Time each</th><th class="n">Count</th><th class="n">Filament</th><th class="n">Time</th><th class="n">Cost</th></tr>
  {''.join(rows)}</table>
  <p style="font-size:9.5pt;color:#444">Filament and print time from the Printdeck slice: the Printdeck slicer with the TAZ Workhorse SE profile
  (pla-0.30-fast, faster speeds, white PLA), the same slice as printdeck.beetlebug.org.
  Cost at ${PRICE_PER_KG:.2f}/kg. The counts are for {N_SETS} jugs.</p>
  <h2 style="margin-top:4mm">Print</h2>
  <p style="margin:1mm 0">The STL files are in their print orientation. Load them, do not turn them.</p>
  <div class="grid4" style="display:grid;grid-template-columns:repeat(4,1fr);gap:2.5mm">{cards}</div>
  <h2 style="margin-top:4mm">Settings (LulzBot TAZ Workhorse)</h2>
  <table style="font-size:8.8pt">{st}</table>
  {foot(2)}
</section>"""


def step_page(i, step, n):
    shot, title, need, items, note = step
    chips = "".join(f'<div class="chip">{x}</div>' for x in need)
    lis = "".join(f"<li>{t}</li>" for t in items)
    nt = f'<div class="note"><b>Note.</b> {note}</div>' if note else ""
    return f"""<section class="page">
  <div class="head"><div class="num">{i}</div><div class="title">{title}</div></div>
  <div class="need">{chips}</div>
  <div class="fig"><img src="{img(shot)}" style="max-height:120mm"></div>
  <ol>{lis}</ol>{nt}
  {foot(n)}
</section>"""


def how_page(n):
    return f"""<section class="page">
  <h2>How it locks</h2>
  <div class="cols">
    <div class="fig" style="margin:0"><img src="{img('detail')}" style="max-height:120mm"></div>
    <div>
      <p style="font-size:10.5pt">The section through the rim, at one side of the jug. From the left: the basket rim under the
      lid plate, the collar, the jug wall in the groove, and the lid skirt.</p>
      <ul style="font-size:10.5pt">
        <li><b>Groove.</b> The cut edge goes up into a tapered groove in the collar. A {S.JUG_T:.1f} mm wall stops
        {FIT['wedge_depth']:.1f} mm below the roof. A firm push wedges it in.</li>
        <li><b>Seat.</b> The basket rim flares out at 45°. It sits on a 45° seat in the collar and centres itself.</li>
        <li><b>Snap.</b> A bead inside the lid skirt goes over a ridge on the collar skirt, and clicks into a groove.
        The snap is {S.SNAP:.1f} mm. {S.SLITS} slits cut the skirt into fingers. Each finger bends with
        {FIT['strain_pct']:.2f} % strain (PLA takes about 1.5 %).</li>
        <li><b>Clamp.</b> The lid skirt holds the collar skirt against the jug wall.</li>
        <li><b>Rim.</b> The lid plate sits on the basket rim. The pellets stay in.</li>
      </ul>
    </div>
  </div>
  <div class="fig"><img src="{img('section')}" style="max-height:90mm"></div>
  <p style="font-size:10pt;color:#444">The section through the middle. The basket holds {FIT['pellet_l']:.1f} L of pellets. The
  space below the basket holds {FIT['brine_l']:.1f} L of brine (cut at {S.CUT_H:.0f} mm). A star of ribs (6 spokes) stiffens the floor.
  The floor prints as an open grid of connected lines, {S.GRID_PITCH} mm apart: one path for each layer, with no small holes.</p>
  {foot(n)}
</section>"""


def end_page(n):
    rows = "".join(f"<tr><td>{a}</td><td><code>{b}</code></td><td class=\"n\">{c}</td><td>{d}</td></tr>"
                   for a, b, c, d in ADJUST)
    return f"""<section class="page">
  <h2>Adjust the fit</h2>
  <p>The jug wall is an estimate. Measure the jug (<code>MEASURE.md</code>), change the values in <code>shape.py</code>,
  run <code>make.sh</code>, and print the fit test arc again.</p>
  <table style="font-size:9.5pt"><tr><th>Problem</th><th>Value</th><th class="n">Now (mm)</th><th>Change</th></tr>{rows}</table>
  <div class="note"><b>The fit check.</b> <code>model.py</code> checks the collar on the jug, the basket in the collar, and the
  lid on the collar, also on the path in. It stops if a part touches where it must not, if the collar has no grip, or if the
  lid has no snap.</div>
  {foot(n)}
</section>"""


def main():
    pages = [cover(), print_page()]
    for i, s in enumerate(STEPS):
        pages.append(step_page(i + 1, s, len(pages) + 1))
    pages.append(how_page(len(pages) + 1))
    pages.append(end_page(len(pages) + 1))
    html = (f'<!doctype html><html lang="en"><head><meta charset="utf-8"><title>Desiccant basket build</title>'
            f'<style>{CSS}</style></head><body>{"".join(pages)}</body></html>')
    src = BUILD / "build.html"
    src.write_text(html)
    subprocess.run(["chromium", "--headless", "--disable-gpu", "--no-pdf-header-footer", "--allow-file-access-from-files",
                    f"--print-to-pdf={OUT}", src.as_uri()], check=True, capture_output=True)
    print("wrote", OUT)


if __name__ == "__main__":
    main()
