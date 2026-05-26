# Hardware Notes

## First PCB Revision

Build a full-size SD-card-shaped board that is electrically conservative:

- 3.3 V signaling only.
- SD default speed first.
- No UHS-II contacts.
- ENIG edge contacts.
- Low-current LEDs.
- Test pads for SWD/programming.

Current generated PCB status:

- KiCad DRC: clean, 0 violations / 0 unconnected items.
- Components are placed on the same face as the SD contact pads.
- Decorative no-net routing has been removed.
- The remaining production gates are schematic capture, real net assignment,
  final routed copper, exact manufacturer stackup, and confirmed component
  heights for the target MacBook SD slot.

## Mechanical Z Budget

This design is based on KiCad's `SD_Card_Device_16mm_SlotDepth` footprint. That
template models the inserted contact/mechanical region of a full-size SD card,
and its own description calls for a 1.4 mm PCB thickness.

The current placement keeps component bodies outside that inserted 16 mm region:

| Item | Side | Approx. package height | Mechanical note |
| --- | --- | ---: | --- |
| RP2350A QFN-60 | SD-contact side | 0.90 mm max | Too tall for an inserted SD throat on a 1.4 mm PCB. Must remain in the exposed region. |
| EASV3015RGBA0 right-angle LED | SD-contact side | 1.10 mm max | Too tall for an inserted SD throat on a 1.4 mm PCB. Intended to sit at the exposed lip. |
| 0402 capacitors | SD-contact side | about 0.5 mm | Also kept out of the inserted region. |
| CT1 capacitive touch electrode | SD-contact side | bare copper | No component height. |
| Debug/test pads | SD-contact side | bare copper | Mechanically safe; no component height. |

This is therefore **not** a guaranteed full-depth/flush-slot design. If the
target MacBook slot swallows the component area, this board will not fit. The
next physical validation step is measuring the actual insertion depth and slot
clearance on the target MacBook, then keeping all non-copper component bodies
outside that envelope.

Run `tools/check_mechanical_envelope.py` after regenerating the board. It fails
if any known package body is placed inside the inserted 16 mm SD-slot region,
and it warns about packages whose board-plus-package stack exceeds normal SD
card thickness.

## Candidate Pin Map

This follows the upstream RP2350 SD emulator default:

| Signal | RP2350 GPIO |
| --- | ---: |
| SD CMD | GP0 |
| SD CLK | GP1 |
| SD DAT0 | GP2 |
| SD DAT1 | GP3 |
| SD DAT2 | GP4 |
| SD DAT3 | GP5 |
| LED DATA | GP6 |
| CAP TOUCH | GP7 |

## Mechanical Notes

Use KiCad's SD-card-device footprint as the starting point for outline and edge
pads. The exposed end should contain the LED diffuser windows and any touch
electrode. Keep all components out of the deep-insertion region unless a real
slot-clearance check proves there is room.

The current capacitive touch electrode is `CT1`, a bare copper/ENIG pad on the
SD-contact side near the exposed lip. It should route to `GP7` through the
touch-sensing front end. Keep a local ground guard optional for a later rev:
the first board should prioritize a large accessible touch area and tune
thresholds in firmware.

## BOM Direction

- MCU: RP2350A/RP2350B, final package TBD by routing and thickness.
- LEDs: right-angle / side-view RGB LEDs facing the exposed SD-card lip. A
  top-emitting addressable LED is a poor fit here unless we add a real light
  pipe, because the laptop slot hides most of the top face.
- Decoupling: local 100 nF caps at MCU and LEDs, plus small bulk capacitance.
- Optional ESD: low-capacitance ESD array on exposed SD lines.
