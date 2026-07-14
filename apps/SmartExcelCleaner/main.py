from core.banner import mostrar_banner
from core.files import solicitar_ruta
from core.config import SITIOS, PALABRAS_CLAVE
from core.messages import saludar
from core.display import mostrar_lista, mostrar_hojas, mostrar_datos
from core.validator import validar_archivo_excel
from core.reader import obtener_hojas_excel, leer_hoja_excel
from core.cleaner import eliminar_filas_vacias

def main():

    nombre_programa = "Smart Excel Cleaner"
    desarrollador = "Alejandro"

    mostrar_banner(nombre_programa)
    saludar(desarrollador)
    mostrar_lista(SITIOS, "Buscando información en")
    mostrar_lista(PALABRAS_CLAVE, "Analizando:")
 
    ruta_archivo = solicitar_ruta()

    es_valido, mensaje = validar_archivo_excel(ruta_archivo)    
    

    if es_valido:
        hojas = obtener_hojas_excel(ruta_archivo)
        mostrar_hojas(hojas)
        datos = leer_hoja_excel(ruta_archivo, hojas[0])
        mostrar_datos(datos)
    else:
        print(mensaje)

    
    if ruta_archivo == "":
        print("No ingresó ninguna ruta.")
        

if __name__ == "__main__":
    main()