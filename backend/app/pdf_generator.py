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

from .models import CalculationResult, CustomerData, CalculationRequest, ShapeType

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
GREEN = colors.HexColor("#0e6d4d")
LIGHT_GREEN = colors.HexColor("#e6f2ef")
DARK_GRAY = colors.HexColor("#333333")
MID_GRAY = colors.HexColor("#666666")
LIGHT_GRAY = colors.HexColor("#f5f5f5")
WHITE = colors.white

COMPANY_ADDRESS = os.getenv("COMPANY_ADDRESS", "ul. Szkolna 20 62-001 Chludowo k. Poznania")
COMPANY_NIP = os.getenv("COMPANY_NIP", "766-178-66-79")
COMPANY_PHONE = os.getenv("COMPANY_PHONE", "+48 604 127 881")
COMPANY_EMAIL = os.getenv("COMPANY_EMAIL", "sklep@siatki-kramer.pl")
COMPANY_WEBSITE = os.getenv("COMPANY_WEBSITE", "https://sklep.siatki-kramer.pl")

# Ścieżka do pliku logotypu (wstawiany ręcznie)
LOGO_PATH = os.getenv("LOGO_PATH", str(Path(__file__).parent.parent / "assets" / "logo.png"))

VAT_RATE = 0.23

# W PDF w kolumnach cen: netto (jak w sklepie), pozostałe pozycje — brutto
MOUNTING_KIT_ITEM_NAMES = frozenset({
    "Linka stalowa fi 4 mm",
    "Śruby oczkowe cynkowane",
    "Karabińczyki cynkowane",
    "Komplet śrub rzymskich i zacisków cynkowanych",
})

PDF_SHAPE_NAMES = {
    ShapeType.LINE: "Linia prosta",
    ShapeType.L: "Kształt L",
    ShapeType.U: "Kształt U",
    ShapeType.CLOSED: "Zamknięty",
}

PDF_WALL_LABELS_PRIMARY = {
    ShapeType.LINE: ["A1"],
    ShapeType.L: ["A1", "A3"],
    ShapeType.U: ["A1", "A3", "A2"],
    ShapeType.CLOSED: ["A1", "A3", "A2", "A4"],
}

PDF_WALL_LABELS_SECONDARY = {
    ShapeType.LINE: ["A2"],
    ShapeType.L: ["A4", "A2"],
}


def _fmt_dim_m(v: float) -> str:
    s = f"{v:g}"
    return s.replace(".", ",")


def _para_cell(text, style: ParagraphStyle) -> Paragraph:
    """Komórka tabeli z zawijaniem tekstu; escapuje znaki specjalne dla ReportLab Paragraph."""
    if text is None:
        t = "—"
    else:
        t = str(text).strip()
        if not t:
            t = "—"
    return Paragraph(escape(t).replace("\n", "<br/>"), style)


def _logo_fit_box(max_width_mm: float = 50, max_height_mm: float = 18):
    """Logotyp jak wcześniej (mały), bez zniekształceń — dopasowanie do prostokąta z zachowaniem proporcji."""
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
            # Najpierw skaluj do max szerokości
            w = w_max
            h = w_max * (ih / float(iw))
            # Jeśli za wysoko — zmniejsz proporcjonalnie (jak object-fit: contain)
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

    def _style(name, font="DV", **kw):
        return ParagraphStyle(name, parent=styles["Normal"], fontName=font, **kw)

    subtitle_style = _style("Sub", fontSize=9, textColor=MID_GRAY, spaceAfter=2)
    section_hdr = _style("SecHdr", font="DV-Bold", fontSize=10, textColor=WHITE,
                         backColor=GREEN, leftPadding=8, rightPadding=8,
                         spaceBefore=8, spaceAfter=0)
    disclaimer_style = _style("Disc", fontSize=7.5, textColor=MID_GRAY,
                               spaceBefore=10, spaceAfter=4)

    hdr_cell_style = ParagraphStyle(
        "HdrCell", fontName="DV-Bold", fontSize=8,
        textColor=WHITE, alignment=TA_CENTER, leading=10, spaceAfter=0, spaceBefore=0,
    )
    item_cell_style = ParagraphStyle(
        "ItemCell", fontName="DV", fontSize=8,
        textColor=DARK_GRAY, leading=11, spaceAfter=0, spaceBefore=0,
        alignment=TA_LEFT,
    )
    item_cell_center_style = ParagraphStyle(
        "ItemCellC", fontName="DV", fontSize=8,
        textColor=DARK_GRAY, leading=11, spaceAfter=0, spaceBefore=0,
        alignment=TA_CENTER,
    )
    item_cell_right_style = ParagraphStyle(
        "ItemCellR", fontName="DV", fontSize=8,
        textColor=DARK_GRAY, leading=11, spaceAfter=0, spaceBefore=0,
        alignment=TA_RIGHT,
    )
    summary_label_style = ParagraphStyle(
        "SumLabel", fontName="DV", fontSize=9,
        textColor=DARK_GRAY, alignment=TA_RIGHT, leading=11, spaceAfter=0, spaceBefore=0,
    )
    summary_total_style = ParagraphStyle(
        "SumTotal", fontName="DV-Bold", fontSize=9,
        textColor=GREEN, alignment=TA_RIGHT, leading=11, spaceAfter=0, spaceBefore=0,
    )

    story = []
    date_str = datetime.now().strftime("%d.%m.%Y")

    # ── NAGŁÓWEK ────────────────────────────────────────────────
    logo_element = _logo_fit_box(50, 18)

    right_paragraphs = [
        Paragraph("Informacja cenowa",
                  _style("OR", font="DV-Bold", fontSize=14, textColor=GREEN, alignment=TA_RIGHT)),
        Paragraph(f"Nr: {offer_number}",
                  _style("ON", font="DV-Bold", fontSize=11, textColor=DARK_GRAY, alignment=TA_RIGHT)),
        Paragraph(f"Data: {date_str}",
                  _style("OD", fontSize=9, textColor=MID_GRAY, alignment=TA_RIGHT)),
    ]

    company_info = Table(
        [[Paragraph(line, subtitle_style)] for line in [
            COMPANY_ADDRESS,
            f"NIP: {COMPANY_NIP}",
            f"Tel.: {COMPANY_PHONE}",
            COMPANY_EMAIL,
            COMPANY_WEBSITE,
        ]],
        colWidths=[95 * mm],
    )
    company_info.setStyle(TableStyle([
        ("TOPPADDING", (0, 0), (-1, -1), 1),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 1),
    ]))

    right_col = Table([[p] for p in right_paragraphs], colWidths=[80 * mm])
    right_col.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("TOPPADDING", (0, 0), (-1, -1), 2),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
    ]))

    left_col = Table(
        [[logo_element], [company_info]],
        colWidths=[95 * mm],
    )
    left_col.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("TOPPADDING", (0, 0), (-1, -1), 0),
        ("BOTTOMPADDING", (0, 0), (0, 0), 7 * mm),
        ("TOPPADDING", (0, 1), (0, 1), 0),
        ("BOTTOMPADDING", (0, 1), (0, 1), 4),
    ]))

    header_table = Table([[left_col, right_col]], colWidths=[100 * mm, 80 * mm])
    header_table.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP")]))
    story.append(header_table)
    story.append(HRFlowable(width="100%", thickness=2, color=GREEN, spaceAfter=10))

    # ── DANE KLIENTA ────────────────────────────────────────────
    story.append(Paragraph("Dane klienta", section_hdr))
    story.append(Spacer(1, 4))

    customer_rows = [
        ["Imię / Nazwa firmy:", customer.name],
        ["Adres e-mail:", customer.email],
    ]
    if customer.phone:
        customer_rows.append(["Telefon:", customer.phone])
    if customer.address:
        customer_rows.append(["Adres / miejscowość:", customer.address])

    ct = Table(customer_rows, colWidths=[45 * mm, 130 * mm])
    ct.setStyle(TableStyle([
        ("FONTNAME", (0, 0), (0, -1), "DV-Bold"),
        ("FONTNAME", (1, 0), (1, -1), "DV"),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("TEXTCOLOR", (0, 0), (0, -1), MID_GRAY),
        ("TEXTCOLOR", (1, 0), (1, -1), DARK_GRAY),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
        ("ROWBACKGROUNDS", (0, 0), (-1, -1), [WHITE, LIGHT_GRAY]),
    ]))
    story.append(ct)
    story.append(Spacer(1, 8))

    # ── KONFIGURACJA PIŁKOCHWYTU ─────────────────────────────────
    story.append(Paragraph("Konfiguracja piłkochwytu", section_hdr))
    story.append(Spacer(1, 4))

    cfg_style = _style("CfgBody", fontSize=9, textColor=DARK_GRAY, leading=12)
    shape = calculation.shape
    cfg_parts = [
        f"<b>Kształt:</b> {PDF_SHAPE_NAMES.get(shape, shape.value)}",
        f"<b>Liczba piłkochwytów (warstw):</b> {calculation.net_layers}",
        "<b>Wymiary — piłkochwyt 1:</b>",
    ]
    labels_p = PDF_WALL_LABELS_PRIMARY.get(shape, [])
    for i, w in enumerate(calculation.walls):
        lab = labels_p[i] if i < len(labels_p) else f"Ściana {i + 1}"
        cfg_parts.append(
            f"{lab} — {_fmt_dim_m(w.length)} m × {_fmt_dim_m(w.height)} m"
        )

    if calculation.net_layers == 2 and calculation.walls_secondary:
        cfg_parts.append("<b>Wymiary — piłkochwyt 2:</b>")
        labels_s = PDF_WALL_LABELS_SECONDARY.get(shape, labels_p)
        for i, w in enumerate(calculation.walls_secondary):
            lab = labels_s[i] if i < len(labels_s) else f"Ściana {i + 1}"
            cfg_parts.append(
                f"{lab} — {_fmt_dim_m(w.length)} m × {_fmt_dim_m(w.height)} m"
            )

    if calculation.include_mounting_kit:
        eye_bolts = 2 * result.poles_count
        cfg_parts.append("<b>Zestaw montażowy (szczegóły ilościowe):</b>")
        cfg_parts.append(
            f"Linka stalowa: ok. {result.rope_length:.0f} mb (szacowany obwód)"
        )
        cfg_parts.append(f"Śruby oczkowe cynkowane: {eye_bolts} szt.")
        cfg_parts.append(f"Karabińczyki cynkowane: {result.carabiners_count} szt.")
        cfg_parts.append(
            f"Komplety śrub rzymskich i zacisków: {result.turnbuckle_sets} kpl."
        )

    story.append(Paragraph("<br/>".join(cfg_parts), cfg_style))
    story.append(Spacer(1, 8))

    # ── TABELA MATERIAŁÓW ───────────────────────────────────────
    story.append(Paragraph("Zestawienie materiałów", section_hdr))
    story.append(Spacer(1, 4))
    story.append(Paragraph(
        "Pozycje zestawu montażowego w kolumnach cen — wartości netto; pozostałe pozycje — brutto.",
        _style("TabNote", fontSize=7.5, textColor=MID_GRAY, spaceAfter=4),
    ))

    def _hdr(text):
        return Paragraph(text.replace("\n", "<br/>"), hdr_cell_style)

    table_data = [[
        _hdr("Lp."), _hdr("Nazwa towaru"), _hdr("Wys.<br/>[m]"), _hdr("Ilość"),
        _hdr("Pow.<br/>[mkw.]"), _hdr("Cena<br/>jedn."), _hdr("Wartość"),
    ]]

    for i, item in enumerate(result.items, 1):
        unit_brutto = item.unit_price_brutto if item.unit_price_brutto is not None else item.unit_price_netto * (1 + VAT_RATE)
        val_brutto = item.value_brutto if item.value_brutto is not None else item.value_netto * (1 + VAT_RATE)
        if item.name in MOUNTING_KIT_ITEM_NAMES:
            unit_show = float(item.unit_price_netto or 0.0)
            val_show = float(item.value_netto or 0.0)
        else:
            unit_show = float(unit_brutto)
            val_show = float(val_brutto)
        table_data.append([
            _para_cell(str(i), item_cell_center_style),
            _para_cell(item.name, item_cell_style),
            _para_cell(f"{item.height:.0f}" if item.height else "—", item_cell_center_style),
            _para_cell(item.quantity_desc or "—", item_cell_style),
            _para_cell(f"{item.area:.2f}" if item.area else "—", item_cell_right_style),
            _para_cell(f"{unit_show:.2f} zł", item_cell_right_style),
            _para_cell(f"{val_show:.2f} zł", item_cell_right_style),
        ])

    table_data.append(["", "", "", "", "",
                        Paragraph("Razem netto:", summary_label_style),
                        _para_cell(f"{result.total_netto:.2f} zł", item_cell_right_style)])
    table_data.append(["", "", "", "", "",
                        Paragraph("VAT 23%:", summary_label_style),
                        _para_cell(f"{result.vat:.2f} zł", item_cell_right_style)])
    table_data.append(["", "", "", "", "",
                        Paragraph("Razem brutto:", summary_total_style),
                        _para_cell(f"{result.total_brutto:.2f} zł", item_cell_right_style)])

    # Szerokości: szersza kolumna „Ilość” (długie opisy), nazwa może się zawijać
    col_widths = [8 * mm, 52 * mm, 12 * mm, 42 * mm, 15 * mm, 23 * mm, 23 * mm]
    n = len(result.items)

    it = Table(table_data, colWidths=col_widths, repeatRows=1)
    it.setStyle(TableStyle([
        # Nagłówek
        ("BACKGROUND", (0, 0), (-1, 0), GREEN),
        ("TEXTCOLOR", (0, 0), (-1, 0), WHITE),
        ("FONTNAME", (0, 0), (-1, 0), "DV-Bold"),
        ("FONTSIZE", (0, 0), (-1, 0), 8),
        ("ALIGN", (0, 0), (-1, 0), "CENTER"),
        ("VALIGN", (0, 0), (-1, 0), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, 0), 5),
        ("BOTTOMPADDING", (0, 0), (-1, 0), 5),
        # Dane
        ("FONTNAME", (0, 1), (-1, n), "DV"),
        ("FONTSIZE", (0, 1), (-1, n), 8),
        ("TEXTCOLOR", (0, 1), (-1, n), DARK_GRAY),
        ("VALIGN", (0, 1), (-1, n), "TOP"),
        ("TOPPADDING", (0, 1), (-1, n), 4),
        ("BOTTOMPADDING", (0, 1), (-1, n), 4),
        ("ROWBACKGROUNDS", (0, 1), (-1, n), [WHITE, LIGHT_GRAY]),
        ("ALIGN", (0, 1), (0, n), "CENTER"),
        ("ALIGN", (2, 1), (2, n), "CENTER"),
        ("ALIGN", (4, 1), (4, n), "RIGHT"),
        ("ALIGN", (5, 1), (5, n), "RIGHT"),
        ("ALIGN", (6, 1), (6, n), "RIGHT"),
        # Grid
        ("GRID", (0, 0), (-1, n), 0.5, colors.HexColor("#cccccc")),
        ("LINEBELOW", (0, 0), (-1, 0), 1, GREEN),
        # Podsumowanie
        ("FONTNAME", (6, n + 1), (6, n + 2), "DV"),
        ("FONTNAME", (6, n + 3), (6, n + 3), "DV-Bold"),
        ("FONTSIZE", (6, n + 1), (6, -1), 9),
        ("ALIGN", (6, n + 1), (6, -1), "RIGHT"),
        ("TOPPADDING", (0, n + 1), (-1, -1), 4),
        ("BOTTOMPADDING", (0, n + 1), (-1, -1), 4),
        ("BACKGROUND", (5, n + 3), (-1, n + 3), LIGHT_GREEN),
        ("TEXTCOLOR", (5, n + 3), (-1, n + 3), GREEN),
        ("LINEABOVE", (5, n + 1), (-1, n + 1), 1, GREEN),
        ("LINEABOVE", (5, n + 3), (-1, n + 3), 1, GREEN),
    ]))
    story.append(it)
    story.append(Spacer(1, 14))

    # ── DISCLAIMER ──────────────────────────────────────────────
    story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#cccccc")))
    story.append(Paragraph(
        "Wycena jest orientacyjna i nie stanowi oferty w rozumieniu przepisów prawa. "
        "Wycena nie obejmuje kosztów montażu. "
        f"Oferta wygenerowana przez system Siatki Kramer dnia {date_str}.",
        disclaimer_style,
    ))

    doc.build(story)
    return output_path
