"""
Email Sender Service for IHSG Terminal Pro.

Mengirim kode verifikasi 6-digit ke email pengguna menggunakan SMTP.
Mendukung Gmail App Password dan SMTP provider lainnya.

Konfigurasi di .env:
    SMTP_HOST=smtp.gmail.com
    SMTP_PORT=587
    SMTP_EMAIL=your-email@gmail.com
    SMTP_PASSWORD=your-gmail-app-password
"""
import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional


def _get_smtp_config() -> dict:
    """Reads SMTP configuration from environment / settings."""
    try:
        from app.core.config import settings
        return {
            "host": getattr(settings, "SMTP_HOST", "") or os.getenv("SMTP_HOST", ""),
            "port": int(getattr(settings, "SMTP_PORT", 0) or os.getenv("SMTP_PORT", "587")),
            "email": getattr(settings, "SMTP_EMAIL", "") or os.getenv("SMTP_EMAIL", ""),
            "password": getattr(settings, "SMTP_PASSWORD", "") or os.getenv("SMTP_PASSWORD", ""),
        }
    except Exception:
        return {
            "host": os.getenv("SMTP_HOST", ""),
            "port": int(os.getenv("SMTP_PORT", "587")),
            "email": os.getenv("SMTP_EMAIL", ""),
            "password": os.getenv("SMTP_PASSWORD", ""),
        }


def is_smtp_configured() -> bool:
    """Returns True if SMTP credentials are fully configured."""
    cfg = _get_smtp_config()
    return bool(cfg["host"] and cfg["email"] and cfg["password"])


def send_verification_email(to_email: str, code: str) -> bool:
    """
    Sends a 6-digit verification code to the given email address via SMTP.

    Returns True if sent successfully, False otherwise.
    """
    cfg = _get_smtp_config()

    if not (cfg["host"] and cfg["email"] and cfg["password"]):
        print(f"[EmailSender] SMTP belum dikonfigurasi. Kode verifikasi untuk {to_email}: {code}")
        return False

    subject = "🔐 Kode Verifikasi Reset Password — IHSG Terminal Pro"

    html_body = f"""
    <div style="font-family: 'Segoe UI', Arial, sans-serif; max-width: 480px; margin: 0 auto; background: #0b1329; border-radius: 16px; overflow: hidden; border: 1px solid #1e293b;">
        <div style="height: 4px; background: linear-gradient(to right, #3b82f6, #ef4444, #f59e0b);"></div>
        <div style="padding: 32px 24px;">
            <h2 style="color: #f1f5f9; margin: 0 0 8px; font-size: 20px;">IHSG Terminal Pro</h2>
            <p style="color: #94a3b8; margin: 0 0 24px; font-size: 13px;">Smart Stock Recommendation & Decision Support System</p>

            <p style="color: #cbd5e1; font-size: 14px; line-height: 1.6;">
                Anda telah meminta reset password untuk akun:
                <br><strong style="color: #22d3ee;">{to_email}</strong>
            </p>

            <div style="background: #111827; border: 1px solid #1e293b; border-radius: 12px; padding: 20px; text-align: center; margin: 24px 0;">
                <p style="color: #94a3b8; font-size: 12px; margin: 0 0 8px; text-transform: uppercase; letter-spacing: 1px;">Kode Verifikasi Anda</p>
                <p style="color: #22d3ee; font-size: 32px; font-weight: 900; letter-spacing: 8px; margin: 0; font-family: 'Courier New', monospace;">{code}</p>
            </div>

            <p style="color: #94a3b8; font-size: 12px; line-height: 1.6;">
                Kode ini berlaku selama <strong>15 menit</strong>. Jangan bagikan kode ini kepada siapapun.
            </p>

            <hr style="border: none; border-top: 1px solid #1e293b; margin: 24px 0;">

            <p style="color: #64748b; font-size: 11px; line-height: 1.5;">
                Jika Anda tidak meminta reset password, abaikan email ini. Akun Anda tetap aman.
            </p>
        </div>
    </div>
    """

    text_body = f"""
IHSG Terminal Pro — Kode Verifikasi Reset Password

Anda telah meminta reset password untuk akun: {to_email}

Kode Verifikasi Anda: {code}

Kode ini berlaku selama 15 menit.
Jangan bagikan kode ini kepada siapapun.

Jika Anda tidak meminta reset password, abaikan email ini.
    """

    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = f"IHSG Terminal Pro <{cfg['email']}>"
        msg["To"] = to_email

        msg.attach(MIMEText(text_body, "plain", "utf-8"))
        msg.attach(MIMEText(html_body, "html", "utf-8"))

        with smtplib.SMTP(cfg["host"], cfg["port"], timeout=10) as server:
            server.ehlo()
            server.starttls()
            server.ehlo()
            server.login(cfg["email"], cfg["password"])
            server.sendmail(cfg["email"], to_email, msg.as_string())

        print(f"[EmailSender] ✅ Kode verifikasi berhasil dikirim ke {to_email}")
        return True

    except smtplib.SMTPAuthenticationError as e:
        print(f"[EmailSender] ❌ Gagal autentikasi SMTP (periksa App Password): {e}")
        return False
    except smtplib.SMTPRecipientsRefused as e:
        print(f"[EmailSender] ❌ Email penerima ditolak: {e}")
        return False
    except Exception as e:
        print(f"[EmailSender] ❌ Gagal mengirim email ke {to_email}: {e}")
        return False
