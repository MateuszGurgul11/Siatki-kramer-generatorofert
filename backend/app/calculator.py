import math
from typing import List, Dict
from .models import (
    CalculationRequest, CalculationResult, LineItem,
    ShapeType, MountingType, QuoteType, Wall
)

# === CENNIK (wartości netto w PLN) ===
POLE_PRICES_NETTO = {
    4: 427.64,   # 526 brutto / 1.23
    5: 580.00,   # z przykładu kalkulatora
    6: 715.00,   # szacunkowe
}

BRACE_PRICES_NETTO = {
    4: 260.00,   # szacunkowe
    5: 325.00,   # szacunkowe
    6: 390.00,   # z dokumentacji
}

SLEEVE_PRICE_BRUTTO = 233.00       # tuleja montażowa (szt.)
_VAT = 1.23
# Ceny podane jako brutto — dzielone przez 1.23 aby uzyskać netto
ROPE_PRICE_NETTO = round(2.00 / _VAT, 6)        # 2,00 zł brutto/mb
EYE_BOLT_PRICE_NETTO = 3.50                      # cena netto (brak ref. brutto)
CARABINER_PRICE_NETTO = round(0.65 / _VAT, 6)   # 0,65 zł brutto/szt.
TURNBUCKLE_SET_PRICE_NETTO = round(60.00 / _VAT, 6)  # 60,00 zł brutto/kpl.

# Liczba zastrzałów wg kształtu
SHAPE_BRACES = {
    ShapeType.LINE: 2,
    ShapeType.L: 4,
    ShapeType.U: 6,
    ShapeType.CLOSED: 8,
}

VAT_RATE = 0.23


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


def calculate(request: CalculationRequest) -> CalculationResult:
    walls = request.walls
    shape = request.shape
    mounting = request.mounting
    quote_type = request.quote_type

    # === 1. Obliczenia geometryczne ===
    total_poles = 0
    poles_detail = []

    for i, wall in enumerate(walls):
        n = calculate_poles_for_wall(wall.length)
        total_poles += n
        poles_detail.append({
            "wall": i + 1,
            "length": wall.length,
            "height": wall.height,
            "poles": n,
        })

    base_braces = SHAPE_BRACES[shape]
    extra_braces_total = sum(extra_braces_for_wall_length(w.length) for w in walls)
    total_braces = base_braces + extra_braces_total

    # Powierzchnia siatki
    net_area = sum(w.length * w.height for w in walls)

    # Obwód (długość linki) — obwód każdej siatki zaokrąglony w górę
    rope_length = sum(math.ceil(2 * (w.length + w.height)) for w in walls)

    # Akcesoria
    eye_bolts_count = 2 * total_poles
    # Karabińczyki: 3 szt. na każdy metr linki, liczone w paczkach po 100 szt.
    carabiners_count = math.ceil(rope_length * 3 / 100) * 100
    # Śruby i zaciski: 1 kpl. na każde rozpoczęte 30 mb długości, każda siatka osobno
    turnbuckle_sets = sum(math.ceil(w.length / 30) for w in walls)

    items: List[LineItem] = []

    # === 2. Pozycje oferty ===

    # Siatka
    from .nets import get_net_by_id
    net = get_net_by_id(request.net_id)
    if net:
        net_value = net["price_netto"] * net_area
        items.append(LineItem(
            name=net["name"],
            height=walls[0].height if walls else 4,
            quantity_desc=f"{rope_length:.1f} mb × {len(walls)} ściany" if len(walls) > 1 else f"{walls[0].length:.1f} mb",
            area=net_area,
            unit_price_netto=net["price_netto"],
            value_netto=round(net_value, 2),
            unit="mkw.",
        ))

    # Słupy i zastrzały (tylko dla kompletnej wyceny)
    if quote_type == QuoteType.COMPLETE:
        # Grupuj słupy wg wysokości
        poles_by_height: Dict[float, int] = {}
        for wall in walls:
            n = calculate_poles_for_wall(wall.length)
            poles_by_height[wall.height] = poles_by_height.get(wall.height, 0) + n

        for height, count in sorted(poles_by_height.items()):
            price = POLE_PRICES_NETTO.get(height, POLE_PRICES_NETTO[5])
            value = price * count
            items.append(LineItem(
                name=f"Słup stalowy 80×80/3mm, cynkowany+lakier RAL 6005",
                height=height,
                quantity_desc=f"{count} szt.",
                unit_price_netto=price,
                value_netto=round(value, 2),
                unit="szt.",
            ))

        # Zastrzały (grupuj wg wysokości): baza wg kształtu, potem dodatki za długość ściany
        braces_by_height: Dict[float, int] = {}
        heights = list(set(w.height for w in walls))
        if len(heights) == 1:
            braces_by_height[heights[0]] = base_braces
        else:
            for h in heights:
                braces_by_height[h] = base_braces // len(heights)

        for wall in walls:
            extra = extra_braces_for_wall_length(wall.length)
            if extra:
                braces_by_height[wall.height] = braces_by_height.get(wall.height, 0) + extra

        for height, count in sorted(braces_by_height.items()):
            if count > 0:
                price = BRACE_PRICES_NETTO.get(height, BRACE_PRICES_NETTO[6])
                value = price * count
                items.append(LineItem(
                    name=f"Zastrzał stalowy 60×40/2mm, cynkowany+lakier RAL 6005",
                    height=height,
                    quantity_desc=f"{count} szt.",
                    unit_price_netto=price,
                    value_netto=round(value, 2),
                    unit="szt.",
                ))

    # Tuleje montażowe
    if mounting == MountingType.SLEEVE:
        sleeve_value = SLEEVE_PRICE_BRUTTO * total_poles
        items.append(LineItem(
            name="Tuleje montażowe cynkowane",
            quantity_desc=f"{total_poles} szt.",
            unit_price_netto=SLEEVE_PRICE_BRUTTO,
            value_netto=round(sleeve_value, 2),
            unit="szt.",
        ))

    # Linka stalowa fi 4mm
    rope_value = ROPE_PRICE_NETTO * rope_length
    items.append(LineItem(
        name="Linka stalowa fi 4 mm",
        quantity_desc=f"{rope_length:.0f} mb",
        unit_price_netto=ROPE_PRICE_NETTO,
        value_netto=round(rope_value, 2),
        unit="mb",
    ))

    # Śruby oczkowe cynkowane
    eye_bolt_value = EYE_BOLT_PRICE_NETTO * eye_bolts_count
    items.append(LineItem(
        name="Śruby oczkowe cynkowane",
        quantity_desc=f"{eye_bolts_count} szt.",
        unit_price_netto=EYE_BOLT_PRICE_NETTO,
        value_netto=round(eye_bolt_value, 2),
        unit="szt.",
    ))

    # Karabińczyki cynkowane
    carabiner_value = CARABINER_PRICE_NETTO * carabiners_count
    items.append(LineItem(
        name="Karabińczyki cynkowane",
        quantity_desc=f"{carabiners_count} szt.  (3 szt./mb linki, paczki po 100)",
        unit_price_netto=CARABINER_PRICE_NETTO,
        value_netto=round(carabiner_value, 2),
        unit="szt.",
    ))

    # Śruby rzymskie + zaciski
    turnbuckle_value = TURNBUCKLE_SET_PRICE_NETTO * turnbuckle_sets
    items.append(LineItem(
        name="Komplet śrub rzymskich i zacisków cynkowanych",
        quantity_desc=f"{turnbuckle_sets} kpl.  (1 kpl./30 mb dł., każda siatka osobno)",
        unit_price_netto=TURNBUCKLE_SET_PRICE_NETTO,
        value_netto=round(turnbuckle_value, 2),
        unit="kpl.",
    ))

    # === 3. Podsumowanie ===
    total_netto = round(sum(item.value_netto for item in items), 2)
    vat = round(total_netto * VAT_RATE, 2)
    total_brutto = round(total_netto + vat, 2)

    return CalculationResult(
        items=items,
        total_netto=total_netto,
        vat=vat,
        total_brutto=total_brutto,
        poles_count=total_poles,
        braces_count=total_braces,
        net_area=round(net_area, 2),
        poles_detail=poles_detail,
        rope_length=rope_length,
        carabiners_count=carabiners_count,
        turnbuckle_sets=turnbuckle_sets,
    )
