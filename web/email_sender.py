from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import smtplib
from .config import SMTP_USER, SMTP_PASS, SMTP_HOST, SMTP_PORT

def enviar_correo_otp(correo_destinatario: str, usuario: str, otp: str) -> tuple[bool, str]:
    """
    Envía el código OTP al correo del usuario.
    Devuelve (True, "") o (False, mensaje_error).
    """
    if not SMTP_USER or not SMTP_PASS:
        return False, (
            "El servidor de correo no está configurado. "
            "Define QPROOF_SMTP_USER y QPROOF_SMTP_PASS."
        )

    asunto = "Q-Proof Portal — Código de recuperación de contraseña"
    cuerpo_html = f"""
    <div style="font-family:Inter,sans-serif;background:#0a1628;color:#e2e8f0;
                padding:2rem;border-radius:12px;max-width:480px;margin:auto;">
        <h2 style="color:#5eead4;margin-top:0;">🛡️ Q-Proof Portal</h2>
        <p>Hola <strong>{usuario}</strong>,</p>
        <p>Has solicitado restablecer tu contraseña. Usa el siguiente código:</p>
        <div style="font-size:2.4rem;font-weight:700;letter-spacing:10px;
                    text-align:center;color:#5eead4;padding:1rem 0;">
            {otp}
        </div>
        <p style="font-size:0.85rem;color:#94a3b8;">
            Este código es válido durante <strong>10 minutos</strong>.<br>
            Si no solicitaste este restablecimiento, ignora este correo.
        </p>
        <hr style="border-color:#1e3a6e;margin:1.5rem 0;">
        <p style="font-size:0.75rem;color:#475569;text-align:center;">
            Especificaciones ML-DSA:
            <a href="https://crystals-dilithium.lovable.app/" style="color:#5eead4;">
                crystals-dilithium.lovable.app
            </a>
        </p>
    </div>
    """
    try:
        mensaje = MIMEMultipart("alternative")
        mensaje["Subject"] = asunto
        mensaje["From"]    = SMTP_USER
        mensaje["To"]      = correo_destinatario
        mensaje.attach(MIMEText(cuerpo_html, "html", "utf-8"))

        with smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=10) as servidor:
            servidor.ehlo()
            servidor.starttls()
            servidor.login(SMTP_USER, SMTP_PASS)
            servidor.sendmail(SMTP_USER, [correo_destinatario], mensaje.as_string())
        return True, ""
    except Exception as exc:
        return False, str(exc)
