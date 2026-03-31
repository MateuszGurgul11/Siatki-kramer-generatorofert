import os
from datetime import datetime
from pathlib import Path
from xml.sax.saxutils import escape
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, HRFlowable,
    KeepTogether,
)
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.graphics.shapes import Drawing, Rect, String
from reportlab.graphics import renderPDF

from .models import CalculationResult, CustomerData, CalculationRequest, ShapeType, MountingType, QuoteType

# === FONTS ===
_FONTS_DIR = Path(__file__).parent.parent / "fonts"
_FONT_REGULAR = str(_FONTS_DIR / "DejaVuSans.ttf")
_FONT_BOLD = str(_FONTS_DIR / "DejaVuSans-Bold.ttf")

_fonts_registered = False

def _ensure_fonts():
    global _fonts_registered
    if _fonts_registered:
        return
    pdfmetrics.registerFont(TTFont("DV", _FONT_REGULAR))
    pdfmetrics.registerFont(TTFont("DV-Bold", _FONT_BOLD))
    pdfmetrics.registerFontFamily("DV", normal="DV", bold="DV-Bold")
    _fonts_registered = True

# Kolory firmowe
GREEN        = colors.HexColor("#0e6d4d")
GREEN_DARK   = colors.HexColor("#0a5239")
LIGHT_GREEN  = colors.HexColor("#e6f2ef")
ACCENT_GREEN = colors.HexColor("#d0eae3")
DARK_GRAY    = colors.HexColor("#222222")
MID_GRAY     = colors.HexColor("#666666")
LIGHT_GRAY   = colors.HexColor("#f7f7f7")
ROW_ALT      = colors.HexColor("#f0f8f5")
WHITE        = colors.white
BORDER_COLOR = colors.HexColor("#d0d0d0")

COMPANY_ADDRESS = os.getenv("COMPANY_ADDRESS", "ul. Szkolna 20 62-001 Chludowo k. Poznania")
COMPANY_NIP     = os.getenv("COMPANY_NIP",     "766-178-66-79")
COMPANY_PHONE   = os.getenv("COMPANY_PHONE",   "+48 604 127 881")
COMPANY_EMAIL   = os.getenv("COMPANY_EMAIL",   "sklep@siatki-kramer.pl")
COMPANY_WEBSITE = os.getenv("COMPANY_WEBSITE", "https://sklep.siatki-kramer.pl")
LOGO_PATH       = os.getenv("LOGO_PATH",       str(Path(__file__).parent.parent / "assets" / "logo.png"))

VAT_RATE = 0.23


def _fmt_money(v: float) -> str:
    return f"{float(v):.2f} zł"


PDF_SHAPE_NAMES = {
    ShapeType.LINE:   "Linia prosta",
    ShapeType.L:      "Kształt L",
    ShapeType.U:      "Kształt U",
    ShapeType.CLOSED: "Zamknięty",
}

PDF_WALL_LABELS_PRIMARY = {
    ShapeType.LINE:   ["A1"],
    ShapeType.L:      ["A1", "A3"],
    ShapeType.U:      ["A1", "A3", "A2"],
    ShapeType.CLOSED: ["A1", "A3", "A2", "A4"],
}

PDF_WALL_LABELS_SECONDARY = {
    ShapeType.LINE: ["A2"],
    ShapeType.L:    ["A4", "A2"],
}


def _fmt_dim_m(v: float) -> str:
    return f"{v:g}".replace(".", ",")


def _para(text, style: ParagraphStyle) -> Paragraph:
    if text is None:
        t = "—"
    else:
        t = str(text).strip() or "—"
    return Paragraph(escape(t).replace("\n", "<br/>"), style)


def _logo_fit_box(max_width_mm: float = 50, max_height_mm: float = 18):
    from reportlab.platypus import Image
    w_max = max_width_mm * mm
    h_max = max_height_mm * mm
    if os.path.exists(LOGO_PATH):
        try:
            from reportlab.lib.utils import ImageReader
            ir = ImageReader(LOGO_PATH)
            iw, ih = ir.getSize()
            if iw <= 0:
                iw, ih = 1, 1
            w = w_max
            h = w_max * (ih / float(iw))
            if h > h_max:
                h = h_max
                w = h_max * (iw / float(ih))
        except Exception:
            w, h = w_max, min(h_max, w_max * 0.36)
        return Image(LOGO_PATH, width=w, height=h)
    w, h = w_max, min(h_max, w_max * 0.36)
    d = Drawing(w, h)
    d.add(Rect(0, 0, w, h, fillColor=colors.HexColor("#e0e0e0"),
               strokeColor=colors.HexColor("#aaaaaa"), strokeWidth=1))
    d.add(String(w / 2, h / 2 - 4, "[ LOGO FIRMY ]",
                 fontName="DV", fontSize=9, fillColor=MID_GRAY,
                 textAnchor="middle"))
    return d


def _section_header(text: str, style: ParagraphStyle) -> list:
    """Nagłówek sekcji z zielonym tłem + mały margines."""
    return [Paragraph(text, style), Spacer(1, 4 * mm)]


def _kv_table(rows: list, col_widths: list, lbl_style, val_style) -> Table:
    """Tabela klucz–wartość (2 kolumny) ze zebrowaniem."""
    data = [[_para(lbl, lbl_style), _para(val, val_style)] for lbl, val in rows]
    t = Table(data, colWidths=col_widths)
    n = len(data)
    style_cmds = [
        ("TOPPADDING",    (0, 0), (-1, -1), 3.5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3.5),
        ("LEFTPADDING",   (0, 0), (-1, -1), 6),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 6),
        ("VALIGN",        (0, 0), (-1, -1), "MIDDLE"),
        ("LINEBELOW",     (0, 0), (-1, n - 1), 0.4, BORDER_COLOR),
    ]
    for i in range(n):
        bg = ROW_ALT if i % 2 == 0 else WHITE
        style_cmds.append(("BACKGROUND", (0, i), (-1, i), bg))
    t.setStyle(TableStyle(style_cmds))
    return t


def generate_pdf(
    offer_number: str,
    customer: CustomerData,
    result: CalculationResult,
    output_path: str,
    calculation: CalculationRequest,
) -> str:
    """Generuje plik PDF oferty i zwraca ścieżkę."""
    _ensure_fonts()
    os.makedirs(os.path.dirname(output_path) if os.path.dirname(output_path) else ".", exist_ok=True)

    doc = SimpleDocTemplate(
        output_path,
        pagesize=A4,
        rightMargin=15 * mm,
        leftMargin=15 * mm,
        topMargin=15 * mm,
        bottomMargin=20 * mm,
    )

    styles = getSampleStyleSheet()

    def S(name, font="DV", **kw):
        return ParagraphStyle(name, parent=styles["Normal"], fontName=font, **kw)

    # Globalne style tekstu
    section_hdr_style = S("SecHdr", font="DV-Bold", fontSize=9.5, textColor=WHITE,
                          backColor=GREEN, leftPadding=8, rightPadding=8,
                          topPadding=5, bottomPadding=5,
                          spaceBefore=0, spaceAfter=0)
    lbl_style = S("Lbl", font="DV-Bold", fontSize=8.5, textColor=MID_GRAY)
    val_style = S("Val", fontSize=8.5, textColor=DARK_GRAY)

    tbl_hdr_style = ParagraphStyle(
        "TblHdr", fontName="DV-Bold", fontSize=7.5, textColor=WHITE,
        alignment=TA_CENTER, leading=9, spaceAfter=0, spaceBefore=0,
    )
    tbl_cell_l = ParagraphStyle(
        "TblL", fontName="DV", fontSize=8, textColor=DARK_GRAY,
        alignment=TA_LEFT, leading=10, spaceAfter=0, spaceBefore=0,
    )
    tbl_cell_c = ParagraphStyle(
        "TblC", fontName="DV", fontSize=8, textColor=DARK_GRAY,
        alignment=TA_CENTER, leading=10, spaceAfter=0, spaceBefore=0,
    )
    tbl_cell_r = ParagraphStyle(
        "TblR", fontName="DV", fontSize=8, textColor=DARK_GRAY,
        alignment=TA_RIGHT, leading=10, spaceAfter=0, spaceBefore=0,
    )
    sum_lbl_style = S("SumLbl", font="DV-Bold", fontSize=9, textColor=MID_GRAY,
                      alignment=TA_RIGHT)
    sum_val_style = S("SumVal", fontSize=9, textColor=DARK_GRAY, alignment=TA_RIGHT)
    sum_total_lbl = S("SumTotL", font="DV-Bold", fontSize=10.5, textColor=WHITE,
                      alignment=TA_RIGHT)
    sum_total_val = S("SumTotV", font="DV-Bold", fontSize=10.5, textColor=WHITE,
                      alignment=TA_RIGHT)
    disclaimer_style = S("Disc", fontSize=7, textColor=MID_GRAY, spaceBefore=6, spaceAfter=2)

    story = []
    date_str = datetime.now().strftime("%d.%m.%Y")

    # ═══════════════════════════════════════════════════════════════
    # NAGŁÓWEK
    # ═══════════════════════════════════════════════════════════════
    logo_el = _logo_fit_box(50, 18)

    offer_block = [
        Paragraph("Informacja cenowa",
                  S("OT", font="DV-Bold", fontSize=16, textColor=GREEN, alignment=TA_RIGHT)),
        Spacer(1, 2),
        Paragraph(f"Nr: <b>{offer_number}</b>",
                  S("ON", fontSize=9, textColor=DARK_GRAY, alignment=TA_RIGHT)),
        Paragraph(f"Data: {date_str}",
                  S("OD", fontSize=8.5, textColor=MID_GRAY, alignment=TA_RIGHT)),
    ]

    company_lines = [
        COMPANY_ADDRESS,
        f"NIP: {COMPANY_NIP}",
        f"Tel.: {COMPANY_PHONE}",
        COMPANY_EMAIL,
        COMPANY_WEBSITE,
    ]
    company_block = Table(
        [[Paragraph(line, S(f"ci{i}", fontSize=8, textColor=MID_GRAY))] for i, line in enumerate(company_lines)],
        colWidths=[95 * mm],
    )
    company_block.setStyle(TableStyle([
        ("TOPPADDING",    (0, 0), (-1, -1), 1),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 1),
    ]))

    right_col = Table([[p] for p in offer_block], colWidths=[80 * mm])
    right_col.setStyle(TableStyle([
        ("VALIGN",        (0, 0), (-1, -1), "TOP"),
        ("TOPPADDING",    (0, 0), (-1, -1), 2),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
    ]))

    left_col = Table([[logo_el], [company_block]], colWidths=[95 * mm])
    left_col.setStyle(TableStyle([
        ("VALIGN",        (0, 0), (-1, -1), "TOP"),
        ("TOPPADDING",    (0, 0), (-1, -1), 0),
        ("BOTTOMPADDING", (0, 0), (0, 0),   6 * mm),
        ("TOPPADDING",    (0, 1), (0, 1),   0),
        ("BOTTOMPADDING", (0, 1), (0, 1),   4),
    ]))

    header_table = Table([[left_col, right_col]], colWidths=[100 * mm, 80 * mm])
    header_table.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP")]))
    story.append(header_table)
    story.append(HRFlowable(width="100%", thickness=2, color=GREEN, spaceAfter=8))

    # ═══════════════════════════════════════════════════════════════
    # DANE KLIENTA
    # ═══════════════════════════════════════════════════════════════
    story.append(Paragraph("Dane klienta", section_hdr_style))
    story.append(Spacer(1, 3))

    cust_rows = [("Imię / Nazwa firmy", customer.name)]
    if customer.email:
        cust_rows.append(("Adres e-mail", customer.email))
    if customer.phone:
        cust_rows.append(("Telefon", customer.phone))
    if customer.address:
        cust_rows.append(("Adres / miejscowość", customer.address))

    story.append(_kv_table(cust_rows, [48 * mm, 127 * mm], lbl_style, val_style))
    story.append(Spacer(1, 7))

    # ═══════════════════════════════════════════════════════════════
    # KONFIGURACJA PIŁKOCHWYTU
    # ═══════════════════════════════════════════════════════════════
    story.append(Paragraph("Konfiguracja piłkochwytu", section_hdr_style))
    story.append(Spacer(1, 3))

    shape = calculation.shape
    labels_p = PDF_WALL_LABELS_PRIMARY.get(shape, [])
    labels_s = PDF_WALL_LABELS_SECONDARY.get(shape, labels_p)

    cfg_rows = [
        ("Kształt", PDF_SHAPE_NAMES.get(shape, shape.value)),
        ("Liczba piłkochwytów (warstw)", str(calculation.net_layers)),
        ("Rodzaj montażu",
         "Tuleje montażowe" if calculation.mounting == MountingType.SLEEVE else "Na stałe (beton)"),
        ("Typ wyceny",
         "Kompletna (słupy + zastrzały + siatka)" if calculation.quote_type == QuoteType.COMPLETE
         else "Tylko siatka + akcesoria"),
        ("Obszycie krawędzi siatki",
         "TAK" if calculation.edge_finishing else "NIE"),
    ]

    # Wymiary ścian – piłkochwyt 1
    for i, w in enumerate(calculation.walls):
        lab = labels_p[i] if i < len(labels_p) else f"Ściana {i + 1}"
        prefix = "Wymiary piłkochwyt 1 –" if len(calculation.walls) == 1 else f"Piłkochwyt 1 – ściana {lab}:"
        cfg_rows.append((
            prefix.rstrip(":"),
            f"{_fmt_dim_m(w.length)} m  ×  {_fmt_dim_m(w.height)} m (dł. × wys.)",
        ))

    # Wymiary ścian – piłkochwyt 2 (jeśli 2 warstwy)
    if calculation.net_layers == 2 and calculation.walls_secondary:
        for i, w in enumerate(calculation.walls_secondary):
            lab = labels_s[i] if i < len(labels_s) else f"Ściana {i + 1}"
            prefix = "Wymiary piłkochwyt 2 –" if len(calculation.walls_secondary) == 1 \
                     else f"Piłkochwyt 2 – ściana {lab}:"
            cfg_rows.append((
                prefix.rstrip(":"),
                f"{_fmt_dim_m(w.length)} m  ×  {_fmt_dim_m(w.height)} m (dł. × wys.)",
            ))

    # Zestaw montażowy
    if calculation.include_mounting_kit:
        eye_bolts = 2 * result.poles_count
        cfg_rows.append(("Zestaw montażowy", "TAK – szczegóły poniżej"))
        cfg_rows.append(("  Linka stalowa fi 4 mm",   f"ok. {result.rope_length:.0f} mb"))
        cfg_rows.append(("  Śruby oczkowe cynkowane", f"{eye_bolts} szt."))
        cfg_rows.append(("  Karabińczyki cynkowane",  f"{result.carabiners_count} szt."))
        cfg_rows.append(("  Komplety śrub i zacisków", f"{result.turnbuckle_sets} kpl."))
    else:
        cfg_rows.append(("Zestaw montażowy", "NIE"))

    story.append(_kv_table(cfg_rows, [72 * mm, 103 * mm], lbl_style, val_style))
    story.append(Spacer(1, 7))

    # ═══════════════════════════════════════════════════════════════
    # TABELA MATERIAŁÓW
    # ═══════════════════════════════════════════════════════════════
    story.append(Paragraph("Zestawienie materiałów", section_hdr_style))
    story.append(Spacer(1, 3))

    def _hdr(text):
        return Paragraph(text.replace("\n", "<br/>"), tbl_hdr_style)

    # Kolumny: Lp. | Nazwa towaru | Wys. | Ilość / opis | Pow. | C.j.netto | C.j.brutto | W.netto | W.brutto
    col_widths = [7*mm, 47*mm, 10*mm, 33*mm, 12*mm, 16*mm, 16*mm, 17*mm, 17*mm]

    table_data = [[
        _hdr("Lp."),
        _hdr("Nazwa towaru"),
        _hdr("Wys.\n[m]"),
        _hdr("Ilość / opis"),
        _hdr("Pow.\n[m²]"),
        _hdr("Cena j.\nnetto"),
        _hdr("Cena j.\nbrutto"),
        _hdr("Wartość\nnetto"),
        _hdr("Wartość\nbrutto"),
    ]]

    for i, item in enumerate(result.items, 1):
        u_n = float(item.unit_price_netto or 0.0)
        u_b = float(item.unit_price_brutto) if item.unit_price_brutto is not None \
              else round(u_n * (1 + VAT_RATE), 2)
        v_n = float(item.value_netto or 0.0)
        v_b = float(item.value_brutto) if item.value_brutto is not None \
              else round(v_n * (1 + VAT_RATE), 2)

        is_info = item.unit == "info"
        price_str = "—" if is_info else _fmt_money(u_n)
        price_b_str = "—" if is_info else _fmt_money(u_b)
        val_n_str  = "—" if is_info else _fmt_money(v_n)
        val_b_str  = "—" if is_info else _fmt_money(v_b)
        pow_str    = f"{item.area:.2f}" if item.area else "—"
        wys_str    = f"{item.height:.0f}" if item.height else "—"

        qty_text = item.quantity_desc or "—"
        if is_info and item.quantity_desc:
            qty_text = item.quantity_desc

        table_data.append([
            _para(str(i),      tbl_cell_c),
            _para(item.name,   tbl_cell_l),
            _para(wys_str,     tbl_cell_c),
            _para(qty_text,    tbl_cell_l),
            _para(pow_str,     tbl_cell_r),
            _para(price_str,   tbl_cell_r),
            _para(price_b_str, tbl_cell_r),
            _para(val_n_str,   tbl_cell_r),
            _para(val_b_str,   tbl_cell_r),
        ])

    n = len(result.items)

    it = Table(table_data, colWidths=col_widths, repeatRows=1)

    tbl_style = TableStyle([
        # Nagłówek
        ("BACKGROUND",    (0, 0), (-1, 0),     GREEN),
        ("TEXTCOLOR",     (0, 0), (-1, 0),     WHITE),
        ("FONTNAME",      (0, 0), (-1, 0),     "DV-Bold"),
        ("FONTSIZE",      (0, 0), (-1, 0),     7.5),
        ("ALIGN",         (0, 0), (-1, 0),     "CENTER"),
        ("VALIGN",        (0, 0), (-1, 0),     "MIDDLE"),
        ("TOPPADDING",    (0, 0), (-1, 0),     5),
        ("BOTTOMPADDING", (0, 0), (-1, 0),     5),
        ("LINEBELOW",     (0, 0), (-1, 0),     1.5, GREEN_DARK),
        # Wiersze danych
        ("FONTNAME",      (0, 1), (-1, n),     "DV"),
        ("FONTSIZE",      (0, 1), (-1, n),     8),
        ("TEXTCOLOR",     (0, 1), (-1, n),     DARK_GRAY),
        ("VALIGN",        (0, 1), (-1, n),     "MIDDLE"),
        ("TOPPADDING",    (0, 1), (-1, n),     4),
        ("BOTTOMPADDING", (0, 1), (-1, n),     4),
        # Poziome oddzielenie wierszy
        ("LINEBELOW",     (0, 1), (-1, n - 1), 0.4, BORDER_COLOR),
        ("LINEBELOW",     (0, n), (-1, n),     1,   BORDER_COLOR),
        # Pionowe linie między kolumnami
        ("LINEBEFORE",    (1, 0), (1, n),      0.3, BORDER_COLOR),
        ("LINEBEFORE",    (4, 0), (4, n),      0.3, BORDER_COLOR),
        ("LINEBEFORE",    (5, 0), (5, n),      0.5, BORDER_COLOR),
        ("LINEBEFORE",    (7, 0), (7, n),      0.5, BORDER_COLOR),
        ("LINEBEFORE",    (8, 0), (8, n),      0.5, BORDER_COLOR),
        # Wyrównania
        ("ALIGN",         (0, 1), (0, n),      "CENTER"),
        ("ALIGN",         (2, 1), (2, n),      "CENTER"),
        ("ALIGN",         (4, 1), (8, n),      "RIGHT"),
    ])

    # Zebra – co drugi wiersz jasno zielony
    for row_i in range(1, n + 1):
        bg = ROW_ALT if row_i % 2 == 1 else WHITE
        tbl_style.add("BACKGROUND", (0, row_i), (-1, row_i), bg)

    it.setStyle(tbl_style)
    story.append(it)
    story.append(Spacer(1, 5))

    # ═══════════════════════════════════════════════════════════════
    # PODSUMOWANIE – osobny blok wyrównany do prawej
    # ═══════════════════════════════════════════════════════════════
    sum_col_lbl = 35 * mm
    sum_col_val = 22 * mm
    sum_total_w = sum_col_lbl + sum_col_val  # 57 mm

    sum_rows = [
        [_para("Razem netto:", sum_lbl_style),
         _para(_fmt_money(result.total_netto), sum_val_style)],
        [_para("VAT 23%:", sum_lbl_style),
         _para(_fmt_money(result.vat), sum_val_style)],
    ]
    sum_tbl_top = Table(sum_rows, colWidths=[sum_col_lbl, sum_col_val])
    sum_tbl_top.setStyle(TableStyle([
        ("TOPPADDING",    (0, 0), (-1, -1), 3.5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3.5),
        ("LEFTPADDING",   (0, 0), (-1, -1), 6),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 6),
        ("LINEBELOW",     (0, 0), (-1, 0),  0.4, BORDER_COLOR),
    ]))

    sum_total_row = Table(
        [[_para("RAZEM BRUTTO:", sum_total_lbl),
          _para(_fmt_money(result.total_brutto), sum_total_val)]],
        colWidths=[sum_col_lbl, sum_col_val],
    )
    sum_total_row.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, -1), GREEN),
        ("TOPPADDING",    (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("LEFTPADDING",   (0, 0), (-1, -1), 6),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 6),
    ]))

    # Wrapujemy w tabelę 2-kolumnową: pusta lewa | blok sum po prawej
    wrapper = Table(
        [[Spacer(1, 1), sum_tbl_top]],
        colWidths=[180 * mm - sum_total_w, sum_total_w],
    )
    wrapper.setStyle(TableStyle([
        ("VALIGN",        (0, 0), (-1, -1), "BOTTOM"),
        ("TOPPADDING",    (0, 0), (-1, -1), 0),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
    ]))
    story.append(wrapper)

    wrapper2 = Table(
        [[Spacer(1, 1), sum_total_row]],
        colWidths=[180 * mm - sum_total_w, sum_total_w],
    )
    wrapper2.setStyle(TableStyle([
        ("VALIGN",        (0, 0), (-1, -1), "TOP"),
        ("TOPPADDING",    (0, 0), (-1, -1), 0),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
    ]))
    story.append(wrapper2)
    story.append(Spacer(1, 10))

    # ═══════════════════════════════════════════════════════════════
    # STOPKA
    # ═══════════════════════════════════════════════════════════════
    story.append(HRFlowable(width="100%", thickness=0.5, color=BORDER_COLOR, spaceAfter=4))
    story.append(Paragraph(
        "Wycena jest orientacyjna i nie stanowi oferty w rozumieniu przepisów prawa. "
        "Wycena nie obejmuje kosztów montażu. "
        f"Oferta wygenerowana przez system Siatki Kramer dnia {date_str}.",
        disclaimer_style,
    ))

    doc.build(story)
    return output_path
