from core.banner import mostrar_banner
from core.files import solicitar_ruta
from core.config import SITIOS, PALABRAS_CLAVE
from core.messages import saludar
from core.display import mostrar_lista



def main():

    nombre_programa = "Smart Excel Cleaner"
    desarrollador = "Alejandro"

    mostrar_banner(nombre_programa)
    saludar(desarrollador)
    mostrar_lista(SITIOS, "Buscando información en")
    mostrar_lista(PALABRAS_CLAVE, "Analizando:")
 
    ruta_archivo = solicitar_ruta()

    if ruta_archivo == "":
        print("No ingresó ninguna ruta.")
    else:
        print("Ruta recibida:")
        print(ruta_archivo)

if __name__ == "__main__":
    main()