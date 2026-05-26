#!/usr/bin/env python3
"""Generate the first KiCad PCB scaffold for the SD LED card."""

from __future__ import annotations

import json
from pathlib import Path

import pcbnew


ROOT = Path(__file__).resolve().parents[1]
KICAD = Path("/Users/xzm/Applications/KiCad/KiCad.app/Contents/SharedSupport")
OUT = ROOT / "hardware" / "sd-led-card.kicad_pcb"
PRO = ROOT / "hardware" / "sd-led-card.kicad_pro"
SCH = ROOT / "hardware" / "sd-led-card.kicad_sch"
BOARD_THICKNESS_MM = 0.8
CONTACT_REGION_STIFFENER_MM = 0.6
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

    # Manufacturing/mechanical note only: with a 0.8 mm PCB, add a 0.6 mm
    # nonconductive stiffener on the non-contact side of the inserted region.
    # That brings the spring-contact area to 1.4 mm while the component area
    # stays below normal 2.1 mm full-size SD thickness.
    add_rect_outline(
        board,
        pcbnew.User_1,
        38.25,
        INSERTED_REGION_MIN_Y_MM + 0.25,
        61.75,
        INSERTED_REGION_MAX_Y_MM - 0.25,
    )
    add_layer_text(
        board,
        f"MECH: F-side +{CONTACT_REGION_STIFFENER_MM:.1f}mm stiffener here",
        39.1,
        46.9,
        pcbnew.User_1,
        0.55,
    )

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
    for i, (x, y) in enumerate(dbg, start=1):
        add_pad(board, "DBG", str(i), x, y, 0.62, 0.62, pcbnew.PAD_SHAPE_CIRCLE, "back")

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
    PRO.write_text(json.dumps(project, indent=2) + "\n")

    SCH.write_text(
        """(kicad_sch
  (version 20250114)
  (generator "sd-led-card-scaffold")
  (paper "A4")
  (title_block
    (title "SD LED Card")
    (rev "R0")
    (comment 1 "Schematic capture pending; PCB scaffold uses KiCad SD-card-device footprint.")
  )
  (lib_symbols)
  (symbol_instances)
)
""",
        encoding="utf-8",
    )

    print(f"Wrote {OUT}")
    print(f"Wrote {PRO}")
    print(f"Wrote {SCH}")


if __name__ == "__main__":
    main()
