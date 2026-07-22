"""Integración con Google Sheets para guardar leads."""
import gspread
from google.oauth2.service_account import Credentials
from app.config import settings
import json

# Scopes necesarios
SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

def get_sheets_client():
    """Obtiene cliente autenticado de Google Sheets."""
    try:
        creds = Credentials.from_service_account_file(
            settings.google_sheets_credentials_path,
            scopes=SCOPES
        )
        return gspread.authorize(creds)
    except Exception as e:
        print(f"Error autenticando con Google Sheets: {e}")
        return None

def ensure_sheet_exists(client, sheet_name: str):
    """Crea la hoja si no existe con los headers correctos."""
    try:
        # Intentar abrir
        spreadsheet = client.open(sheet_name)
    except gspread.SpreadsheetNotFound:
        # Crear nueva
        spreadsheet = client.create(sheet_name)
        worksheet = spreadsheet.sheet1

        # Headers
        headers = [
            "Fecha", "Hora", "Nombre", "Teléfono", "Email",
            "Ciudad", "Dirección", "Tipo Servicio", "Problema",
            "Urgencia", "Horario", "Precio Estimado", "Estado",
            "Canal", "Origen", "Notas"
        ]
        worksheet.append_row(headers)

        # Compartir con el email configurado
        spreadsheet.share(settings.email_to, perm_type="user", role="writer")

    return spreadsheet

async def save_lead(lead_data: dict):
    """Guarda un lead en Google Sheets."""
    try:
        client = get_sheets_client()
        if not client:
            print("No se pudo conectar a Google Sheets")
            return False

        spreadsheet = ensure_sheet_exists(client, settings.google_sheet_name)
        worksheet = spreadsheet.sheet1

        from datetime import datetime
        now = datetime.now()

        row = [
            now.strftime("%Y-%m-%d"),
            now.strftime("%H:%M:%S"),
            lead_data.get("nombre", ""),
            lead_data.get("telefono", ""),
            lead_data.get("email", ""),
            lead_data.get("ciudad", ""),
            lead_data.get("direccion", ""),
            lead_data.get("tipo_servicio", ""),
            lead_data.get("problema", ""),
            lead_data.get("urgencia", ""),
            lead_data.get("horario", ""),
            lead_data.get("precio_estimado", ""),
            lead_data.get("estado", "pendiente"),
            lead_data.get("canal", "whatsapp"),
            lead_data.get("origen", "organico"),
            lead_data.get("notas", "")
        ]

        worksheet.append_row(row)
        print(f"✅ Lead guardado: {lead_data.get('nombre', 'N/A')}")
        return True

    except Exception as e:
        print(f"Error guardando lead: {e}")
        return False
