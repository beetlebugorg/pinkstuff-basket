#!/usr/bin/env python3
"""Slice each part of printdeck.yml with the Printdeck slicer (curaslice.py of printdeck-action)
and the profiles in profiles/. This is the same slice as the Printdeck service makes.
Writes build/gcode/<part>.gcode and build/printdeck_slice.json (print time, filament).
Set PRINTDECK_ACTION to the printdeck-action folder (default ~/Projects/printdeck-action)."""

import json
import os
import sys

import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.environ.get("PRINTDECK_ACTION", os.path.expanduser("~/Projects/printdeck-action")))
import curaslice  # noqa: E402


def main():
    deck = yaml.safe_load(open(os.path.join(HERE, "printdeck.yml")))
    out_dir = os.path.join(HERE, "build", "gcode")
    os.makedirs(out_dir, exist_ok=True)
    result = {}
    for part in deck["parts"]:
        folder, quality = part["profile"].split("/", 1)
        stem = os.path.splitext(os.path.basename(part["files"][0]))[0]
        out = os.path.join(out_dir, stem + ".gcode")
        settings = {k: str(v) for k, v in (part.get("settings") or {}).items()}
        files = [os.path.join(HERE, f) for f in part["files"]]
        f = curaslice.slice_plate(os.path.join(HERE, "profiles", folder), quality, part.get("material"),
                                  [(part["name"], files, 1, settings)], out, name=stem)
        result[stem] = {"name": part["name"], "count": part.get("count", 1), "seconds": f.get("seconds"),
                        "grams": f.get("grams"), "metres": f.get("metres"), "profile": f["profile"]}
        h, m = divmod(round(f.get("seconds", 0) / 60), 60)
        print(f"  {part['name']:16s} {h:2d} h {m:02d} min  {f.get('grams', 0):6.1f} g  ({f['profile']}, {part.get('material')})")
    json.dump(result, open(os.path.join(HERE, "build", "printdeck_slice.json"), "w"), indent=1)


if __name__ == "__main__":
    main()
