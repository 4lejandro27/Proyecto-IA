import os
from openpyxl import load_workbook


def validar_archivo_excel(ruta_archivo):

    if not os.path.exists(ruta_archivo):
        return False, "La ruta del archivo no existe."

    extension = os.path.splitext(ruta_archivo)[1].lower()

    if extension not in [".xlsx", ".xls"]:
        return False, "El archivo no tiene una extensión de Excel."

    try:
        load_workbook(ruta_archivo)
    except Exception:
        return False, "El archivo está dañado o no es un Excel válido."

    return True, "Archivo válido."