"""Clasificacion de intenciones y generacion de respuestas con OpenAI."""
import json
from openai import AsyncOpenAI
from app.config import settings

client = AsyncOpenAI(api_key=settings.openai_api_key)

SYSTEM_PROMPT_CLASSIFY = """Eres un asistente inteligente para una empresa de servicios (plomeria, electricidad, aire acondicionado, cerrajeria, limpieza, mantenimiento, reparaciones).

Tu trabajo es analizar el mensaje del cliente y clasificarlo en formato JSON.

Responde UNICAMENTE con un JSON valido en este formato:
{
    "intencion": "nuevo_servicio|consulta|urgencia|cotizacion|seguimiento|saludo|otro",
    "tipo_servicio": "plomeria|electricidad|aire_acondicionado|cerrajeria|limpieza|mantenimiento|fumigacion|reparacion|desconocido",
    "urgencia": "alta|media|baja",
    "palabras_clave": ["tubo", "fuga", "luz", "corto", etc],
    "resumen": "breve descripcion de lo que necesita",
    "preguntas_faltantes": ["direccion", "horario", "nombre", etc]
}

Reglas:
- Si dice "fuga", "inundacion", "no sale agua", "tuberia rota" -> tipo_servicio: plomeria, urgencia: alta
- Si dice "se fue la luz", "corto", "chispas" -> tipo_servicio: electricidad, urgencia: alta
- Si dice "no enfria", "calor", "aire" -> tipo_servicio: aire_acondicionado
- Si dice "llave", "cerradura", "encerrado" -> tipo_servicio: cerrajeria, urgencia: alta
- Si dice "sucio", "limpiar", "mantenimiento" -> tipo_servicio: limpieza o mantenimiento
- Si solo dice "hola", "buenas" -> intencion: saludo
"""

SYSTEM_PROMPT_RESPONSE = """Eres el asistente virtual de {business_name}, una empresa de servicios profesionales.

Tu personalidad: amable, profesional, eficiente, paciente. Hablas como un recepcionista experimentado.

Reglas importantes:
1. SIEMPRE responde en espanol
2. Se conciso pero completo (maximo 3-4 oraciones por mensaje)
3. Si falta informacion, pregunta UNA COSA A LA VEZ
4. Nunca inventes precios exactos, solo rangos aproximados
5. Si es urgencia, muestra empatia y prioridad
6. Cuando tengas toda la info, confirma con un resumen claro

Contexto actual del cliente:
{context}

Datos recolectados hasta ahora:
{collected_data}

Proxima pregunta recomendada: {next_question}

Responde al mensaje del cliente de forma natural y profesional.
"""

async def classify_intent(message: str) -> dict:
    """Clasifica la intencion del mensaje del cliente."""
    print(f"[CLASSIFIER] Clasificando: {message[:50]}...")
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
        print(f"[CLASSIFIER] Respuesta cruda: {content[:200]}...")

        # Limpiar posibles markdown
        if content.startswith("```json"):
            content = content[7:]
        if content.endswith("```"):
            content = content[:-3]
        content = content.strip()

        result = json.loads(content)
        print(f"[CLASSIFIER] Resultado: {result}")
        return result
    except Exception as e:
        print(f"[CLASSIFIER] ERROR: {e}")
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
    print(f"[CLASSIFIER] Generando respuesta para: {message[:50]}...")
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

        result = response.choices[0].message.content.strip()
        print(f"[CLASSIFIER] Respuesta generada: {result[:100]}...")
        return result
    except Exception as e:
        print(f"[CLASSIFIER] ERROR generando respuesta: {e}")
        # Fallback: devolver la pregunta directa
        return next_question
