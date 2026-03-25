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
from .email_service import send_offer_email
from .nets import get_all_nets

app = FastAPI(
    title="Siatki Kramer — Generator Ofert API",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

PDF_DIR = Path("./pdfs")
PDF_DIR.mkdir(exist_ok=True)


@app.on_event("startup")
def startup():
    init_db()


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
    """Generuje ofertę PDF, zapisuje do bazy i wysyła e-mail."""
    try:
        # 1. Oblicz
        result = calculate(request.calculation)

        # 2. Numer oferty
        offer_number = get_next_offer_number()

        # 3. Generuj PDF
        pdf_path = str(PDF_DIR / f"Oferta_{offer_number}.pdf")
        generate_pdf(offer_number, request.customer, result, pdf_path)

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

        # 5. Wyślij e-mail
        email_sent = send_offer_email(
            recipient_email=request.customer.email,
            recipient_name=request.customer.name,
            offer_number=offer_number,
            total_brutto=result.total_brutto,
            pdf_path=pdf_path,
        )

        return {
            "offer_number": offer_number,
            "pdf_url": f"/api/offers/{offer_number}/pdf",
            "email_sent": email_sent,
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
