# `LEDS.TXT` Format

The config is line-oriented ASCII.

```text
brightness=64
led0=#ff0000
led1=#00ff00
led2=#0000ff
led3=255,128,0
led4=12,12,12
led5=off
```

Rules:

- `brightness` is 0-255.
- LED keys are `led0`, `led1`, etc.
- Colors can be hex (`#rrggbb`) or decimal CSV (`r,g,b`).
- `off` means `0,0,0`.
- Unknown lines are ignored.
- Whitespace around keys and values is allowed.

