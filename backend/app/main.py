import os
import uuid
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from .models import CalculationRequest, OfferRequest, CalculationResult
from .calculator import calculate
from .database import init_db, get_next_offer_number, save_offer
from .pdf_generator import generate_pdf
from .nets import get_all_nets

app = FastAPI(
    title="Siatki Kramer — Generator Ofert API",
    version="1.0.0",
)

ALLOWED_ORIGINS = [
    "http://localhost:5173",
    "http://localhost:3000",
]
# Dołącz produkcyjny adres frontendu z zmiennej środowiskowej (np. https://xxx.vercel.app)
_frontend_url = os.getenv("FRONTEND_URL", "").strip().rstrip("/")
if _frontend_url:
    ALLOWED_ORIGINS.append(_frontend_url)

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

PDF_DIR = Path(os.getenv("PDF_DIR", "./pdfs"))
PDF_DIR.mkdir(parents=True, exist_ok=True)


@app.on_event("startup")
def startup():
    init_db()


@app.get("/")
def root():
    """Szybka weryfikacja, że serwis działa (wcześniej `/` zwracało 404)."""
    return {
        "service": "Siatki Kramer — Generator Ofert API",
        "docs": "/docs",
        "health": "/health",
    }


@app.get("/api/nets")
def list_nets():
    """Zwraca listę dostępnych siatek."""
    return get_all_nets()


@app.post("/api/calculate", response_model=CalculationResult)
def calculate_endpoint(request: CalculationRequest):
    """Oblicza wycenę na podstawie konfiguracji piłkochwytu."""
    try:
        return calculate(request)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/generate-offer")
def generate_offer(request: OfferRequest):
    """Generuje ofertę PDF i zapisuje ją w bazie."""
    try:
        # 1. Oblicz
        result = calculate(request.calculation)

        # 2. Numer oferty
        offer_number = get_next_offer_number()

        # 3. Generuj PDF
        pdf_path = str(PDF_DIR / f"Oferta_{offer_number}.pdf")
        generate_pdf(offer_number, request.customer, result, pdf_path, request.calculation)

        # 4. Zapisz do bazy
        save_offer(
            offer_number=offer_number,
            customer_name=request.customer.name,
            customer_email=request.customer.email,
            customer_phone=request.customer.phone or "",
            customer_address=request.customer.address or "",
            total_netto=result.total_netto,
            total_brutto=result.total_brutto,
            shape=request.calculation.shape.value,
            quote_type=request.calculation.quote_type.value,
            pdf_path=pdf_path,
        )

        return {
            "offer_number": offer_number,
            "pdf_url": f"/api/offers/{offer_number}/pdf",
            "total_brutto": result.total_brutto,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/offers/{offer_number}/pdf")
def download_pdf(offer_number: str):
    """Pobierz PDF oferty."""
    pdf_path = PDF_DIR / f"Oferta_{offer_number}.pdf"
    if not pdf_path.exists():
        raise HTTPException(status_code=404, detail="Oferta nie znaleziona")
    return FileResponse(
        path=str(pdf_path),
        media_type="application/pdf",
        filename=f"Oferta_{offer_number}.pdf",
    )


@app.get("/health")
def health():
    return {"status": "ok"}
