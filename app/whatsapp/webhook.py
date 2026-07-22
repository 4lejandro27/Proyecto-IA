"""Webhook para recibir mensajes de WhatsApp."""
from fastapi import APIRouter, Request, Response
from app.config import settings
from app.ai.classifier import classify_intent, generate_response
from app.flows.service_flow import ServiceFlowManager
from app.database.sheets import save_lead
from app.notifications.notifier import notify_business
import json

router = APIRouter(prefix="/webhook", tags=["whatsapp"])

# Manager de flujos (en memoria, en producción usar Redis)
flow_managers = {}

@router.get("")
async def verify_webhook(
    hub_mode: str = None,
    hub_verify_token: str = None,
    hub_challenge: str = None
):
    """Verificación del webhook por Meta."""
    if hub_mode == "subscribe" and hub_verify_token == settings.whatsapp_verify_token:
        return Response(content=hub_challenge, media_type="text/plain")
    return Response(status_code=403)

@router.post("")
async def receive_message(request: Request):
    """Recibe mensajes entrantes de WhatsApp."""
    body = await request.json()

    try:
        entry = body.get("entry", [{}])[0]
        changes = entry.get("changes", [{}])[0]
        value = changes.get("value", {})

        if "messages" not in value:
            return {"status": "ok"}

        message = value["messages"][0]
        from_number = message.get("from")

        # Extraer texto del mensaje
        text = ""
        if message.get("type") == "text":
            text = message["text"]["body"]
        elif message.get("type") == "image":
            text = "[IMAGEN_RECIBIDA]"
        elif message.get("type") == "document":
            text = "[DOCUMENTO_RECIBIDO]"
        else:
            text = "[MENSAJE_NO_TEXTO]"

        # Obtener o crear manager de flujo para este número
        if from_number not in flow_managers:
            flow_managers[from_number] = ServiceFlowManager(from_number)

        manager = flow_managers[from_number]

        # Procesar el mensaje
        response_text, is_complete, lead_data = await manager.process_message(text)

        # Enviar respuesta
        from app.whatsapp.sender import send_whatsapp_message
        await send_whatsapp_message(from_number, response_text)

        # Si el flujo está completo, guardar y notificar
        if is_complete and lead_data:
            # Guardar en Google Sheets
            await save_lead(lead_data)

            # Notificar al negocio
            await notify_business(lead_data)

            # Limpiar flujo
            del flow_managers[from_number]

        return {"status": "processed"}

    except Exception as e:
        print(f"Error procesando mensaje: {e}")
        return {"status": "error", "detail": str(e)}
