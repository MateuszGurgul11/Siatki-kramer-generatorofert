import os
import secrets
import sqlite3
from datetime import datetime

DATABASE_PATH = os.getenv("DATABASE_PATH", "./offers.db")


def get_connection():
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS offers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            offer_number TEXT UNIQUE NOT NULL,
            customer_name TEXT NOT NULL,
            customer_email TEXT NOT NULL,
            customer_phone TEXT,
            customer_address TEXT,
            total_netto REAL NOT NULL,
            total_brutto REAL NOT NULL,
            shape TEXT NOT NULL,
            quote_type TEXT NOT NULL,
            created_at TEXT NOT NULL,
            pdf_path TEXT
        )
    """)
    conn.commit()
    conn.close()


def get_next_offer_number() -> str:
    """Generuje unikalny numer oferty KR-YYYY-NNNNN (losowy 5-cyfrowy sufiks 10000–99999)."""
    year = datetime.now().year
    prefix = f"KR-{year}-"
    conn = get_connection()
    cursor = conn.cursor()
    try:
        for _ in range(100):
            suffix = secrets.randbelow(90000) + 10000
            candidate = f"{prefix}{suffix:05d}"
            cursor.execute(
                "SELECT 1 FROM offers WHERE offer_number = ? LIMIT 1",
                (candidate,),
            )
            if cursor.fetchone() is None:
                return candidate
        raise RuntimeError("Nie udało się wygenerować unikalnego numeru oferty po 100 próbach.")
    finally:
        conn.close()


def save_offer(
    offer_number: str,
    customer_name: str,
    customer_email: str,
    customer_phone: str,
    customer_address: str,
    total_netto: float,
    total_brutto: float,
    shape: str,
    quote_type: str,
    pdf_path: str = None,
):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO offers (
            offer_number, customer_name, customer_email, customer_phone,
            customer_address, total_netto, total_brutto, shape, quote_type,
            created_at, pdf_path
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        offer_number, customer_name, customer_email, customer_phone,
        customer_address, total_netto, total_brutto, shape, quote_type,
        datetime.now().isoformat(), pdf_path
    ))
    conn.commit()
    conn.close()
