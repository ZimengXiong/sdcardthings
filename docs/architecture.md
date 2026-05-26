# Architecture

## Goal

Expose a small writable SD-card volume to macOS. The user edits `LEDS.TXT`, and
the card updates a row of RGB LEDs without needing a separate USB connection.

## Chosen Architecture

Use an RP2350 as an SD-card device emulator.

MacBook SD slot:

```text
macOS SD host <-> SD edge pads <-> RP2350 PIO SDIO emulator
                                  |
                                  +-> LEDS.TXT block-write parser
                                  |
                                  +-> RGB LED driver
```

The firmware does not need to implement a complete general-purpose SD card. It
only needs to satisfy macOS well enough to mount a small FAT volume and accept
writes to a known config file.

## Why Not a Real MicroSD Card?

A real microSD card plus MCU creates a bus ownership problem:

```text
macOS SD host <-> microSD card
MCU          <-> microSD card
```

Only one controller can own the card at a time. A bus switch can make that safe,
but then the user workflow becomes "write file, eject, wait for MCU to read,
remount." That can work as a fallback prototype, but it is not the intended
seamless file workflow.

## Firmware Plan

1. Start from `petritoast/pico_sdcard`.
2. Keep 3.3 V default-speed SD mode for the first revision.
3. Replace the demo block handler with a tiny virtual FAT volume.
4. Expose one fixed file: `LEDS.TXT`.
5. On `CMD24`/`CMD25` writes, inspect written blocks.
6. When a block contains a valid LED config, parse it and update LEDs.

The first parser is deliberately forgiving. It accepts:

```text
brightness=64
led0=#ff0000
led1=0,255,0
led2=#0040ff
```

## Hardware Plan

Core parts:

- RP2350A or RP2350B MCU.
- 3.3 V rail from SD `VDD`.
- 6 SDIO pins: `CMD`, `CLK`, `DAT0`, `DAT1`, `DAT2`, `DAT3`.
- 5-7 low-profile RGB LEDs at the exposed edge.
- Optional capacitive touch pad on exposed edge plating.
- Programming pads/SWD or BOOT/USB breakout for firmware loading.

The first PCB should intentionally ignore UHS-II rear-row pins. It should behave
as a 3.3 V default-speed SD card.

## Main Risks

- macOS may be stricter than the USB reader used by the upstream emulator.
- The SD slot may power-manage the card aggressively.
- Full SD-card thickness leaves almost no component clearance.
- macOS writes hidden metadata files; firmware should tolerate extra writes.
- In-slot LED current must be low to avoid heat and brownouts.

