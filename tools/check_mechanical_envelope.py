#!/usr/bin/env python3
"""Check the SD-slot insertion height envelope for the generated board.

This is intentionally conservative: with the current 1.4 mm SD-card PCB
assumption, all package bodies are treated as too tall to enter the Mac SD slot
throat. Only the KiCad SD-card contact footprint is allowed in the inserted
region.
"""

from __future__ import annotations

from pathlib import Path

import pcbnew


ROOT = Path(__file__).resolve().parents[1]
BOARD = ROOT / "hardware" / "sd-led-card.kicad_pcb"

# KiCad's SD_Card_Device_16mm_SlotDepth footprint is placed at Y=50.0 mm.
# Its inserted/contact region ends at local Y=-0.05, i.e. board Y=49.95 mm.
INSERTED_REGION_MAX_Y_MM = 49.95
BOARD_THICKNESS_MM = 1.4
FULL_SIZE_SD_NORMAL_THICKNESS_MM = 2.1

PACKAGE_HEIGHTS_MM = {
    "QFN-60-1EP_7x7mm_P0.4mm_EP3.4x3.4mm": 0.90,
    "LED_RGB_Everlight_EASV3015RGBA0_Horizontal": 1.10,
    "C_0402_1005Metric": 0.50,
}


def main() -> None:
    board = pcbnew.LoadBoard(str(BOARD))
    failures: list[str] = []

    for fp in board.GetFootprints():
        name = str(fp.GetFPID().GetLibItemName())
        if name in {"SD_Card_Device_16mm_SlotDepth"}:
            continue

        y = pcbnew.ToMM(fp.GetPosition().y)
        height = PACKAGE_HEIGHTS_MM.get(name, 0.0)
        total_height = BOARD_THICKNESS_MM + height

        if y <= INSERTED_REGION_MAX_Y_MM and height > 0:
            failures.append(
                f"{fp.GetReference()} {name} is at Y={y:.2f} mm inside the "
                f"inserted region; total height would be {total_height:.2f} mm."
            )

        if height > 0 and total_height > FULL_SIZE_SD_NORMAL_THICKNESS_MM:
            print(
                f"NOTE: {fp.GetReference()} {name} total stack "
                f"{total_height:.2f} mm exceeds normal SD thickness; placement "
                "must remain in the exposed region."
            )

    if failures:
        for failure in failures:
            print(f"FAIL: {failure}")
        raise SystemExit(1)

    print(
        "Mechanical envelope check passed: component bodies are outside the "
        "KiCad 16 mm inserted SD-slot region."
    )


if __name__ == "__main__":
    main()
