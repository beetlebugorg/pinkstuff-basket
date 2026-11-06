#!/usr/bin/env python3
"""The measurement images for the razor blade. The blade is a drawing to scale (no photo).
Run with: uv run --no-project --with pillow python docs/measure/blade_steps.py
Writes docs/measure/blade-<n>.jpg."""

import importlib.util
from pathlib import Path

from PIL import Image, ImageDraw

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("steps", Path.home() / ".claude/skills/3d-print/template/docs/measure/steps.py")
T = importlib.util.module_from_spec(spec)
spec.loader.exec_module(T)

PX = 30                       # pixels per mm
X0, Y0 = 330, 160             # the left end of the spine back
SPINE_L, BLADE_L, BLADE_D, SPINE_D = 39.65, 38.86, 19.37, 7.19
HOLE_W, HOLE_H, HOLE_C = 2.71, 6.0, 10.5


def blade():
    im = Image.new("RGBA", (1900, 1000), (255, 255, 255, 255))
    g = ImageDraw.Draw(im)
    x1 = X0 + SPINE_L * PX
    inset = (SPINE_L - BLADE_L) / 2 * PX
    ye = Y0 + BLADE_D * PX
    g.polygon([(X0 + inset, Y0), (x1 - inset, Y0), (x1 - inset, ye), (X0 + inset, ye)], fill=(200, 205, 212), outline=(0, 0, 0), width=3)
    g.rectangle([X0 + inset, ye - 1.5 * PX, x1 - inset, ye], fill=(232, 236, 240), outline=(0, 0, 0), width=2)
    g.rectangle([X0, Y0, x1, Y0 + SPINE_D * PX], fill=(120, 126, 134), outline=(0, 0, 0), width=3)
    hx, hy = X0 + SPINE_L / 2 * PX, Y0 + HOLE_C * PX
    g.rounded_rectangle([hx - HOLE_W / 2 * PX, hy - HOLE_H / 2 * PX, hx + HOLE_W / 2 * PX, hy + HOLE_H / 2 * PX],
                        radius=HOLE_W / 2 * PX, fill=(255, 255, 255), outline=(0, 0, 0), width=3)
    f = T.font(30)
    g.text((x1 + 20, Y0 + SPINE_D * PX / 2), "spine (1 mm thick)", font=f, fill=(0, 0, 0), anchor="lm")
    g.text((x1 + 20, ye - 0.75 * PX), "cutting edge", font=f, fill=(0, 0, 0), anchor="lm")
    g.text((x1 + 20, hy), "the hole", font=f, fill=(0, 0, 0), anchor="lm")
    g.line([(hx + HOLE_W / 2 * PX + 4, hy), (x1 + 14, hy)], fill=(0, 0, 0), width=2)
    return im


STEPS = [
    dict(item="S1", name="Spine depth · OUTSIDE jaws",
         a=(X0 + 3 * PX, Y0), b=(X0 + 3 * PX, Y0 + SPINE_D * PX), side=(-1, 0), d=230,
         lines=["Lay the blade flat on the table, spine away from you.",
                "Put one big jaw against the back of the spine.",
                "Put the other jaw on the blade face, pushed against the front edge of the spine.",
                "Measure near one end, away from the hole."],
         reply="S1 = __ mm"),
    dict(item="S2", name="Spine back to the hole · OUTSIDE jaws",
         a=(X0 + SPINE_L / 2 * PX, Y0), b=(X0 + SPINE_L / 2 * PX, Y0 + (HOLE_C - HOLE_H / 2) * PX), side=(-1, 0), d=680,
         lines=["Put one big jaw tip down into the hole.",
                "Pull it against the end of the hole nearest the spine.",
                "Put the other jaw against the back of the spine. Read the value."],
         reply="S2 = __ mm"),
]


def main():
    for i, s in enumerate(STEPS, 1):
        im = blade()
        T.caliper(im, s["a"], s["b"], s["side"], s["d"], "outside", 0.8)
        out = T.frame(im, (0, 0, im.width, im.height), 0.8, i, len(STEPS), s["item"], s["name"], s["lines"], s["reply"])
        out.save(HERE / f"blade-{i}.jpg", quality=90)
    print("wrote", len(STEPS))


if __name__ == "__main__":
    main()
