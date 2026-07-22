"""Envio de mensajes por WhatsApp Cloud API."""
import httpx
from app.config import settings

WHATSAPP_API_URL = "https://graph.facebook.com/v20.0"

async def send_whatsapp_message(to_phone: str, message: str, message_type: str = "text"):
    """Envia un mensaje de WhatsApp a un numero de telefono."""
    url = f"{WHATSAPP_API_URL}/{settings.whatsapp_phone_number_id}/messages"

    headers = {
        "Authorization": f"Bearer {settings.whatsapp_token}",
        "Content-Type": "application/json"
    }

    # Formatear numero (quitar + si existe)
    to_phone = to_phone.replace("+", "").replace(" ", "").replace("-", "")

    payload = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": to_phone,
        "type": "text",
        "text": {"body": message}
    }

    print(f"[SENDER] Enviando a {to_phone}")
    print(f"[SENDER] URL: {url}")
    print(f"[SENDER] Token (primeros 20 chars): {settings.whatsapp_token[:20]}...")
    print(f"[SENDER] Phone ID: {settings.whatsapp_phone_number_id}")

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(url, headers=headers, json=payload)
            result = response.json()
            print(f"[SENDER] Status: {response.status_code}")
            print(f"[SENDER] Respuesta Meta: {result}")
            return result
    except Exception as e:
        print(f"[SENDER] ERROR enviando mensaje: {e}")
        import traceback
        traceback.print_exc()
        return {"error": str(e)}

async def send_whatsapp_template(to_phone: str, template_name: str, language_code: str = "es"):
    """Envia una plantilla aprobada de WhatsApp."""
    url = f"{WHATSAPP_API_URL}/{settings.whatsapp_phone_number_id}/messages"

    headers = {
        "Authorization": f"Bearer {settings.whatsapp_token}",
        "Content-Type": "application/json"
    }

    to_phone = to_phone.replace("+", "").replace(" ", "").replace("-", "")

    payload = {
        "messaging_product": "whatsapp",
        "to": to_phone,
        "type": "template",
        "template": {
            "name": template_name,
            "language": {"code": language_code}
        }
    }

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(url, headers=headers, json=payload)
            return response.json()
    except Exception as e:
        print(f"[SENDER] ERROR enviando template: {e}")
        return {"error": str(e)}
