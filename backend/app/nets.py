from typing import Optional, List

NETS = [
    {
        "id": "pp_10x10_3mm",
        "name": "Siatka polipropylenowa PP, oczko 10×10 cm, śr. sznurka 3 mm",
        "price_netto": 8.30,
        "description": "Standardowa siatka PP – ekonomiczna, UV-stabilizowana",
    },
    {
        "id": "pp_10x10_4mm",
        "name": "Siatka polipropylenowa PP, oczko 10×10 cm, śr. sznurka 4 mm",
        "price_netto": 14.00,
        "description": "Wzmocniona siatka PP – większa trwałość",
    },
    {
        "id": "pe_10x10_3mm",
        "name": "Siatka polietylenowa PE, oczko 10×10 cm, śr. sznurka 3 mm",
        "price_netto": 12.00,
        "description": "Siatka PE – lepsza odporność na warunki atmosferyczne",
    },
    {
        "id": "pe_10x10_4mm",
        "name": "Siatka polietylenowa PE, oczko 10×10 cm, śr. sznurka 4 mm",
        "price_netto": 16.00,
        "description": "Wzmocniona siatka PE – profesjonalna",
    },
    {
        "id": "pa_10x10_3mm",
        "name": "Siatka poliamidowa PA (nylon), oczko 10×10 cm, śr. sznurka 3 mm",
        "price_netto": 18.00,
        "description": "Siatka nylonowa – najwyższa wytrzymałość i elastyczność",
    },
]


def get_net_by_id(net_id: str) -> Optional[dict]:
    return next((n for n in NETS if n["id"] == net_id), None)


def get_all_nets() -> List[dict]:
    return NETS
