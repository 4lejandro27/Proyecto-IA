"""Webhook para recibir mensajes de WhatsApp."""
from fastapi import APIRouter, Request, Response
from app.config import settings
from app.ai.classifier import classify_intent, generate_response
from app.flows.service_flow import ServiceFlowManager
from app.database.sheets import save_lead
from app.notifications.notifier import notify_business
import json
import traceback

router = APIRouter(prefix="/webhook", tags=["whatsapp"])

# Manager de flujos (en memoria, en produccion usar Redis)
flow_managers = {}

@router.get("")
async def verify_webhook(
    hub_mode: str = None,
    hub_verify_token: str = None,
    hub_challenge: str = None
):
    """Verificacion del webhook por Meta."""
    print(f"[WEBHOOK GET] mode={hub_mode}, token={hub_verify_token}")
    if hub_mode == "subscribe" and hub_verify_token == settings.whatsapp_verify_token:
        print("[WEBHOOK GET] Verificacion exitosa")
        return Response(content=hub_challenge, media_type="text/plain")
    print(f"[WEBHOOK GET] Verificacion fallida. Esperado: {settings.whatsapp_verify_token}, Recibido: {hub_verify_token}")
    return Response(status_code=403)

@router.post("")
async def receive_message(request: Request):
    """Recibe mensajes entrantes de WhatsApp."""
    try:
        body = await request.json()
        print(f"[WEBHOOK POST] Body recibido: {json.dumps(body, indent=2)[:500]}")
    except Exception as e:
        print(f"[WEBHOOK POST] Error parseando JSON: {e}")
        return {"status": "error", "detail": "Invalid JSON"}

    try:
        entry = body.get("entry", [{}])[0]
        changes = entry.get("changes", [{}])[0]
        value = changes.get("value", {})

        if "messages" not in value:
            print("[WEBHOOK POST] No hay mensajes en el payload")
            return {"status": "ok"}

        message = value["messages"][0]
        from_number = message.get("from")
        print(f"[WEBHOOK POST] Mensaje de: {from_number}")

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

        print(f"[WEBHOOK POST] Texto recibido: {text}")

        # Obtener o crear manager de flujo para este numero
        if from_number not in flow_managers:
            print(f"[WEBHOOK POST] Creando nuevo flujo para {from_number}")
            flow_managers[from_number] = ServiceFlowManager(from_number)

        manager = flow_managers[from_number]

        # Procesar el mensaje
        print("[WEBHOOK POST] Procesando con IA...")
        response_text, is_complete, lead_data = await manager.process_message(text)
        print(f"[WEBHOOK POST] Respuesta IA: {response_text[:100]}...")

        # Enviar respuesta
        from app.whatsapp.sender import send_whatsapp_message
        print(f"[WEBHOOK POST] Enviando respuesta a {from_number}...")
        result = await send_whatsapp_message(from_number, response_text)
        print(f"[WEBHOOK POST] Resultado envio: {result}")

        # Si el flujo esta completo, guardar y notificar
        if is_complete and lead_data:
            print(f"[WEBHOOK POST] Flujo completo, guardando lead: {lead_data}")
            try:
                await save_lead(lead_data)
            except Exception as e:
                print(f"[WEBHOOK POST] Error guardando lead: {e}")

            try:
                await notify_business(lead_data)
            except Exception as e:
                print(f"[WEBHOOK POST] Error notificando: {e}")

            # Limpiar flujo
            del flow_managers[from_number]

        return {"status": "processed"}

    except Exception as e:
        print(f"[WEBHOOK POST] ERROR GENERAL: {e}")
        traceback.print_exc()
        return {"status": "error", "detail": str(e)}
