import math
from typing import List, Dict, Tuple
from .models import (
    CalculationRequest, CalculationResult, LineItem,
    ShapeType, MountingType, QuoteType, Wall
)

# === CENNIK (wartości BRUTTO w PLN) ===
VAT_RATE = 0.23
_VAT = 1 + VAT_RATE

POLE_PRICES_BRUTTO = {
    4: 526.00,
    5: 631.00,
    6: 736.00,
}

BRACE_PRICE_BRUTTO = 430.00
SLEEVE_PRICE_BRUTTO = 233.00
TRANSPORT_PRICE_BRUTTO = 1500.00

# Zestaw montażowy — stawki jednostkowe NETTO (UniCPO); brutto = netto × (1 + VAT) przy pozycji
ROPE_PRICE_PER_M_NETTO = 2.0
CARABINER_PRICE_PER_UNIT_NETTO = 0.65
TURNBUCKLE_SET_PRICE_NETTO = 60.0
# Śruby oczkowe — 2 szt. na słup, cena jednostkowa brutto
EYE_BOLT_UNIT_PRICE_BRUTTO = 5.0


def _net_markup_multiplier(area_mkw: float) -> float:
    """Mnożnik narzutu na materiał siatkowy (wg progów powierzchni w mkw., jak UniCPO)."""
    if area_mkw <= 5:
        return 2.0
    if area_mkw <= 10:
        return 1.5
    if area_mkw <= 15:
        return 1.3
    return 1.0

# Liczba zastrzałów wg kształtu
SHAPE_BRACES = {
    ShapeType.LINE: 2,
    ShapeType.L: 4,
    ShapeType.U: 6,
    ShapeType.CLOSED: 8,
}

def calculate_poles_for_wall(length: float) -> int:
    """Oblicza liczbę słupów dla ściany o danej długości.

    Zasady:
    - Odległość 1-2 słupa i przedostatni-ostatni: 3 m
    - Odległość pośrednia: max 5,5 m
    """
    if length <= 3:
        return 2
    if length <= 6:
        return 3  # 0, 3, L (gdzie L-3 <= 3, więc nie dublujemy)

    # L > 6: kotwice na 0, 3, L-3, L
    middle_length = length - 6.0  # odcinek między 2. a przedostatnim słupem
    n_spans = math.ceil(middle_length / 5.5)
    n_middle_poles = max(0, n_spans - 1)
    return 4 + n_middle_poles


def extra_braces_for_wall_length(length: float) -> int:
    """Dodatkowe zastrzały na jedną ścianę prostą: powyżej 30 m +2 szt. na każde
    rozpoczęte 30 m (np. 31–60 m → +2, 61–90 m → +4)."""
    if length <= 30:
        return 0
    return 2 * math.ceil((length - 30) / 30)


def _corner_pairs(shape: ShapeType) -> List[Tuple[int, int]]:
    if shape == ShapeType.L:
        return [(0, 1)]
    if shape == ShapeType.U:
        return [(0, 1), (1, 2)]
    if shape == ShapeType.CLOSED:
        return [(0, 1), (1, 2), (2, 3), (3, 0)]
    return []


def _subtract_shared_corners(shape: ShapeType, walls: List[Wall], poles_by_height: Dict[float, int]) -> int:
    """Odejmuje słupy współdzielone w narożnikach z grupowania wg wysokości."""
    shared = 0
    for i, j in _corner_pairs(shape):
        # Narożny słup traktujemy jako należący do niższego z dwóch odcinków,
        # dzięki czemu wyższe słupy za bramkami nie są sztucznie zaniżane.
        h = min(walls[i].height, walls[j].height)
        if poles_by_height.get(h, 0) > 0:
            poles_by_height[h] -= 1
            shared += 1
    return shared


def _as_netto(brutto: float) -> float:
    return round(brutto / _VAT, 2)


def _as_brutto(netto: float) -> float:
    return round(netto * _VAT, 2)


def _line_item(
    name: str,
    unit_price_brutto: float,
    value_brutto: float,
    *,
    height: float | None = None,
    quantity_desc: str | None = None,
    area: float | None = None,
    unit: str = "szt.",
) -> LineItem:
    return LineItem(
        name=name,
        height=height,
        quantity_desc=quantity_desc,
        area=area,
        unit_price_brutto=round(unit_price_brutto, 2),
        value_brutto=round(value_brutto, 2),
        unit_price_netto=_as_netto(unit_price_brutto),
        value_netto=_as_netto(value_brutto),
        unit=unit,
    )


def _line_item_from_netto(
    name: str,
    unit_price_netto: float,
    value_netto: float,
    *,
    height: float | None = None,
    quantity_desc: str | None = None,
    area: float | None = None,
    unit: str = "szt.",
) -> LineItem:
    """Pozycja liczona od cen netto; brutto dopisywane VAT (jak zestaw montażowy)."""
    upn = round(unit_price_netto, 2)
    vn = round(value_netto, 2)
    return LineItem(
        name=name,
        height=height,
        quantity_desc=quantity_desc,
        area=area,
        unit_price_netto=upn,
        value_netto=vn,
        unit_price_brutto=_as_brutto(upn),
        value_brutto=_as_brutto(vn),
        unit=unit,
    )


def calculate(request: CalculationRequest) -> CalculationResult:
    walls_primary = request.walls
    walls_groups = [walls_primary]
    if request.net_layers == 2 and request.walls_secondary:
        walls_groups.append(request.walls_secondary)

    shape = request.shape
    mounting = request.mounting
    quote_type = request.quote_type
    include_mounting_kit = request.include_mounting_kit
    edge_finishing = request.edge_finishing

    # === 1. Obliczenia geometryczne ===
    poles_by_height: Dict[float, int] = {}
    poles_detail = []

    shared_corners = 0
    total_braces = 0
    base_braces = SHAPE_BRACES[shape]

    for layer_idx, walls in enumerate(walls_groups, start=1):
        for i, wall in enumerate(walls):
            n = calculate_poles_for_wall(wall.length)
            poles_by_height[wall.height] = poles_by_height.get(wall.height, 0) + n
            poles_detail.append({
                "layer": layer_idx,
                "wall": i + 1,
                "length": wall.length,
                "height": wall.height,
                "poles": n,
            })
        shared_corners += _subtract_shared_corners(shape, walls, poles_by_height)
        extra_braces = sum(extra_braces_for_wall_length(w.length) for w in walls)
        total_braces += base_braces + extra_braces

    total_poles = max(0, sum(poles_by_height.values()))

    # Powierzchnia siatek i akcesoria siatkowe (dla 1 lub 2 warstw)
    net_area = sum(w.length * w.height for group in walls_groups for w in group)

    # Obwód (długość linki) — obwód każdej siatki zaokrąglony w górę
    rope_length = sum(math.ceil(2 * (w.length + w.height)) for group in walls_groups for w in group)

    # Akcesoria (wartości pośrednie do podglądu / PDF) — jak UniCPO
    eye_bolts_count = 2 * total_poles if include_mounting_kit else 0
    carabiners_count = math.ceil(rope_length * 3 / 100) * 100 if include_mounting_kit else 0
    # Komplety śrub rzymskich: max(1, floor(obwód_segmentu/30)) na ścianę (obwód = 2×(dł.+wys.))
    turnbuckle_sets = 0
    if include_mounting_kit:
        for group in walls_groups:
            for w in group:
                perim = 2.0 * (w.length + w.height)
                turnbuckle_sets += max(1, math.floor(perim / 30.0))

    items: List[LineItem] = []

    # === 2. Pozycje oferty ===

    # Siatka
    from .nets import get_net_by_id
    net = get_net_by_id(request.net_id)
    if net:
        net_price_brutto = round(net["price_brutto"], 2)
        markup_mult = _net_markup_multiplier(net_area)
        net_value_brutto = round(net_price_brutto * net_area * markup_mult, 2)
        layers_desc = f"{request.net_layers} {'siatki' if request.net_layers == 2 else 'siatka'}"
        if edge_finishing:
            layers_desc += ", obszycie krawędzi: TAK"
        if markup_mult != 1.0:
            layers_desc += f", narzut materiału: ×{markup_mult:g}"
        items.append(_line_item(
            name=net["name"],
            height=walls_primary[0].height if walls_primary else 4,
            quantity_desc=layers_desc,
            area=net_area,
            unit_price_brutto=round(net_price_brutto * markup_mult, 2),
            value_brutto=net_value_brutto,
            unit="mkw.",
        ))

    # Słupy i zastrzały (tylko dla kompletnej wyceny)
    if quote_type == QuoteType.COMPLETE:
        for height, count in sorted(poles_by_height.items()):
            if count <= 0:
                continue
            price = POLE_PRICES_BRUTTO.get(height, POLE_PRICES_BRUTTO[5])
            value = price * count
            items.append(_line_item(
                name=f"Słup stalowy 80×80/3mm, cynkowany+lakier RAL 6005",
                height=height,
                quantity_desc=f"{count} szt.",
                unit_price_brutto=price,
                value_brutto=value,
                unit="szt.",
            ))

        # Zastrzały grupowane wg wysokości i liczone osobno dla każdej siatki.
        braces_by_height: Dict[float, int] = {}
        for walls in walls_groups:
            heights = list(set(w.height for w in walls))
            if len(heights) == 1:
                braces_by_height[heights[0]] = braces_by_height.get(heights[0], 0) + base_braces
            else:
                per_height = base_braces // len(heights)
                remainder = base_braces % len(heights)
                for idx, h in enumerate(sorted(heights)):
                    braces_by_height[h] = braces_by_height.get(h, 0) + per_height + (1 if idx < remainder else 0)

            for wall in walls:
                extra = extra_braces_for_wall_length(wall.length)
                if extra:
                    braces_by_height[wall.height] = braces_by_height.get(wall.height, 0) + extra

        for height, count in sorted(braces_by_height.items()):
            if count > 0:
                price = BRACE_PRICE_BRUTTO
                value = price * count
                items.append(_line_item(
                    name=f"Zastrzał stalowy 60×40/2mm, cynkowany+lakier RAL 6005",
                    height=height,
                    quantity_desc=f"{count} szt.",
                    unit_price_brutto=price,
                    value_brutto=value,
                    unit="szt.",
                ))

    # Tuleje montażowe (tylko przy kompletnej wycenie — przy samej siatce brak słupów w ofercie)
    if quote_type == QuoteType.COMPLETE and mounting == MountingType.SLEEVE:
        sleeve_value = SLEEVE_PRICE_BRUTTO * total_poles
        items.append(_line_item(
            name="Tuleje montażowe cynkowane",
            quantity_desc=f"{total_poles} szt.",
            unit_price_brutto=SLEEVE_PRICE_BRUTTO,
            value_brutto=sleeve_value,
            unit="szt.",
        ))

    if include_mounting_kit:
        rope_value_netto = rope_length * ROPE_PRICE_PER_M_NETTO
        items.append(_line_item_from_netto(
            name="Linka stalowa fi 4 mm",
            quantity_desc=f"{rope_length:.0f} mb",
            unit_price_netto=ROPE_PRICE_PER_M_NETTO,
            value_netto=rope_value_netto,
            unit="mb",
        ))

        if eye_bolts_count > 0:
            items.append(_line_item(
                name="Śruby oczkowe cynkowane",
                quantity_desc=f"{eye_bolts_count} szt.",
                unit_price_brutto=EYE_BOLT_UNIT_PRICE_BRUTTO,
                value_brutto=EYE_BOLT_UNIT_PRICE_BRUTTO * eye_bolts_count,
                unit="szt.",
            ))

        carabiners_value_netto = carabiners_count * CARABINER_PRICE_PER_UNIT_NETTO
        items.append(_line_item_from_netto(
            name="Karabińczyki cynkowane",
            quantity_desc=f"{carabiners_count} szt.",
            unit_price_netto=CARABINER_PRICE_PER_UNIT_NETTO,
            value_netto=carabiners_value_netto,
            unit="szt.",
        ))

        turnbuckle_value_netto = turnbuckle_sets * TURNBUCKLE_SET_PRICE_NETTO
        items.append(_line_item_from_netto(
            name="Komplet śrub rzymskich i zacisków cynkowanych",
            quantity_desc=f"{turnbuckle_sets} kpl.",
            unit_price_netto=TURNBUCKLE_SET_PRICE_NETTO,
            value_netto=turnbuckle_value_netto,
            unit="kpl.",
        ))

    if quote_type == QuoteType.COMPLETE:
        items.append(_line_item(
            name="Transport",
            quantity_desc="1 usługa",
            unit_price_brutto=TRANSPORT_PRICE_BRUTTO,
            value_brutto=TRANSPORT_PRICE_BRUTTO,
            unit="kpl.",
        ))
    else:
        items.append(_line_item(
            name="Koszt dostawy",
            quantity_desc="Koszt dostawy do ustalenia w sklepie sklep.siatki-kramer.pl",
            unit_price_brutto=0.0,
            value_brutto=0.0,
            unit="info",
        ))

    # === 3. Podsumowanie ===
    total_brutto = round(sum((item.value_brutto or 0.0) for item in items), 2)
    total_netto = round(sum((item.value_netto or 0.0) for item in items), 2)
    vat = round(total_brutto - total_netto, 2)

    return CalculationResult(
        items=items,
        total_netto=total_netto,
        vat=vat,
        total_brutto=total_brutto,
        poles_count=total_poles,
        braces_count=total_braces,
        net_area=round(net_area, 2),
        poles_detail=[*poles_detail, {"shared_corners_subtracted": shared_corners}],
        rope_length=rope_length,
        carabiners_count=carabiners_count,
        turnbuckle_sets=turnbuckle_sets,
    )
