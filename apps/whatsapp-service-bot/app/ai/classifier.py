"""Clasificación de intenciones y generación de respuestas con OpenAI."""
import json
from openai import AsyncOpenAI
from app.config import settings

client = AsyncOpenAI(api_key=settings.openai_api_key)

SYSTEM_PROMPT_CLASSIFY = """Eres un asistente inteligente para una empresa de servicios (plomería, electricidad, aire acondicionado, cerrajería, limpieza, mantenimiento, reparaciones).

Tu trabajo es analizar el mensaje del cliente y clasificarlo en formato JSON.

Responde ÚNICAMENTE con un JSON válido en este formato:
{
    "intencion": "nuevo_servicio|consulta|urgencia|cotizacion|seguimiento|saludo|otro",
    "tipo_servicio": "plomeria|electricidad|aire_acondicionado|cerrajeria|limpieza|mantenimiento|fumigacion|reparacion|desconocido",
    "urgencia": "alta|media|baja",
    "palabras_clave": ["tubo", "fuga", "luz", "corto", etc],
    "resumen": "breve descripción de lo que necesita",
    "preguntas_faltantes": ["direccion", "horario", "nombre", etc]
}

Reglas:
- Si dice "fuga", "inundación", "no sale agua", "tubería rota" → tipo_servicio: plomeria, urgencia: alta
- Si dice "se fue la luz", "corto", "chispas" → tipo_servicio: electricidad, urgencia: alta
- Si dice "no enfría", "calor", "aire" → tipo_servicio: aire_acondicionado
- Si dice "llave", "cerradura", "encerrado" → tipo_servicio: cerrajeria, urgencia: alta
- Si dice "sucio", "limpiar", "mantenimiento" → tipo_servicio: limpieza o mantenimiento
- Si solo dice "hola", "buenas" → intencion: saludo
"""

SYSTEM_PROMPT_RESPONSE = """Eres el asistente virtual de {business_name}, una empresa de servicios profesionales.

Tu personalidad: amable, profesional, eficiente, paciente. Hablas como un recepcionista experimentado.

Reglas importantes:
1. SIEMPRE responde en español
2. Sé conciso pero completo (máximo 3-4 oraciones por mensaje)
3. Si falta información, pregunta UNA COSA A LA VEZ
4. Nunca inventes precios exactos, solo rangos aproximados
5. Si es urgencia, muestra empatía y prioridad
6. Cuando tengas toda la info, confirma con un resumen claro

Contexto actual del cliente:
{context}

Datos recolectados hasta ahora:
{collected_data}

Próxima pregunta recomendada: {next_question}

Responde al mensaje del cliente de forma natural y profesional.
"""

async def classify_intent(message: str) -> dict:
    """Clasifica la intención del mensaje del cliente."""
    try:
        response = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT_CLASSIFY},
                {"role": "user", "content": message}
            ],
            temperature=0.3,
            max_tokens=300
        )

        content = response.choices[0].message.content.strip()

        # Limpiar posibles markdown
        if content.startswith("```json"):
            content = content[7:]
        if content.endswith("```"):
            content = content[:-3]
        content = content.strip()

        return json.loads(content)
    except Exception as e:
        print(f"Error clasificando: {e}")
        return {
            "intencion": "nuevo_servicio",
            "tipo_servicio": "desconocido",
            "urgencia": "media",
            "palabras_clave": [],
            "resumen": message,
            "preguntas_faltantes": ["tipo_servicio", "direccion", "horario", "nombre"]
        }

async def generate_response(
    message: str,
    context: dict,
    collected_data: dict,
    next_question: str,
    business_name: str = "Servicios Express"
) -> str:
    """Genera una respuesta natural con IA."""
    try:
        prompt = SYSTEM_PROMPT_RESPONSE.format(
            business_name=business_name,
            context=json.dumps(context, ensure_ascii=False),
            collected_data=json.dumps(collected_data, ensure_ascii=False),
            next_question=next_question
        )

        response = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": message}
            ],
            temperature=0.7,
            max_tokens=500
        )

        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"Error generando respuesta: {e}")
        return "Disculpe, hubo un error técnico. Por favor, escriba su solicitud nuevamente."
