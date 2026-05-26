# Hardware Notes

## First PCB Revision

Build a full-size SD-card-shaped board that is electrically conservative:

- 3.3 V signaling only.
- SD default speed first.
- No UHS-II contacts.
- ENIG edge contacts.
- Low-current LEDs.
- Test pads for SWD/programming.

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

## BOM Direction

- MCU: RP2350A/RP2350B, final package TBD by routing and thickness.
- LEDs: right-angle / side-view RGB LEDs facing the exposed SD-card lip. A
  top-emitting addressable LED is a poor fit here unless we add a real light
  pipe, because the laptop slot hides most of the top face.
- Decoupling: local 100 nF caps at MCU and LEDs, plus small bulk capacitance.
- Optional ESD: low-capacitance ESD array on exposed SD lines.
