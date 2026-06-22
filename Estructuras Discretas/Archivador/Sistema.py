import pandas as pd
from Arbol import Arbol

def normalizar_columna(columna):
    columna = str(columna).strip().lower()

    columna = columna.replace("á", "a")
    columna = columna.replace("é", "e")
    columna = columna.replace("í", "i")
    columna = columna.replace("ó", "o")
    columna = columna.replace("ú", "u")

    columna = columna.replace("-", "")
    columna = columna.replace("_", "")
    columna = columna.replace(" ", "")

    return columna


def generar_id(ids_usados, contador):
    nuevo_id = f"AUTO_{contador}"

    while nuevo_id in ids_usados:
        contador += 1
        nuevo_id = f"AUTO_{contador}"

    return nuevo_id, contador + 1


def preparar_registros(ruta_excel):
    registros_validos = []
    errores = []
    advertencias = []
    ids_usados = set()
    contador_id = 1

    try:
        datos = pd.read_excel(ruta_excel, dtype=str, keep_default_na=False)

    except FileNotFoundError:
        errores.append(f"No se encontró el archivo '{ruta_excel}'.")
        return registros_validos, errores, advertencias

    except Exception as error:
        errores.append(f"No se pudo leer el archivo excel {error}")
        return registros_validos, errores, advertencias

    columnas = {}

    for columna in datos.columns:
        columna_normalizada = normalizar_columna(columna)
        columnas[columna_normalizada] = columna

    columnas_obligatorias = ["id", "nombre", "tipo", "area", "subarea"]

    for columna in columnas_obligatorias:
        if columna not in columnas:
            errores.append(f"Falta la columna obligatoria '{columna}'.")

    if len(errores) > 0:
        return registros_validos, errores, advertencias

    for indice, fila in datos.iterrows():
        fila_excel = indice + 2
        problemas = []

        id_nodo = str(fila[columnas["id"]]).strip()
        nombre = str(fila[columnas["nombre"]]).strip()
        tipo = str(fila[columnas["tipo"]]).strip()
        area = str(fila[columnas["area"]]).strip()
        subarea = str(fila[columnas["subarea"]]).strip()

        if nombre == "":
            problemas.append("Nombre vacío")

        if tipo == "":
            problemas.append("Tipo vacío")

        if area == "":
            problemas.append("Área vacía")

        if subarea == "":
            problemas.append("Subárea vacía")

        tipo_normalizado = tipo.lower()

        if tipo != "" and tipo_normalizado not in ["carpeta", "archivo"]:
            problemas.append("EL tipo del archivo debe ser carpeta o archivo")

        if id_nodo != "" and id_nodo in ids_usados:
            problemas.append(f"ID repetido '{id_nodo}'")

        if len(problemas) > 0:
            errores.append({"fila": fila_excel, "id": id_nodo, "nombre": nombre, "tipo": tipo, "area": area, "subarea": subarea, "problemas": problemas})
            continue

        if id_nodo == "":
            id_nodo, contador_id = generar_id(ids_usados, contador_id)

            advertencias.append(f"Fila {fila_excel} tiene id vacio, se le asignó automáticamente el ID '{id_nodo}'")

        ids_usados.add(id_nodo)

        if tipo_normalizado == "carpeta":
            tipo = "Carpeta"
        else:
            tipo = "Archivo"

        registro = {"id": id_nodo, "nombre": nombre, "tipo": tipo, "area": area, "subarea": subarea, "fila_excel": fila_excel}

        registros_validos.append(registro)

    return registros_validos, errores, advertencias


def cargar_arbol_desde_excel(ruta_excel):
    registros, errores_carga, advertencias = preparar_registros(ruta_excel)

    arbol = Arbol()

    if len(registros) == 0:
        return arbol, registros, errores_carga, advertencias

    arbol.construir_desde_registros(registros)

    return arbol, registros, errores_carga, advertencias


def mostrar_resumen_carga(arbol, registros, errores_carga, advertencias):
    print("\nResumen de errores y faltas en el archivo cargado")
    print(f"Registros válidos leídos: {len(registros)}")
    print(f"Nodos cargados en el árbol: {arbol.orden()}")

    if len(advertencias) > 0:
        print("\nAdvertencias:")

        for advertencia in advertencias:
            print(f"- {advertencia}")

    if len(errores_carga) > 0:
        print("\nFilas no cargadas por errores de validación:")

        for error in errores_carga:
            if isinstance(error, str):
                print(f"- {error}")

            else:
                print(
                    f"- Fila {error['fila']}: "
                    f"ID={error['id']}, "
                    f"Nombre={error['nombre']}, "
                    f"Tipo={error['tipo']}, "
                    f"Área={error['area']}, "
                    f"Subárea={error['subarea']}"
                )

                for problema in error["problemas"]:
                    print(f"  * {problema}")

    if len(arbol.errores) > 0:
        print("\nErrores al construir el árbol:")

        for error in arbol.errores:
            print(f"- {error}")

    print("\n")

def nodo_desde_texto(arbol, texto):
    texto = str(texto).strip()

    if texto == "":
        return None, "Debe ingresar un ID, ruta o nombre."

    nodo = arbol.buscar_por_id(texto)

    if nodo is not None:
        return nodo, "Nodo encontrado por ID."

    nodo = arbol.buscar_por_ruta(texto)

    if nodo is not None:
        return nodo, "Nodo encontrado por ruta"

    encontrados = arbol.buscar_por_nombre(texto)

    if len(encontrados) == 1:
        return encontrados[0], "Nodo encontrado por nombre"

    if len(encontrados) > 1:
        mensaje = "El nombre ingresado es ambiguo. Coincidencias encontradas:"

        for encontrado in encontrados:
            mensaje += f"\n- ID {encontrado.id}: {encontrado.ruta()}"

        mensaje += "\nIngrese el id o la ruta del nodo."

        return None, mensaje

    return None, "No se encontró ningún nodo con ese ID, ruta o nombre."

if __name__ == "__main__":
    arbol = Arbol()
    registros = []
    errores_carga = []
    advertencias = []

    while True:
        print("\nAdministrador de archivos")
        print("1 Cargar archivo Excel")
        print("2 Mostrar estructura jerárquica")
        print("3 Mostrar recorrido preorden")
        print("4 Mostrar recorrido postorden")
        print("5 Mostrar estructura por niveles")
        print("6 Mostrar propiedades del árbol")
        print("7 Eliminar nodo con respaldo")
        print("8 Mostrar respaldo de eliminaciones")
        print("9 Salir")
        print("\n")
        opcion = input("Seleccione una opción: ").strip()

        if opcion == "1":
            ruta = input("Ingrese la ruta de su archivo excel, se carga Metadatos.xlsx automatica si se encuentra en la misma carpeta que el codigo y en cado de que no ingrese nada: ").strip()

            if ruta == "":
                ruta = "Metadatos.xlsx"

            arbol, registros, errores_carga, advertencias = cargar_arbol_desde_excel(ruta)
            mostrar_resumen_carga(arbol, registros, errores_carga, advertencias)

        elif opcion == "2":
            if arbol.esta_vacio():
                print("Primero debe cargar un archivo Excel.")
                continue

            print("\nEstructura jerarquica del arbol")

            for linea in arbol.lineas_arbol():
                print(linea)

            print("n")

        elif opcion == "3":
            if arbol.esta_vacio():
                print("Primero debe cargar un archivo Excel.")
                continue

            print("\nPreorden")
            print("Orden usado para respaldar primero carpetas principales.\n")

            recorrido = arbol.recorrido_preorden()

            for indice, nodo in enumerate(recorrido, start=1):
                print(f"{indice}. {nodo} | Ruta: {nodo.ruta()}")

            print("\n")

        elif opcion == "4":
            if arbol.esta_vacio():
                print("Primero debe cargar un archivo Excel.")
                continue

            print("\nPostorden")
            print("Orden usado para eliminar contenido antes que carpetas.\n")

            recorrido = arbol.recorrido_postorden()

            for indice, nodo in enumerate(recorrido, start=1):
                print(f"{indice}. {nodo} | Ruta: {nodo.ruta()}")

            print("\n")

        elif opcion == "5":
            if arbol.esta_vacio():
                print("Primero debe cargar un archivo Excel.")
                continue

            print("\nEstructura del arbol por niveles")

            recorrido = arbol.recorrido_por_niveles()
            nivel_actual = -1

            for dato in recorrido:
                nodo = dato["nodo"]
                nivel = dato["nivel"]

                if nivel != nivel_actual:
                    nivel_actual = nivel
                    print(f"\nNivel {nivel_actual}:")

                print(f"- {nodo} | Grado: {nodo.grado()}")

            print("\n")

        elif opcion == "6":
            if arbol.esta_vacio():
                print("Primero debe cargar un archivo Excel.")
                continue

            print("\nPropiedades del arbol")

            altura = arbol.altura()

            print(f"Orden del árbol: {arbol.orden()}")
            print(f"Grado del árbol: {arbol.grado_arbol()}")
            print(f"Altura en aristas: {altura}")

            if altura >= 0:
                print(f"Altura en niveles: {altura + 1}")
            else:
                print("Altura en niveles: 0")

            print("\nGrado de cada nodo:")

            for dato in arbol.grados_por_nodo():
                print(
                    f"- {dato['ruta']} | "
                    f"ID: {dato['id']} | "
                    f"Tipo: {dato['tipo']} | "
                    f"Grado: {dato['grado']}"
                )

            print("\n")

        elif opcion == "7":
            if arbol.esta_vacio():
                print("Primero debe cargar un archivo Excel.")
                continue

            print("\nPuede eliminar por ID, ruta completa o nombre no ambiguo.")
            entrada = input("Ingrese el nodo que desea eliminar: ").strip()

            nodo, mensaje = nodo_desde_texto(arbol, entrada)

            if nodo is None:
                print(mensaje)
                continue

            print(f"\nNodo seleccionado: {nodo}")
            print(f"Ruta: {nodo.ruta()}")

            confirmacion = input("¿Confirma la eliminación con respaldo? (s/n): ").strip().lower()

            if confirmacion != "s":
                print("Eliminación cancelada.")
                continue

            exito, mensaje = arbol.eliminar_con_respaldo(nodo)
            print(mensaje)

        elif opcion == "8":
            if len(arbol.respaldo_eliminados) == 0:
                print("No hay respaldos de eliminación registrados.")
                continue

            print("\nRespaldo de las eliminaciones")

            for indice, dato in enumerate(arbol.respaldo_eliminados, start=1):
                print(
                    f"{indice}. "
                    f"ID: {dato['id']} | "
                    f"Nombre: {dato['nombre']} | "
                    f"Tipo: {dato['tipo']} | "
                    f"Ruta original: {dato['ruta']}"
                )

            print("\n")

        else:
            print("Debe ingresar un numero del 1-9")