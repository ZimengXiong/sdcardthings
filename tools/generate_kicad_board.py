#!/usr/bin/env python3
"""Generate the first KiCad PCB scaffold for the SD LED card."""

from __future__ import annotations

import json
import uuid
from pathlib import Path

import pcbnew


ROOT = Path(__file__).resolve().parents[1]
KICAD = Path("/Users/xzm/Applications/KiCad/KiCad.app/Contents/SharedSupport")
OUT = ROOT / "hardware" / "sd-led-card.kicad_pcb"
PRO = ROOT / "hardware" / "sd-led-card.kicad_pro"
SCH = ROOT / "hardware" / "sd-led-card.kicad_sch"
BOARD_THICKNESS_MM = 0.8
INSERTED_REGION_MIN_Y_MM = 34.05
INSERTED_REGION_MAX_Y_MM = 49.95


def mm(x: float, y: float) -> pcbnew.VECTOR2I:
    return pcbnew.VECTOR2I(pcbnew.FromMM(x), pcbnew.FromMM(y))


def load_fp(lib: str, name: str, ref: str, value: str, x: float, y: float):
    fp = pcbnew.FootprintLoad(str(KICAD / "footprints" / f"{lib}.pretty"), name)
    if fp is None:
        raise RuntimeError(f"Could not load {lib}:{name}")
    fp.SetReference(ref)
    fp.SetValue(value)
    fp.SetPosition(mm(x, y))
    return fp


def add_text(
    board: pcbnew.BOARD,
    text: str,
    x: float,
    y: float,
    size: float = 0.8,
    angle: float = 0,
):
    item = pcbnew.PCB_TEXT(board)
    item.SetText(text)
    item.SetLayer(pcbnew.F_SilkS)
    item.SetPosition(mm(x, y))
    item.SetTextAngleDegrees(angle)
    item.SetTextSize(mm(size, size))
    item.SetTextThickness(pcbnew.FromMM(0.12))
    board.Add(item)


def smd_layers(side: str = "front") -> pcbnew.LSET:
    layers = pcbnew.LSET()
    if side == "back":
        layers.AddLayer(pcbnew.B_Cu)
        layers.AddLayer(pcbnew.B_Mask)
        layers.AddLayer(pcbnew.B_Paste)
    else:
        layers.AddLayer(pcbnew.F_Cu)
        layers.AddLayer(pcbnew.F_Mask)
        layers.AddLayer(pcbnew.F_Paste)
    return layers


def add_pad(
    board: pcbnew.BOARD,
    ref: str,
    number: str,
    x: float,
    y: float,
    w: float,
    h: float,
    shape=pcbnew.PAD_SHAPE_ROUNDRECT,
    side: str = "front",
) -> None:
    fp = pcbnew.FOOTPRINT(board)
    if side == "back":
        fp.SetLayer(pcbnew.B_Cu)
    fp.SetReference(ref)
    fp.SetValue(ref)
    fp.Reference().SetVisible(False)
    fp.Value().SetVisible(False)
    pad = pcbnew.PAD(fp)
    pad.SetNumber(number)
    pad.SetAttribute(pcbnew.PAD_ATTRIB_SMD)
    pad.SetShape(shape)
    pad.SetLayerSet(smd_layers(side))
    pad.SetPosition(mm(x, y))
    pad.SetSize(mm(w, h))
    if shape == pcbnew.PAD_SHAPE_ROUNDRECT:
        pad.SetRoundRectRadiusRatio(0.12)
    fp.Add(pad)
    board.Add(fp)


def add_pad_footprint(
    board: pcbnew.BOARD,
    ref: str,
    value: str,
    pads: list[tuple[str, float, float, float, float, int]],
    side: str = "front",
) -> None:
    fp = pcbnew.FOOTPRINT(board)
    fp.SetReference(ref)
    fp.SetValue(value)
    fp.Reference().SetVisible(False)
    fp.Value().SetVisible(False)
    if side == "back":
        fp.SetLayer(pcbnew.B_Cu)

    for number, x, y, w, h, shape in pads:
        pad = pcbnew.PAD(fp)
        pad.SetNumber(number)
        pad.SetAttribute(pcbnew.PAD_ATTRIB_SMD)
        pad.SetShape(shape)
        pad.SetLayerSet(smd_layers(side))
        pad.SetPosition(mm(x, y))
        pad.SetSize(mm(w, h))
        if shape == pcbnew.PAD_SHAPE_ROUNDRECT:
            pad.SetRoundRectRadiusRatio(0.12)
        fp.Add(pad)

    board.Add(fp)


def add_filled_rect(board: pcbnew.BOARD, layer: int, start, end, width: float = 0.01) -> None:
    shape = pcbnew.PCB_SHAPE(board)
    shape.SetShape(pcbnew.SHAPE_T_RECT)
    shape.SetLayer(layer)
    shape.SetWidth(pcbnew.FromMM(width))
    shape.SetStart(mm(*start))
    shape.SetEnd(mm(*end))
    shape.SetFilled(True)
    board.Add(shape)


def add_edge_segment(board: pcbnew.BOARD, start, end) -> None:
    shape = pcbnew.PCB_SHAPE(board)
    shape.SetShape(pcbnew.SHAPE_T_SEGMENT)
    shape.SetLayer(pcbnew.Edge_Cuts)
    shape.SetWidth(pcbnew.FromMM(0.12))
    shape.SetStart(mm(*start))
    shape.SetEnd(mm(*end))
    board.Add(shape)


def add_user_segment(board: pcbnew.BOARD, start, end, layer: int = pcbnew.User_1, width: float = 0.08) -> None:
    shape = pcbnew.PCB_SHAPE(board)
    shape.SetShape(pcbnew.SHAPE_T_SEGMENT)
    shape.SetLayer(layer)
    shape.SetWidth(pcbnew.FromMM(width))
    shape.SetStart(mm(*start))
    shape.SetEnd(mm(*end))
    board.Add(shape)


def add_rect_outline(board: pcbnew.BOARD, layer: int, x0: float, y0: float, x1: float, y1: float) -> None:
    add_user_segment(board, (x0, y0), (x1, y0), layer)
    add_user_segment(board, (x1, y0), (x1, y1), layer)
    add_user_segment(board, (x1, y1), (x0, y1), layer)
    add_user_segment(board, (x0, y1), (x0, y0), layer)


def add_layer_text(
    board: pcbnew.BOARD,
    text: str,
    x: float,
    y: float,
    layer: int,
    size: float = 0.55,
    angle: float = 0,
) -> None:
    item = pcbnew.PCB_TEXT(board)
    item.SetText(text)
    item.SetLayer(layer)
    item.SetPosition(mm(x, y))
    item.SetTextAngleDegrees(angle)
    item.SetTextSize(mm(size, size))
    item.SetTextThickness(pcbnew.FromMM(0.08))
    board.Add(item)


SCHEMATIC_UUID = "7a27751f-9548-47ad-9f45-899b84ebad22"


def stable_uuid(key: str) -> str:
    return str(uuid.uuid5(uuid.UUID(SCHEMATIC_UUID), key))


def sch_property(name: str, value: str, x: float, y: float, pid: int, hide: bool = False) -> str:
    hidden = "\n\t\t\t(hide yes)" if hide else ""
    return f'''\
\t\t(property "{name}" "{value}"
\t\t\t(at {x:.2f} {y:.2f} 0)
\t\t\t(effects
\t\t\t\t(font
\t\t\t\t\t(size 1.27 1.27)
\t\t\t\t)
{hidden}
\t\t\t)
\t\t)
'''


def symbol_def(lib_id: str, ref_prefix: str, value: str, pins: list[tuple[str, str, str, float]]) -> str:
    height = max(8.0, (len(pins) + 1) * 1.27)
    y_top = height / 2
    y_bottom = -height / 2
    pin_defs = []
    for idx, (number, name, side, y) in enumerate(pins):
        x = -15.24 if side == "left" else 15.24
        angle = 0 if side == "left" else 180
        pin_defs.append(f'''\
\t\t\t\t(pin passive line
\t\t\t\t\t(at {x:.2f} {y:.2f} {angle})
\t\t\t\t\t(length 5.08)
\t\t\t\t\t(name "{name}"
\t\t\t\t\t\t(effects
\t\t\t\t\t\t\t(font
\t\t\t\t\t\t\t\t(size 1.0 1.0)
\t\t\t\t\t\t\t)
\t\t\t\t\t\t)
\t\t\t\t\t)
\t\t\t\t\t(number "{number}"
\t\t\t\t\t\t(effects
\t\t\t\t\t\t\t(font
\t\t\t\t\t\t\t\t(size 1.0 1.0)
\t\t\t\t\t\t\t)
\t\t\t\t\t\t)
\t\t\t\t\t)
\t\t\t\t)
''')
    short = lib_id.split(":")[-1]
    return f'''\
\t\t(symbol "{lib_id}"
\t\t\t(pin_names
\t\t\t\t(offset 0.762)
\t\t\t)
\t\t\t(exclude_from_sim no)
\t\t\t(in_bom yes)
\t\t\t(on_board yes)
{sch_property("Reference", ref_prefix, 0, y_top + 2.54, 0)}{sch_property("Value", value, 0, y_bottom - 2.54, 1)}{sch_property("Footprint", "", 0, 0, 2, True)}{sch_property("Datasheet", "~", 0, 0, 3, True)}
\t\t\t(symbol "{short}_1_1"
\t\t\t\t(rectangle
\t\t\t\t\t(start -10.16 {y_top:.2f})
\t\t\t\t\t(end 10.16 {y_bottom:.2f})
\t\t\t\t\t(stroke
\t\t\t\t\t\t(width 0.254)
\t\t\t\t\t\t(type default)
\t\t\t\t\t)
\t\t\t\t\t(fill
\t\t\t\t\t\t(type background)
\t\t\t\t\t)
\t\t\t\t)
{"".join(pin_defs)}\t\t\t)
\t\t\t(embedded_fonts no)
\t\t)
'''


def placed_symbol(
    lib_id: str,
    ref: str,
    value: str,
    footprint: str,
    x: float,
    y: float,
    pins: list[tuple[str, str, str, float]],
    project_name: str,
) -> str:
    pin_entries = "\n".join(
        f'\t\t(pin "{number}"\n\t\t\t(uuid "{stable_uuid(ref + "-pin-" + number)}")\n\t\t)'
        for number, _, _, _ in pins
    )
    return f'''\
\t(symbol
\t\t(lib_id "{lib_id}")
\t\t(at {x:.2f} {y:.2f} 0)
\t\t(unit 1)
\t\t(exclude_from_sim no)
\t\t(in_bom yes)
\t\t(on_board yes)
\t\t(dnp no)
\t\t(uuid "{stable_uuid(ref)}")
\t\t(property "Reference" "{ref}"
\t\t\t(at {x:.2f} {y - 8.0:.2f} 0)
\t\t\t(effects
\t\t\t\t(font
\t\t\t\t\t(size 1.27 1.27)
\t\t\t\t)
\t\t\t)
\t\t)
\t\t(property "Value" "{value}"
\t\t\t(at {x:.2f} {y + 8.0:.2f} 0)
\t\t\t(effects
\t\t\t\t(font
\t\t\t\t\t(size 1.27 1.27)
\t\t\t\t)
\t\t\t)
\t\t)
\t\t(property "Footprint" "{footprint}"
\t\t\t(at {x:.2f} {y:.2f} 0)
\t\t\t(effects
\t\t\t\t(font
\t\t\t\t\t(size 1.27 1.27)
\t\t\t\t)
\t\t\t\t(hide yes)
\t\t\t)
\t\t)
\t\t(property "Datasheet" "~"
\t\t\t(at {x:.2f} {y:.2f} 0)
\t\t\t(effects
\t\t\t\t(font
\t\t\t\t\t(size 1.27 1.27)
\t\t\t\t)
\t\t\t\t(hide yes)
\t\t\t)
\t\t)
{pin_entries}
\t\t(instances
\t\t\t(project "{project_name}"
\t\t\t\t(path "/{SCHEMATIC_UUID}"
\t\t\t\t\t(reference "{ref}")
\t\t\t\t\t(unit 1)
\t\t\t\t)
\t\t\t)
\t\t)
\t)
'''


def label(name: str, x: float, y: float, angle: int = 0) -> str:
    justify = "right bottom" if angle == 180 else "left bottom"
    return f'''\
\t(label "{name}"
\t\t(at {x:.2f} {y:.2f} {angle})
\t\t(effects
\t\t\t(font
\t\t\t\t(size 1.0 1.0)
\t\t\t)
\t\t\t(justify {justify})
\t\t)
\t\t(uuid "{stable_uuid("label-" + name + f"-{x:.2f}-{y:.2f}")}")
\t)
'''


def labels_for_symbol(x: float, y: float, pins: list[tuple[str, str, str, float]], labels: dict[str, str]) -> str:
    out = []
    for number, _, side, pin_y in pins:
        if number not in labels:
            continue
        lx = x - 15.24 if side == "left" else x + 15.24
        ly = y - pin_y
        angle = 0 if side == "left" else 180
        out.append(label(labels[number], lx, ly, angle))
    return "".join(out)


def no_connect(x: float, y: float) -> str:
    return f'''\
\t(no_connect
\t\t(at {x:.2f} {y:.2f})
\t\t(uuid "{stable_uuid(f"nc-{x:.2f}-{y:.2f}")}")
\t)
'''


def no_connects_for_symbol(
    x: float,
    y: float,
    pins: list[tuple[str, str, str, float]],
    connected_pin_numbers: set[str],
) -> str:
    out = []
    for number, _, side, pin_y in pins:
        if number in connected_pin_numbers:
            continue
        nx = x - 15.24 if side == "left" else x + 15.24
        ny = y - pin_y
        out.append(no_connect(nx, ny))
    return "".join(out)


def build_schematic() -> str:
    project_name = "sd-led-card"
    mcu_x, mcu_y = 120.65, 85.09
    sd_x, sd_y = 45.72, 60.96
    dbg_x, dbg_y = 45.72, 104.14
    touch_x, touch_y = 45.72, 130.81
    cap1_x, cap_y = 95.25, 130.81
    cap2_x = 110.49
    led_x0, led_y, led_pitch = 45.72, 160.02, 24.13
    mcu_left = [
        ("1", "GP0/SD_CMD", "left", 24.13),
        ("2", "GP1/SD_CLK", "left", 21.59),
        ("3", "GP2/SD_DAT0", "left", 19.05),
        ("4", "GP3/SD_DAT1", "left", 16.51),
        ("5", "GP4/SD_DAT2", "left", 13.97),
        ("6", "GP5/SD_DAT3", "left", 11.43),
        ("7", "GP6/LED_DIN", "left", 8.89),
        ("8", "GP7/CAP_TOUCH", "left", 6.35),
        ("9", "SWDIO", "left", 3.81),
        ("10", "SWCLK", "left", 1.27),
        ("11", "RUN", "left", -1.27),
        ("12", "UART_TX", "left", -3.81),
        ("13", "UART_RX", "left", -6.35),
        ("14", "3V3", "left", -8.89),
        ("15", "GND", "left", -11.43),
    ]
    mcu_right = [(str(i), f"NC{i}", "right", 24.13 - (i - 16) * 1.27) for i in range(16, 61)]
    mcu_pins = mcu_left + mcu_right
    sd_pins = [
        ("1", "DAT2", "right", 10.16),
        ("2", "DAT3/CD", "right", 7.62),
        ("3", "CMD", "right", 5.08),
        ("4", "VDD", "right", 2.54),
        ("5", "CLK", "right", 0),
        ("6", "VSS", "right", -2.54),
        ("7", "DAT0", "right", -5.08),
        ("8", "DAT1", "right", -7.62),
        ("9", "VSS2", "right", -10.16),
    ]
    led_pins = [
        ("1", "VDD", "left", 3.81),
        ("2", "DOUT", "right", 1.27),
        ("3", "GND", "left", -1.27),
        ("4", "DIN", "right", -3.81),
    ]
    cap_pins = [("1", "1", "left", 1.27), ("2", "2", "left", -1.27)]
    dbg_pins = [
        ("1", "SWDIO", "right", 8.89),
        ("2", "SWCLK", "right", 6.35),
        ("3", "RUN", "right", 3.81),
        ("4", "3V3", "right", 1.27),
        ("5", "GND", "right", -1.27),
        ("6", "UART_TX", "right", -3.81),
        ("7", "UART_RX", "right", -6.35),
        ("8", "BOOTSEL", "right", -8.89),
    ]
    touch_pins = [("1", "TOUCH", "right", 0)]

    lib_symbols = "".join(
        [
            symbol_def("SDLED:RP2350A_QFN60_Min", "U", "RP2350A", mcu_pins),
            symbol_def("SDLED:SD_Edge_9Pin", "J", "SD edge contacts", sd_pins),
            symbol_def("SDLED:Addressable_Side_RGB", "D", "Side RGB addressable LED", led_pins),
            symbol_def("SDLED:Capacitor", "C", "Capacitor", cap_pins),
            symbol_def("SDLED:DebugPads_8", "J", "SWD/debug pads", dbg_pins),
            symbol_def("SDLED:TouchPad", "TP", "Cap touch electrode", touch_pins),
        ]
    )

    symbols = [
        placed_symbol("SDLED:RP2350A_QFN60_Min", "U1", "RP2350A", "Package_DFN_QFN:QFN-60-1EP_7x7mm_P0.4mm_EP3.4x3.4mm", mcu_x, mcu_y, mcu_pins, project_name),
        placed_symbol("SDLED:SD_Edge_9Pin", "J1", "SD edge contacts", "Connector_Card:SD_Card_Device_16mm_SlotDepth", sd_x, sd_y, sd_pins, project_name),
        placed_symbol("SDLED:DebugPads_8", "DBG1", "SWD/debug pads", "SDLED:Debug_Robot_Pads_8", dbg_x, dbg_y, dbg_pins, project_name),
        placed_symbol("SDLED:TouchPad", "CT1", "Cap touch", "SDLED:Cap_Touch_Pad", touch_x, touch_y, touch_pins, project_name),
        placed_symbol("SDLED:Capacitor", "C1", "100n", "Capacitor_SMD:C_0402_1005Metric", cap1_x, cap_y, cap_pins, project_name),
        placed_symbol("SDLED:Capacitor", "C2", "1u", "Capacitor_SMD:C_0402_1005Metric", cap2_x, cap_y, cap_pins, project_name),
    ]
    for i in range(6):
        symbols.append(
            placed_symbol(
                "SDLED:Addressable_Side_RGB",
                f"D{i + 1}",
                "side RGB addressable",
                "LED_SMD:LED_RGB_Everlight_EASV3015RGBA0_Horizontal",
                led_x0 + i * led_pitch,
                led_y,
                led_pins,
                project_name,
            )
        )

    labels = []
    mcu_labels = {
        "1": "SD_CMD", "2": "SD_CLK", "3": "SD_DAT0", "4": "SD_DAT1",
        "5": "SD_DAT2", "6": "SD_DAT3", "7": "LED_D0", "8": "CAP_TOUCH",
        "9": "SWDIO", "10": "SWCLK", "11": "RUN", "12": "UART_TX",
        "13": "UART_RX", "14": "+3V3", "15": "GND",
    }
    sd_labels = {
        "1": "SD_DAT2", "2": "SD_DAT3", "3": "SD_CMD", "4": "+3V3",
        "5": "SD_CLK", "6": "GND", "7": "SD_DAT0", "8": "SD_DAT1", "9": "GND",
    }
    dbg_labels = {
        "1": "SWDIO", "2": "SWCLK", "3": "RUN", "4": "+3V3",
        "5": "GND", "6": "UART_TX", "7": "UART_RX", "8": "BOOTSEL",
    }
    labels.append(labels_for_symbol(mcu_x, mcu_y, mcu_pins, mcu_labels))
    labels.append(no_connects_for_symbol(mcu_x, mcu_y, mcu_pins, set(mcu_labels)))
    labels.append(labels_for_symbol(sd_x, sd_y, sd_pins, sd_labels))
    labels.append(labels_for_symbol(dbg_x, dbg_y, dbg_pins, dbg_labels))
    labels.append(labels_for_symbol(touch_x, touch_y, touch_pins, {"1": "CAP_TOUCH"}))
    labels.append(labels_for_symbol(cap1_x, cap_y, cap_pins, {"1": "+3V3", "2": "GND"}))
    labels.append(labels_for_symbol(cap2_x, cap_y, cap_pins, {"1": "+3V3", "2": "GND"}))
    for i in range(6):
        din = "LED_D0" if i == 0 else f"LED_D{i}"
        dout = f"LED_D{i + 1}"
        led_labels = {
            "1": "+3V3", "2": dout, "3": "GND", "4": din,
        }
        if i == 5:
            led_labels.pop("2")
        x = led_x0 + i * led_pitch
        labels.append(labels_for_symbol(x, led_y, led_pins, led_labels))
        if i == 5:
            labels.append(no_connects_for_symbol(x, led_y, led_pins, set(led_labels)))

    return f'''(kicad_sch
\t(version 20250114)
\t(generator "sd-led-card-scaffold")
\t(generator_version "1.0")
\t(uuid "{SCHEMATIC_UUID}")
\t(paper "A4")
\t(title_block
\t\t(title "SD LED Card")
\t\t(rev "R0")
\t\t(comment 1 "Functional schematic for SD emulator, RGB LEDs, capacitive touch, and debug pads.")
\t)
\t(lib_symbols
{lib_symbols}\t)
{"".join(labels)}{"".join(symbols)}\t(symbol_instances)
\t(embedded_fonts no)
)
'''


def add_edge_arc(board: pcbnew.BOARD, start, mid, end) -> None:
    shape = pcbnew.PCB_SHAPE(board)
    shape.SetShape(pcbnew.SHAPE_T_ARC)
    shape.SetLayer(pcbnew.Edge_Cuts)
    shape.SetWidth(pcbnew.FromMM(0.12))
    shape.SetArcGeometry(mm(*start), mm(*mid), mm(*end))
    board.Add(shape)


def add_track(board: pcbnew.BOARD, start, end, width: float = 0.15, layer: int = pcbnew.B_Cu) -> None:
    track = pcbnew.PCB_TRACK(board)
    track.SetLayer(layer)
    track.SetWidth(pcbnew.FromMM(width))
    track.SetStart(mm(*start))
    track.SetEnd(mm(*end))
    board.Add(track)


def add_via(board: pcbnew.BOARD, x: float, y: float, diameter: float = 0.42, drill: float = 0.2) -> None:
    via = pcbnew.PCB_VIA(board)
    via.SetPosition(mm(x, y))
    via.SetWidth(pcbnew.FromMM(diameter))
    via.SetDrill(pcbnew.FromMM(drill))
    via.SetLayerPair(pcbnew.F_Cu, pcbnew.B_Cu)
    board.Add(via)


def add_logo(board: pcbnew.BOARD, x: float, y: float, scale: float = 0.105) -> None:
    logo_path = ROOT / "hardware" / "snowpaca_logo_pixels.json"
    if not logo_path.exists():
        return

    data = json.loads(logo_path.read_text(encoding="utf-8"))
    width = data["width"]
    height = data["height"]
    for px, py in data["pixels"]:
        x0 = x + (px - width / 2) * scale
        y0 = y + (py - height / 2) * scale
        add_filled_rect(
            board,
            pcbnew.F_SilkS,
            (x0, y0),
            (x0 + scale * 0.72, y0 + scale * 0.72),
            0.005,
        )


def hide_ref_value(fp) -> None:
    fp.Reference().SetVisible(False)
    fp.Value().SetVisible(False)


def add_back_footprint(board: pcbnew.BOARD, fp) -> None:
    board.Add(fp)
    fp.SetLayerAndFlip(pcbnew.B_Cu)


def move_footprint_layers(fp, layers: set[int], target_layer: int) -> None:
    for item in list(fp.GraphicalItems()):
        if item.GetLayer() in layers:
            item.SetLayer(target_layer)


def set_3d_model(fp, filename: str, scale=(1.0, 1.0, 1.0)) -> None:
    fp.Models().clear()
    model = pcbnew.FP_3DMODEL()
    model.m_Filename = filename
    model.m_Scale.x = scale[0]
    model.m_Scale.y = scale[1]
    model.m_Scale.z = scale[2]
    fp.Add3DModel(model)


def main() -> None:
    board = pcbnew.BOARD()
    board.SetBoardUse(0)
    settings = board.GetDesignSettings()
    settings.SetBoardThickness(pcbnew.FromMM(BOARD_THICKNESS_MM))
    board.SetDesignSettings(settings)

    # Full-size SD-card outline and contacts from KiCad's device-side SD card
    # template. Keeping this as the mechanical/contact source of truth avoids
    # hand-drawn pad geometry drifting away from the real card layout.
    sd_card = load_fp(
        "Connector_Card",
        "SD_Card_Device_16mm_SlotDepth",
        "J1",
        "SD card edge contacts",
        50.0,
        50.0,
    )
    hide_ref_value(sd_card)
    board.Add(sd_card)

    # The KiCad template models the inserted 16 mm contact/mechanical region.
    # Close it into our full visible card by extending the outline to the
    # exposed LED lip.
    add_edge_segment(board, (38, 49.95), (38, 65.0))
    add_edge_arc(board, (38, 65.0), (38.292893, 65.707107), (39, 66.0))
    add_edge_segment(board, (39, 66.0), (61, 66.0))
    add_edge_arc(board, (61, 66.0), (61.707107, 65.707107), (62, 65.0))
    add_edge_segment(board, (62, 65.0), (62, 49.95))

    # RP2350A placeholder footprint. Final symbol/part selection still needs
    # schematic work, but this is the right package class for first placement.
    mcu = load_fp(
        "Package_DFN_QFN",
        "QFN-60-1EP_7x7mm_P0.4mm_EP3.4x3.4mm",
        "U1",
        "RP2350A",
        56.85,
        58.35,
    )
    hide_ref_value(mcu)
    set_3d_model(
        mcu,
        "${KICAD10_3DMODEL_DIR}/Package_DFN_QFN.3dshapes/QFN-56-1EP_7x7mm_P0.4mm_EP4x4mm.step",
    )
    add_back_footprint(board, mcu)

    # Six right-angle RGB LEDs pushed to the exposed edge. The lens side faces
    # the card lip (+Y), so light exits the MacBook slot instead of shining up
    # into the inside of the slot.
    led_x0 = 40.25
    led_pitch = 3.9
    for i in range(6):
        x = led_x0 + i * led_pitch
        led = load_fp(
            "LED_SMD",
            "LED_RGB_Everlight_EASV3015RGBA0_Horizontal",
            f"D{i + 1}",
            "EASV3015 side RGB",
            x,
            65.20,
        )
        hide_ref_value(led)
        set_3d_model(
            led,
            "${KICAD10_3DMODEL_DIR}/LED_SMD.3dshapes/LED_Kingbright_APA1606_1.6x0.6mm_Horizontal.step",
            (1.65, 1.65, 1.65),
        )
        move_footprint_layers(led, {pcbnew.F_SilkS}, pcbnew.F_Fab)
        add_back_footprint(board, led)

    cap = load_fp(
        "Capacitor_SMD",
        "C_0402_1005Metric",
        "C1",
        "100n",
        41.2,
        52.15,
    )
    hide_ref_value(cap)
    add_back_footprint(board, cap)

    cap2 = load_fp(
        "Capacitor_SMD",
        "C_0402_1005Metric",
        "C2",
        "1u",
        43.2,
        52.15,
    )
    hide_ref_value(cap2)
    add_back_footprint(board, cap2)

    # Bare copper/ENIG capacitive touch electrode on the exposed card face.
    # This adds no component height, which is critical for SD-slot clearance.
    add_pad(
        board,
        "CT1",
        "1",
        46.1,
        62.35,
        8.6,
        1.15,
        pcbnew.PAD_SHAPE_ROUNDRECT,
        "back",
    )

    # Keep the front face minimal. Electrical routing should come from the
    # captured schematic/netlist; no decorative no-net copper belongs in a
    # production DRC pass.

    # Debug/programming pads arranged as a simple robot face. Six can carry
    # SWD/debug signals; the two extra bottom pads can be NC or UART/test.
    dbg = [
        (39.8, 51.4), (39.8, 52.7),
        (44.6, 51.4), (44.6, 52.7),
        (39.8, 54.1), (41.4, 54.1), (43.0, 54.1), (44.6, 54.1),
    ]
    add_pad_footprint(
        board,
        "DBG1",
        "SWD/debug pads",
        [
            (str(i), x, y, 0.62, 0.62, pcbnew.PAD_SHAPE_CIRCLE)
            for i, (x, y) in enumerate(dbg, start=1)
        ],
        "back",
    )

    OUT.parent.mkdir(parents=True, exist_ok=True)
    pcbnew.SaveBoard(str(OUT), board)

    project = {
        "board": {"design_settings": {"defaults": {}}},
        "boards": [],
        "cvpcb": {"equivalence_files": []},
        "erc": {"erc_exclusions": []},
        "libraries": {"pinned_footprint_libs": [], "pinned_symbol_libs": []},
        "meta": {"filename": "sd-led-card.kicad_pro", "version": 1},
        "net_settings": {
            "classes": [
                {
                    "bus_width": 12.0,
                    "clearance": 0.15,
                    "diff_pair_gap": 0.25,
                    "diff_pair_via_gap": 0.25,
                    "diff_pair_width": 0.2,
                    "line_style": 0,
                    "microvia_diameter": 0.3,
                    "microvia_drill": 0.1,
                    "name": "Default",
                    "pcb_color": "rgba(0, 0, 0, 0.000)",
                    "schematic_color": "rgba(0, 0, 0, 0.000)",
                    "track_width": 0.15,
                    "via_diameter": 0.45,
                    "via_drill": 0.25,
                    "wire_width": 6.0,
                }
            ]
        },
        "pcbnew": {"page_layout_descr_file": ""},
        "schematic": {"drawing": {"default_line_thickness": 6.0}},
        "sheets": [["00000000-0000-0000-0000-000000000000", "Root"]],
        "text_variables": {},
    }
    if not PRO.exists():
        PRO.write_text(json.dumps(project, indent=2) + "\n")

    SCH.write_text(build_schematic(), encoding="utf-8")

    print(f"Wrote {OUT}")
    print(f"Wrote {PRO}")
    print(f"Wrote {SCH}")


if __name__ == "__main__":
    main()
