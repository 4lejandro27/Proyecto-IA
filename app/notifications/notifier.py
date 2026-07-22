"""Sistema de notificaciones al negocio (Email + Telegram)."""
import httpx
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from app.config import settings

async def notify_business(lead_data: dict):
    """Envia notificacion al negocio por email y Telegram."""
    email_task = send_email_notification(lead_data)
    telegram_task = send_telegram_notification(lead_data)

    try:
        await email_task
    except Exception as e:
        print(f"Error enviando email: {e}")

    try:
        await telegram_task
    except Exception as e:
        print(f"Error enviando Telegram: {e}")

async def send_email_notification(lead_data: dict):
    """Envia notificacion por email."""
    if not settings.email_to or not settings.smtp_pass or settings.smtp_pass == "placeholder_resend_key":
        print("Email no configurado, saltando...")
        return

    subject = f"Nuevo Lead: {lead_data.get('tipo_servicio', 'Servicio').upper()} - {lead_data.get('urgencia', 'media').upper()}"

    body = f"""
    <html>
    <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
        <h2 style="color: #d9534f;">Nuevo Lead Recibido</h2>

        <table style="border-collapse: collapse; width: 100%; max-width: 600px;">
            <tr style="background: #f9f9f9;">
                <td style="padding: 10px; border: 1px solid #ddd; font-weight: bold;">Nombre:</td>
                <td style="padding: 10px; border: 1px solid #ddd;">{lead_data.get('nombre', 'N/A')}</td>
            </tr>
            <tr>
                <td style="padding: 10px; border: 1px solid #ddd; font-weight: bold;">Telefono:</td>
                <td style="padding: 10px; border: 1px solid #ddd;">{lead_data.get('telefono', 'N/A')}</td>
            </tr>
            <tr style="background: #f9f9f9;">
                <td style="padding: 10px; border: 1px solid #ddd; font-weight: bold;">Email:</td>
                <td style="padding: 10px; border: 1px solid #ddd;">{lead_data.get('email', 'N/A')}</td>
            </tr>
            <tr>
                <td style="padding: 10px; border: 1px solid #ddd; font-weight: bold;">Direccion:</td>
                <td style="padding: 10px; border: 1px solid #ddd;">{lead_data.get('direccion', 'N/A')}, {lead_data.get('ciudad', 'N/A')}</td>
            </tr>
            <tr style="background: #f9f9f9;">
                <td style="padding: 10px; border: 1px solid #ddd; font-weight: bold;">Servicio:</td>
                <td style="padding: 10px; border: 1px solid #ddd;">{lead_data.get('tipo_servicio', 'N/A')}</td>
            </tr>
            <tr>
                <td style="padding: 10px; border: 1px solid #ddd; font-weight: bold;">Problema:</td>
                <td style="padding: 10px; border: 1px solid #ddd;">{lead_data.get('problema', 'N/A')}</td>
            </tr>
            <tr style="background: #f9f9f9;">
                <td style="padding: 10px; border: 1px solid #ddd; font-weight: bold;">Urgencia:</td>
                <td style="padding: 10px; border: 1px solid #ddd; color: {'#d9534f' if lead_data.get('urgencia') == 'alta' else '#f0ad4e' if lead_data.get('urgencia') == 'media' else '#5cb85c'};">
                    {lead_data.get('urgencia', 'N/A').upper()}
                </td>
            </tr>
            <tr>
                <td style="padding: 10px; border: 1px solid #ddd; font-weight: bold;">Horario:</td>
                <td style="padding: 10px; border: 1px solid #ddd;">{lead_data.get('horario', 'N/A')}</td>
            </tr>
            <tr style="background: #f9f9f9;">
                <td style="padding: 10px; border: 1px solid #ddd; font-weight: bold;">Precio Estimado:</td>
                <td style="padding: 10px; border: 1px solid #ddd; font-weight: bold; color: #5cb85c;">{lead_data.get('precio_estimado', 'N/A')}</td>
            </tr>
            <tr>
                <td style="padding: 10px; border: 1px solid #ddd; font-weight: bold;">Fecha:</td>
                <td style="padding: 10px; border: 1px solid #ddd;">{lead_data.get('fecha_hora', 'N/A')}</td>
            </tr>
        </table>

        <p style="margin-top: 20px; color: #666; font-size: 12px;">
            Este lead fue generado automaticamente por ServiceBot.
        </p>
    </body>
    </html>
    """

    msg = MIMEMultipart()
    msg["From"] = settings.email_from
    msg["To"] = settings.email_to
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "html"))

    with smtplib.SMTP(settings.smtp_host, settings.smtp_port) as server:
        server.starttls()
        server.login(settings.smtp_user, settings.smtp_pass)
        server.send_message(msg)

    print(f"Email enviado a {settings.email_to}")

async def send_telegram_notification(lead_data: dict):
    """Envia notificacion por Telegram."""
    if not settings.telegram_bot_token or not settings.telegram_chat_id:
        print("Telegram no configurado, saltando...")
        return

    emoji_urgencia = {
        "alta": "ALTA",
        "media": "MEDIA",
        "baja": "BAJA"
    }

    message = f"""
NUEVO LEAD - {lead_data.get('urgencia', 'MEDIA').upper()}

Nombre: {lead_data.get('nombre', 'N/A')}
Telefono: {lead_data.get('telefono', 'N/A')}
Email: {lead_data.get('email', 'N/A')}
Direccion: {lead_data.get('direccion', 'N/A')}, {lead_data.get('ciudad', 'N/A')}

Servicio: {lead_data.get('tipo_servicio', 'N/A')}
Problema: {lead_data.get('problema', 'N/A')}
Horario: {lead_data.get('horario', 'N/A')}
Precio Estimado: {lead_data.get('precio_estimado', 'N/A')}

Fecha: {lead_data.get('fecha_hora', 'N/A')}
    """

    url = f"https://api.telegram.org/bot{settings.telegram_bot_token}/sendMessage"

    async with httpx.AsyncClient() as client:
        response = await client.post(url, json={
            "chat_id": settings.telegram_chat_id,
            "text": message,
            "parse_mode": "Markdown"
        })

        if response.status_code == 200:
            print(f"Telegram enviado al chat {settings.telegram_chat_id}")
        else:
            print(f"Error Telegram: {response.text}")
