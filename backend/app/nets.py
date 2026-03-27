from typing import Optional, List

NETS = [
    {
        "id": "pp_10x10_3mm",
        "name": "Siatka polipropylenowa PP, oczko 10×10 cm, śr. sznurka 3 mm",
        "price_brutto": 8.30,
        "description": "Standardowa siatka PP – ekonomiczna, UV-stabilizowana",
    },
    {
        "id": "pe_10x10_3mm",
        "name": "Siatka polietylenowa PE, oczko 10×10 cm, śr. sznurka 3 mm",
        "price_brutto": 11.69,
        "description": "PE, oczko 10×10 cm, grubość 3 mm",
    },
    {
        "id": "pp_10x10_4mm",
        "name": "Siatka polipropylenowa PP, oczko 10×10 cm, śr. sznurka 4 mm",
        "price_brutto": 10.50,
        "description": "PP, oczko 10×10 cm, grubość 4 mm",
    },
    {
        "id": "pe_10x10_4mm",
        "name": "Siatka polietylenowa PE, oczko 10×10 cm, śr. sznurka 4 mm",
        "price_brutto": 14.15,
        "description": "PE, oczko 10×10 cm, grubość 4 mm",
    },
    {
        "id": "pp_10x10_5mm",
        "name": "Siatka polipropylenowa PP, oczko 10×10 cm, śr. sznurka 5 mm",
        "price_brutto": 16.61,
        "description": "PP, oczko 10×10 cm, grubość 5 mm",
    },
    {
        "id": "pe_10x10_5mm",
        "name": "Siatka polietylenowa PE, oczko 10×10 cm, śr. sznurka 5 mm",
        "price_brutto": 17.22,
        "description": "PE, oczko 10×10 cm, grubość 5 mm",
    },
    {
        "id": "pp_8x8_4mm",
        "name": "Siatka polipropylenowa PP, oczko 8×8 cm, śr. sznurka 4 mm",
        "price_brutto": 12.92,
        "description": "PP, oczko 8×8 cm, grubość 4 mm",
    },
    {
        "id": "pp_8x8_5mm",
        "name": "Siatka polipropylenowa PP, oczko 8×8 cm, śr. sznurka 5 mm",
        "price_brutto": 17.96,
        "description": "PP, oczko 8×8 cm, grubość 5 mm",
    },
    {
        "id": "pe_5x5_4mm",
        "name": "Siatka polietylenowa PE, oczko 5×5 cm, śr. sznurka 4 mm",
        "price_brutto": 19.56,
        "description": "PE, oczko 5×5 cm, grubość 4 mm",
    },
    {
        "id": "pe_5x5_5mm",
        "name": "Siatka polietylenowa PE, oczko 5×5 cm, śr. sznurka 5 mm",
        "price_brutto": 29.98,
        "description": "PE, oczko 5×5 cm, grubość 5 mm",
    },
    {
        "id": "pp_4_5x4_5_3mm",
        "name": "Siatka polipropylenowa PP, oczko 4,5×4,5 cm, śr. sznurka 3 mm",
        "price_brutto": 12.30,
        "description": "PP, oczko 4,5×4,5 cm, grubość 3 mm",
    },
    {
        "id": "pe_4_5x4_5_3mm",
        "name": "Siatka polietylenowa PE, oczko 4,5×4,5 cm, śr. sznurka 3 mm",
        "price_brutto": 15.13,
        "description": "PE, oczko 4,5×4,5 cm, grubość 3 mm",
    },
    {
        "id": "pp_4_5x4_5_4mm",
        "name": "Siatka polipropylenowa PP, oczko 4,5×4,5 cm, śr. sznurka 4 mm",
        "price_brutto": 17.22,
        "description": "PP, oczko 4,5×4,5 cm, grubość 4 mm",
    },
    {
        "id": "pp_4_5x4_5_5mm",
        "name": "Siatka polipropylenowa PP, oczko 4,5×4,5 cm, śr. sznurka 5 mm",
        "price_brutto": 29.40,
        "description": "PP, oczko 4,5×4,5 cm, grubość 5 mm",
    },
    {
        "id": "pp_4x4_2_5mm",
        "name": "Siatka polipropylenowa PP, oczko 4×4 cm, śr. sznurka 2,5 mm",
        "price_brutto": 12.92,
        "description": "PP, oczko 4×4 cm, grubość 2,5 mm",
    },
    {
        "id": "pa_4x4_5mm",
        "name": "Siatka poliamidowa PA, oczko 4×4 cm, śr. sznurka 5 mm",
        "price_brutto": 73.80,
        "description": "PA, oczko 4×4 cm, grubość 5 mm",
    },
    {
        "id": "pes_3x3_4mm",
        "name": "Siatka poliestrowa PES, oczko 3×3 cm, śr. sznurka 4 mm",
        "price_brutto": 73.80,
        "description": "PES, oczko 3×3 cm, grubość 4 mm",
    },
    {
        "id": "pp_2x2_2mm",
        "name": "Siatka polipropylenowa PP, oczko 2×2 cm, śr. sznurka 2 mm",
        "price_brutto": 17.22,
        "description": "PP, oczko 2×2 cm, grubość 2 mm",
    },
]


def get_net_by_id(net_id: str) -> Optional[dict]:
    return next((n for n in NETS if n["id"] == net_id), None)


def get_all_nets() -> List[dict]:
    return NETS
