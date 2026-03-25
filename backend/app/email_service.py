import smtplib
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER", "")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
SENDER_NAME = os.getenv("SENDER_NAME", "Siatki Kramer")
ORDER_LINK = os.getenv("ORDER_LINK", "https://sklep.siatki-kramer.pl/zamowienie/")
COMPANY_WEBSITE = os.getenv("COMPANY_WEBSITE", "https://sklep.siatki-kramer.pl")


def send_offer_email(
    recipient_email: str,
    recipient_name: str,
    offer_number: str,
    total_brutto: float,
    pdf_path: str,
) -> bool:
    """Wysyła e-mail z ofertą PDF do klienta. Zwraca True w przypadku sukcesu."""
    if not SMTP_USER or not SMTP_PASSWORD:
        print("SMTP nie skonfigurowany — pominięto wysyłkę e-mail.")
        return False

    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = f"Oferta nr {offer_number} — Siatki Kramer"
        msg["From"] = f"{SENDER_NAME} <{SMTP_USER}>"
        msg["To"] = recipient_email

        order_link = f"{ORDER_LINK}?oferta={offer_number}"

        html_body = f"""
        <!DOCTYPE html>
        <html lang="pl">
        <head><meta charset="UTF-8"></head>
        <body style="font-family: Arial, sans-serif; color: #333; max-width: 600px; margin: 0 auto; padding: 20px;">
            <div style="background: #1a5c2a; padding: 20px; border-radius: 8px 8px 0 0;">
                <h1 style="color: white; margin: 0; font-size: 22px;">Siatki Kramer</h1>
                <p style="color: #a5d6a7; margin: 4px 0 0 0; font-size: 13px;">Generator ofert piłkochwytów</p>
            </div>
            <div style="background: #f9f9f9; border: 1px solid #e0e0e0; padding: 24px; border-radius: 0 0 8px 8px;">
                <p>Szanowny/a Panie/Pani <b>{recipient_name}</b>,</p>
                <p>Dziękujemy za skorzystanie z naszego generatora ofert. W załączeniu przesyłamy wycenę materiałów do budowy piłkochwytu.</p>

                <div style="background: #e8f5e9; border-left: 4px solid #1a5c2a; padding: 16px; margin: 20px 0; border-radius: 0 8px 8px 0;">
                    <p style="margin: 0; font-size: 13px; color: #555;">Numer oferty</p>
                    <p style="margin: 4px 0; font-size: 20px; font-weight: bold; color: #1a5c2a;">{offer_number}</p>
                    <p style="margin: 8px 0 0 0; font-size: 13px; color: #555;">Wartość brutto: <b style="font-size: 16px;">{total_brutto:.2f} zł</b></p>
                </div>

                <p>Aby złożyć zamówienie na podstawie tej oferty, kliknij poniższy przycisk:</p>

                <div style="text-align: center; margin: 24px 0;">
                    <a href="{order_link}"
                       style="background: #1a5c2a; color: white; padding: 14px 32px; text-decoration: none; border-radius: 6px; font-size: 16px; font-weight: bold; display: inline-block;">
                        Złóż zamówienie →
                    </a>
                </div>

                <p style="font-size: 12px; color: #888; border-top: 1px solid #e0e0e0; padding-top: 16px; margin-top: 24px;">
                    Oferta jest orientacyjna i nie stanowi oferty w rozumieniu przepisów prawa.<br>
                    Ceny netto, VAT 23%. Wycena nie obejmuje kosztów montażu.<br><br>
                    <b>Siatki Kramer</b> | <a href="{COMPANY_WEBSITE}" style="color: #1a5c2a;">{COMPANY_WEBSITE}</a>
                </p>
            </div>
        </body>
        </html>
        """

        msg.attach(MIMEText(html_body, "html", "utf-8"))

        # Załącz PDF
        if pdf_path and os.path.exists(pdf_path):
            with open(pdf_path, "rb") as f:
                part = MIMEBase("application", "octet-stream")
                part.set_payload(f.read())
                encoders.encode_base64(part)
                part.add_header(
                    "Content-Disposition",
                    f"attachment; filename=Oferta_{offer_number}.pdf"
                )
                msg.attach(part)

        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USER, SMTP_PASSWORD)
            server.sendmail(SMTP_USER, recipient_email, msg.as_string())

        return True
    except Exception as e:
        print(f"Błąd wysyłki e-mail: {e}")
        return False
