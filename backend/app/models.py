from pydantic import BaseModel, model_validator
from typing import Optional, List, Dict
from enum import Enum


class ShapeType(str, Enum):
    LINE = "line"      # Linia prosta - 2 zastrzały
    L = "L"            # L - 4 zastrzały
    U = "U"            # U - 6 zastrzałów
    CLOSED = "closed"  # Zamknięty - 8 zastrzałów


SHAPES_WALL_COUNT: Dict[ShapeType, int] = {
    ShapeType.LINE: 1,
    ShapeType.L: 2,
    ShapeType.U: 3,
    ShapeType.CLOSED: 4,
}


class MountingType(str, Enum):
    CONCRETE = "concrete"  # Na stałe w betonie (bez dodatkowych kosztów)
    SLEEVE = "sleeve"      # Tuleje montażowe


class QuoteType(str, Enum):
    NET_ONLY = "net_only"   # Tylko siatka + akcesoria + dostawa
    COMPLETE = "complete"    # Kompletna wycena (słupy + zastrzały + siatka + akcesoria)


class Wall(BaseModel):
    length: float  # długość ściany [m]
    height: float  # wysokość [m] - 4, 5 lub 6


class CalculationRequest(BaseModel):
    shape: ShapeType
    walls: List[Wall]
    mounting: MountingType
    net_id: str
    quote_type: QuoteType

    @model_validator(mode="after")
    def walls_match_shape(self) -> "CalculationRequest":
        expected = SHAPES_WALL_COUNT[self.shape]
        if len(self.walls) != expected:
            raise ValueError(
                f"Liczba ścian ({len(self.walls)}) nie odpowiada kształtowi (wymagane: {expected})."
            )
        return self


class CustomerData(BaseModel):
    name: str
    email: str
    phone: Optional[str] = None
    address: Optional[str] = None


class OfferRequest(BaseModel):
    calculation: CalculationRequest
    customer: CustomerData


class LineItem(BaseModel):
    name: str
    height: Optional[float] = None
    quantity_desc: Optional[str] = None
    area: Optional[float] = None
    unit_price_netto: float
    value_netto: float
    unit: str = "szt."


class CalculationResult(BaseModel):
    items: List[LineItem]
    total_netto: float
    vat: float
    total_brutto: float
    poles_count: int
    braces_count: int
    net_area: float
    poles_detail: List[dict]
    # Akcesoria — wartości pośrednie do wyświetlenia
    rope_length: float          # długość linki stalowej [mb]
    carabiners_count: int       # liczba karabińczyków [szt.]
    turnbuckle_sets: int        # liczba kompletów śrub i zacisków


class OfferResponse(BaseModel):
    offer_number: str
    pdf_url: str
    message: str
