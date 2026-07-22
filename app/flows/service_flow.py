"""Gestion del flujo de conversacion para servicios."""
from app.ai.classifier import classify_intent, generate_response
from datetime import datetime

class ServiceFlowManager:
    """Maneja el flujo completo de recoleccion de informacion del cliente."""

    QUESTIONS = [
        {"field": "tipo_servicio", "question": "Que tipo de servicio necesitas? (plomeria, electricidad, aire acondicionado, cerrajeria, limpieza, mantenimiento, etc.)"},
        {"field": "ciudad", "question": "En que ciudad te encuentras?"},
        {"field": "direccion", "question": "Cual es la direccion exacta donde necesitas el servicio?"},
        {"field": "problema", "question": "Cual es el problema o que necesitas que hagamos?"},
        {"field": "urgencia", "question": "Que tan urgente es? (alta: emergencia, media: hoy o manana, baja: esta semana)"},
        {"field": "horario", "question": "En que horario prefieres que visitemos? (manana, tarde, noche, o hora especifica)"},
        {"field": "nombre", "question": "Cual es tu nombre completo?"},
        {"field": "email", "question": "Cual es tu correo electronico? (para enviarte la confirmacion)"},
        {"field": "telefono", "question": "Confirmas que este es tu numero de WhatsApp para contactarte?"},
    ]

    def __init__(self, phone_number: str):
        self.phone_number = phone_number
        self.collected_data = {
            "telefono": phone_number,
            "fecha_hora": datetime.now().isoformat(),
            "estado": "en_proceso",
            "canal": "whatsapp",
            "origen": "organico"
        }
        self.current_question_index = 0
        self.context = {}
        self.conversation_history = []
        self.is_complete = False

    async def process_message(self, message: str):
        """Procesa un mensaje del cliente y retorna respuesta."""
        self.conversation_history.append({"role": "user", "content": message})

        # Primera interaccion o saludo
        if len(self.conversation_history) == 1:
            classification = await classify_intent(message)
            self.context = classification

            # Si es saludo, presentarse
            if classification.get("intencion") == "saludo":
                response = (
                    "Hola! Soy el asistente virtual de Servicios Express.

"
                    "Estoy aqui para ayudarte a agendar tu servicio de forma rapida y sencilla.

"
                    "Que tipo de servicio necesitas hoy?"
                )
                return response, False, None

            # Si ya identifico el servicio en el primer mensaje
            if classification.get("tipo_servicio") != "desconocido":
                self.collected_data["tipo_servicio"] = classification["tipo_servicio"]
                self.collected_data["urgencia"] = classification.get("urgencia", "media")
                self.collected_data["problema"] = classification.get("resumen", message)

                # Saltar a la siguiente pregunta
                self.current_question_index = 1

                response = await generate_response(
                    message,
                    self.context,
                    self.collected_data,
                    self.QUESTIONS[1]["question"]
                )
                return response, False, None

        # Intentar extraer respuesta de la pregunta actual
        current_field = self.QUESTIONS[self.current_question_index]["field"]
        self.collected_data[current_field] = message

        # Avanzar a la siguiente pregunta
        self.current_question_index += 1

        # Verificar si completamos todas las preguntas
        if self.current_question_index >= len(self.QUESTIONS):
            return await self._complete_flow()

        # Generar respuesta con la siguiente pregunta
        next_q = self.QUESTIONS[self.current_question_index]["question"]
        response = await generate_response(
            message,
            self.context,
            self.collected_data,
            next_q
        )

        return response, False, None

    async def _complete_flow(self):
        """Finaliza el flujo y genera resumen."""
        self.is_complete = True
        self.collected_data["estado"] = "pendiente"
        self.collected_data["fecha_completado"] = datetime.now().isoformat()

        # Calcular rango de precio estimado
        precio = self._estimate_price()
        self.collected_data["precio_estimado"] = precio

        # Generar resumen
        resumen = (
            f"Solicitud registrada!

"
            f"Resumen de tu servicio:
"
            f"Nombre: {self.collected_data.get('nombre', 'N/A')}
"
            f"Direccion: {self.collected_data.get('direccion', 'N/A')}, {self.collected_data.get('ciudad', 'N/A')}
"
            f"Servicio: {self.collected_data.get('tipo_servicio', 'N/A')}
"
            f"Problema: {self.collected_data.get('problema', 'N/A')}
"
            f"Horario: {self.collected_data.get('horario', 'N/A')}
"
            f"Urgencia: {self.collected_data.get('urgencia', 'N/A')}
"
            f"Precio estimado: {precio}

"
            f"Confirmacion enviada a: {self.collected_data.get('email', 'N/A')}

"
            f"Un tecnico se pondra en contacto contigo en los proximos 30 minutos.
"
            f"Necesitas algo mas?"
        )

        return resumen, True, self.collected_data

    def _estimate_price(self):
        """Estima un rango de precio segun el servicio."""
        servicio = self.collected_data.get("tipo_servicio", "").lower()
        urgencia = self.collected_data.get("urgencia", "media")

        precios_base = {
            "plomeria": "$50 - $150",
            "electricidad": "$40 - $120",
            "aire_acondicionado": "$60 - $200",
            "cerrajeria": "$30 - $100",
            "limpieza": "$40 - $150",
            "mantenimiento": "$50 - $180",
            "fumigacion": "$60 - $150",
            "reparacion": "$40 - $200",
        }

        base = precios_base.get(servicio, "$50 - $150")

        if urgencia == "alta":
            return f"{base} (tarifa de emergencia puede aplicar)"
        return base
