"""Guardado de leads en Google Sheets."""
from app.config import settings
import json

async def save_lead(lead_data: dict):
    """Guarda un lead en Google Sheets."""
    print(f"[SHEETS] Guardando lead: {lead_data.get('nombre', 'N/A')}")

    # TODO: Implementar conexion real con Google Sheets
    # Por ahora solo logueamos
    print(f"[SHEETS] Datos: {json.dumps(lead_data, ensure_ascii=False, indent=2)}")

    # Si tienes credentials.json configurado, descomenta esto:
    # import gspread
    # from google.oauth2.service_account import Credentials
    # 
    # scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    # creds = Credentials.from_service_account_file(settings.google_sheets_credentials_path, scopes=scope)
    # client = gspread.authorize(creds)
    # sheet = client.open(settings.google_sheet_name).sheet1
    # 
    # row = [
    #     lead_data.get("fecha_hora", ""),
    #     lead_data.get("nombre", ""),
    #     lead_data.get("telefono", ""),
    #     lead_data.get("email", ""),
    #     lead_data.get("ciudad", ""),
    #     lead_data.get("direccion", ""),
    #     lead_data.get("tipo_servicio", ""),
    #     lead_data.get("problema", ""),
    #     lead_data.get("urgencia", ""),
    #     lead_data.get("horario", ""),
    #     lead_data.get("precio_estimado", ""),
    #     lead_data.get("estado", "pendiente"),
    # ]
    # sheet.append_row(row)
    # print("[SHEETS] Lead guardado en Google Sheets")
