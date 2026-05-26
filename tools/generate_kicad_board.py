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


def front_smd_layers() -> pcbnew.LSET:
    layers = pcbnew.LSET()
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
) -> None:
    fp = pcbnew.FOOTPRINT(board)
    fp.SetReference(ref)
    fp.SetValue(ref)
    fp.Reference().SetVisible(False)
    fp.Value().SetVisible(False)
    pad = pcbnew.PAD(fp)
    pad.SetNumber(number)
    pad.SetAttribute(pcbnew.PAD_ATTRIB_SMD)
    pad.SetShape(shape)
    pad.SetLayerSet(front_smd_layers())
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

    # Full-size SD-card outline, drawn directly so the visible face can carry
    # both contacts and components like the reference render.
    add_edge_segment(board, (38, 65.0), (38, 35))
    add_edge_arc(board, (38, 35), (38.292893, 34.292893), (39, 34))
    add_edge_segment(board, (39, 34), (57.792893, 34))
    add_edge_arc(board, (57.792893, 34), (57.984235, 34.03806), (58.146447, 34.146447))
    add_edge_segment(board, (58.146447, 34.146447), (61.853553, 37.853553))
    add_edge_arc(board, (61.853553, 37.853553), (61.96194, 38.015766), (62, 38.207107))
    add_edge_segment(board, (62, 38.207107), (62, 44))
    add_edge_segment(board, (62, 44), (61.25, 44))
    add_edge_segment(board, (61.25, 44), (61.25, 45.5))
    add_edge_segment(board, (61.25, 45.5), (62, 45.5))
    add_edge_segment(board, (62, 45.5), (62, 65.0))
    add_edge_arc(board, (38, 65.0), (38.292893, 65.707107), (39, 66.0))
    add_edge_segment(board, (39, 66.0), (61, 66.0))
    add_edge_arc(board, (61, 66.0), (61.707107, 65.707107), (62, 65.0))

    # Top-face SD contacts, deliberately visible for the concept render.
    contact_x = [40.2, 42.6, 45.0, 47.4, 49.8, 52.2, 54.6, 57.0, 59.0]
    for i, x in enumerate(contact_x, start=1):
        add_pad(board, "J1", str(i), x, 36.4, 1.45 if i < 8 else 1.1, 3.6)

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
    board.Add(mcu)

    # Six right-angle RGB LEDs pushed to the exposed edge. The lens side faces
    # the card lip (+Y), so light exits the MacBook slot instead of shining up
    # into the inside of the slot.
    led_x0 = 41.0
    for i in range(6):
        x = led_x0 + i * 3.6
        led = load_fp(
            "LED_SMD",
            "LED_RGB_Everlight_EASV3015RGBA0_Horizontal",
            f"D{i + 1}",
            "EASV3015 side RGB",
            x,
            65.08,
        )
        hide_ref_value(led)
        set_3d_model(
            led,
            "${KICAD10_3DMODEL_DIR}/LED_SMD.3dshapes/LED_Kingbright_APA1606_1.6x0.6mm_Horizontal.step",
            (1.65, 1.65, 1.65),
        )
        board.Add(led)
        add_filled_rect(
            board,
            pcbnew.F_SilkS,
            (x - 1.35, 65.58),
            (x + 1.35, 65.94),
            0.01,
        )

    cap = load_fp(
        "Capacitor_SMD",
        "C_0402_1005Metric",
        "C1",
        "100n",
        41.2,
        40.75,
    )
    hide_ref_value(cap)
    board.Add(cap)

    cap2 = load_fp(
        "Capacitor_SMD",
        "C_0402_1005Metric",
        "C2",
        "1u",
        43.2,
        40.75,
    )
    hide_ref_value(cap2)
    board.Add(cap2)

    # Pretty, restrained face text.
    # Keep the front face minimal for now. Branding/text can come back after
    # the mechanical and electrical placement is solid.

    # Visual routing: not final electrical routing, but laid out to show the
    # intended organized topology before full schematic capture.
    for idx, x in enumerate(contact_x):
        add_track(board, (x, 38.4), (52.6 + idx * 0.55, 52.1), 0.12)
    for i in range(6):
        x = led_x0 + i * 3.6
        add_track(board, (52.9 + i * 0.75, 59.8), (x, 63.6), 0.12)

    # Debug/programming pads arranged as a simple robot face. Six can carry
    # SWD/debug signals; the two extra bottom pads can be NC or UART/test.
    dbg = [
        (39.8, 40.0), (39.8, 41.3),
        (44.6, 40.0), (44.6, 41.3),
        (39.8, 42.7), (41.4, 42.7), (43.0, 42.7), (44.6, 42.7),
    ]
    for i, (x, y) in enumerate(dbg, start=1):
        add_pad(board, "DBG", str(i), x, y, 0.62, 0.62, pcbnew.PAD_SHAPE_CIRCLE)

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
