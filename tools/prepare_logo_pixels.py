#!/usr/bin/env python3
"""Convert the snowpaca PNG logo into low-res KiCad silkscreen pixels."""

from __future__ import annotations

import json
from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
SRC = Path("/Users/xzm/Projects/snowpaca.cc/assets/snowpaca-black.png")
OUT = ROOT / "hardware" / "snowpaca_logo_pixels.json"


def main() -> None:
    img = Image.open(SRC).convert("RGBA")
    img.thumbnail((28, 28), Image.Resampling.LANCZOS)

    canvas = Image.new("RGBA", (28, 28), (255, 255, 255, 0))
    canvas.alpha_composite(img, ((28 - img.width) // 2, (28 - img.height) // 2))

    pixels = []
    for y in range(canvas.height):
        for x in range(canvas.width):
            r, g, b, a = canvas.getpixel((x, y))
            # The black logo has strong alpha and dark RGB where ink exists.
            if a > 80 and (r + g + b) < 500:
                pixels.append([x, y])

    OUT.write_text(json.dumps({"width": 28, "height": 28, "pixels": pixels}), encoding="utf-8")
    print(f"Wrote {OUT} with {len(pixels)} pixels")


if __name__ == "__main__":
    main()

