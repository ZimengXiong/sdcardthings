# SD LED Card

SD-card-shaped RGB status module for a MacBook SD slot.

The intended UX is:

1. Insert the card.
2. macOS mounts a tiny volume.
3. Edit `LEDS.TXT` on that volume.
4. Firmware parses the written file and updates the LEDs.

This is not a passive SD adapter. The card has to emulate an SD memory card well
enough for macOS, then intercept block writes to a tiny virtual FAT volume.

## Current Direction

- Controller: RP2350/RP2350A, because PIO can emulate 4-bit SDIO timing.
- SD behavior: fork/adapt `petritoast/pico_sdcard`.
- LED control: low-profile RGB LEDs on the exposed end of the SD card.
- Storage model: virtual FAT volume with a fixed `LEDS.TXT`.
- First hardware: full-size SD card outline, 3.3 V only, no UHS-II.

## Important Constraint

A microcontroller cannot simply "read a file on the SD card" while the Mac is
also using that same SD storage bus. SD is host-owned. To make the file workflow
work smoothly, our MCU should be the SD card: it emulates the block device,
accepts writes from macOS, and updates LEDs when the file content changes.

The alternate approach is a real microSD card plus bus switch, but that usually
requires the Mac to unmount/eject before the MCU can safely read the card. That
is a worse UX for this project.

## Repo Layout

- `docs/architecture.md` - technical plan and tradeoffs.
- `hardware/` - KiCad and hardware notes.
- `firmware/led_config/` - parser for `LEDS.TXT`.
- `firmware/pico_sdcard_upstream/` - upstream SD emulator reference.

