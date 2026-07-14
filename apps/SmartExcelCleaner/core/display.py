def mostrar_lista(lista, mensaje):

    for elemento in lista:
        print(f"{mensaje} {elemento}")

def mostrar_hojas(lista_hojas):

    print("\nHojas encontradas:\n")

    for hoja in lista_hojas:
        print(f"- {hoja}")

def mostrar_datos(datos):

    print("\nContenido de la hoja:\n")

    for fila in datos:
        print(fila)