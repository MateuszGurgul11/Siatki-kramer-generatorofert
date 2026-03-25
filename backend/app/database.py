import sqlite3
import os
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
    """Generuje kolejny numer oferty w formacie KR-YYYY-NNNNN."""
    conn = get_connection()
    cursor = conn.cursor()
    year = datetime.now().year
    cursor.execute(
        "SELECT COUNT(*) as cnt FROM offers WHERE offer_number LIKE ?",
        (f"KR-{year}-%",)
    )
    row = cursor.fetchone()
    conn.close()
    count = row["cnt"] + 1
    return f"KR-{year}-{count:05d}"


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
