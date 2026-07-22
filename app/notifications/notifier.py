"""Sistema de notificaciones al negocio (Email + Telegram)."""
import httpx
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from app.config import settings
import asyncio

async def notify_business(lead_data: dict):
    """Envia notificacion al negocio por email y Telegram."""
    print(f"[NOTIFIER] Notificando lead: {lead_data.get('nombre', 'N/A')}")

    # Ejecutar ambas notificaciones en paralelo
    tasks = []

    if settings.email_to and settings.smtp_pass and settings.smtp_pass != "placeholder_resend_key":
        tasks.append(send_email_notification(lead_data))
    else:
        print("[NOTIFIER] Email no configurado, saltando...")

    if settings.telegram_bot_token and settings.telegram_chat_id:
        tasks.append(send_telegram_notification(lead_data))
    else:
        print("[NOTIFIER] Telegram no configurado, saltando...")

    if tasks:
        results = await asyncio.gather(*tasks, return_exceptions=True)
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                print(f"[NOTIFIER] Error en notificacion {i}: {result}")
            else:
                print(f"[NOTIFIER] Notificacion {i} enviada OK")
    else:
        print("[NOTIFIER] No hay notificaciones configuradas")

async def send_email_notification(lead_data: dict):
    """Envia notificacion por email."""
    print(f"[EMAIL] Preparando email para {settings.email_to}")

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
                <td style="padding: 10px; border: 1px solid #ddd;">{lead_data.get('urgencia', 'N/A').upper()}</td>
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

    try:
        with smtplib.SMTP(settings.smtp_host, settings.smtp_port) as server:
            server.starttls()
            server.login(settings.smtp_user, settings.smtp_pass)
            server.send_message(msg)
        print(f"[EMAIL] Email enviado a {settings.email_to}")
    except Exception as e:
        print(f"[EMAIL] Error enviando email: {e}")
        raise

async def send_telegram_notification(lead_data: dict):
    """Envia notificacion por Telegram."""
    print(f"[TELEGRAM] Enviando a chat {settings.telegram_chat_id}")

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

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(url, json={
                "chat_id": settings.telegram_chat_id,
                "text": message,
                "parse_mode": "Markdown"
            })

            if response.status_code == 200:
                print(f"[TELEGRAM] Enviado OK al chat {settings.telegram_chat_id}")
            else:
                print(f"[TELEGRAM] Error: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"[TELEGRAM] Error: {e}")
        raise
