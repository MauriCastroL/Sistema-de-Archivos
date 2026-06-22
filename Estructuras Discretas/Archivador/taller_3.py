from collections import deque
import pandas as pd

# Estas son las areas que deben estar en el excel de forma obligatoria
COLUMNAS_REQUERIDAS = {"ID", "Nombre", "Tipo", "Área", "Subárea"}

class Nodo:
    """
    Representa un nodo del árbol general.
    Puede ser raíz, carpeta, subcarpeta o archivo.
    """
    def __init__(self, id_nodo, nombre, tipo, area=None, subarea=None):
        self.id = id_nodo
        self.nombre = str(nombre).strip()
        self.tipo = str(tipo).strip()
        
        if area == None:
            self.area = None
        else:
            self.area = str(area).strip()

        if subarea == None:
            self.subarea = None
        else:
            self.subarea = str(subarea).strip()

        self.hijos = []

    def agregar_hijo(self, nodo):
        self.hijos.append(nodo)

    def grado(self):
        return len(self.hijos)

    def es_hoja(self):
        return len(self.hijos) == 0

    def __str__(self):
        return f"{self.nombre} ({self.tipo})"


class Arbol:
    """
    Representa un árbol general utilizado para modelar
    la jerarquía de carpetas, subcarpetas y archivos.
    """

    def __init__(self, raiz):
        self.raiz = raiz

    def mostrar_arbol(self, nodo=None, nivel=0):
        """
        Muestra la estructura jerárquica del árbol con formato similar a Linux.
        """
        if nodo is None:
            nodo = self.raiz

        sangria = "    " * nivel

        if nodo.id is None:
            print(f"{sangria}- {nodo.nombre} [{nodo.tipo}]")
        else:
            print(f"{sangria}- {nodo.nombre} [{nodo.tipo}] ID: {nodo.id}")

        for hijo in nodo.hijos:
            self.mostrar_arbol(hijo, nivel + 1)

    def preorden(self, nodo=None, resultado=None):
        """
        con preorden respaldamos primero las carpetas principales
        """
        if resultado is None:
            resultado = []

        if nodo is None:
            nodo = self.raiz

        resultado.append(nodo.nombre)

        for hijo in nodo.hijos:
            self.preorden(hijo, resultado)

        return resultado

    def postorden(self, nodo=None):
        """
        con esto eliminamos primero el contenido antes que la carpeta padre.
        """
        if nodo is None:
            nodo = self.raiz

        for hijo in nodo.hijos:
            self.postorden(hijo)

        nodo.hijos.clear()

    def recorrido_por_niveles(self):
        """
        entrega la lista con los niveles 
        """
        resultado = []
        cola = deque()
        cola.append((self.raiz, 0))

        while cola:
            nodo, nivel = cola.popleft()
            resultado.append((nivel, nodo.nombre))

            for hijo in nodo.hijos:
                cola.append((hijo, nivel + 1))

        return resultado

    def altura(self, nodo=None):
        if nodo is None:
            nodo = self.raiz

        if nodo.es_hoja():
            return 0

        return 1 + max(self.altura(hijo) for hijo in nodo.hijos)

    def grado_arbol(self, nodo=None):
        # Esta funcion muestra el grado del ARBOL: el max(nodo.hijo)
        if nodo is None:
            nodo = self.raiz

        maximo = nodo.grado()

        for hijo in nodo.hijos:
            maximo = max(maximo, self.grado_arbol(hijo))

        return maximo

    def orden(self):
        return self.grado_arbol()


def validar_archivo(df):
    """
    Valida que el archivo excel tenga la estructura ID, nombre, tipo, area y subarea.
    """
    df.columns = df.columns.str.strip()

    columnas_actuales = set(df.columns)
    faltantes = COLUMNAS_REQUERIDAS - columnas_actuales

    if faltantes:
        raise ValueError(f"Faltan columnas obligatorias: {faltantes}")

    if df.empty:
        raise ValueError("El archivo excel esta vacio")

    notificaciones = []
    indices_a_eliminar = []

    # con esto revisamos las filas que le falten parametros
    for indice, fila in df.iterrows():
        campos_faltantes = []

        for columna in COLUMNAS_REQUERIDAS:
            if valor_vacio(fila[columna]):
                campos_faltantes.append(columna)

        if campos_faltantes:
            notificaciones.append(describir_fila_con_error(fila, campos_faltantes))
            indices_a_eliminar.append(indice)

    # elimina las filas que no pueden cargarse
    if indices_a_eliminar:
        df = df.drop(indices_a_eliminar)

    if df.empty:
        raise ValueError("No existen datos validos para cargar el arbol")

    df["Nombre"] = df["Nombre"].astype(str).str.strip()
    df["Tipo"] = df["Tipo"].astype(str).str.strip().str.capitalize()
    df["Área"] = df["Área"].astype(str).str.strip()
    df["Subárea"] = df["Subárea"].astype(str).str.strip()

    if df["ID"].duplicated().any():
        raise ValueError("Existen ID duplicados en los datos validos del archivo")

    tipos_validos = {"Carpeta", "Archivo"}

    for indice, fila in df.iterrows():
        tipo = fila["Tipo"]

        if tipo not in tipos_validos:
            raise ValueError(f"{tipo} es un tipo no valido, debe probar con: {tipos_validos}")

    return df, notificaciones


def valor_vacio(valor):
    """
    avisa si falta un parametro en el arcvhjivo (validacion de archivo)
    """
    if pd.isna(valor):
        return True

    if str(valor).strip() == "":
        return True

    return False


def describir_fila_con_error(fila, campos_faltantes):
    """
    crea el texto de notificacion para una fila que no pudo cargarse (validacion de archivo)
    """
    partes = []

    for columna in ["ID", "Nombre", "Tipo", "Área", "Subárea"]:
        valor = fila.get(columna, None)

        if valor_vacio(valor):
            valor = "None"

        partes.append(f"{columna}={valor}")

    campos = ", ".join(campos_faltantes)
    datos = ", ".join(partes)

    return f"Dato con: {datos} no fue posible cargarse por tener parametro None en: {campos}"

def generar_arbol(ruta_excel):
    """
    Agrega los nodos y aplica el modelo del sistema
    """

    df = pd.read_excel(ruta_excel, sheet_name="Registro de archivos")
    df, notificaciones = validar_archivo(df)

    # Filtro de pandas para poder buscar el nodo raiz
    fila_raiz = df[
        (df["Tipo"] == "Carpeta")
        & (df["Área"] == "Sistema")
        & (df["Subárea"] == "Raíz")
    ]

    # Crea el nodo si es que no lo encuentra 
    if fila_raiz.empty:
        raiz = Nodo(None, "Servidor_Principal", "Raíz", "Sistema", "Raíz")
    else:
        datos_raiz = fila_raiz.iloc[0]
        raiz = Nodo(datos_raiz["ID"], datos_raiz["Nombre"], "Raíz", datos_raiz["Área"], datos_raiz["Subárea"])

    arbol = Arbol(raiz, notificaciones)

    carpetas_principales = {}
    subcarpetas = {}

    filas_carpetas_principales = df[
        (df["Tipo"] == "Carpeta")
        & (df["Área"] == "Sistema")
        & (df["Subárea"] != "Raíz")
    ]

    # Agregamos al arbol las carpertas principales, sistema
    for _, fila in filas_carpetas_principales.iterrows():
        nodo = Nodo(fila["ID"], fila["Nombre"], fila["Tipo"], fila["Área"], fila["Subárea"])

        raiz.agregar_hijo(nodo)

        carpetas_principales[fila["Nombre"]] = nodo
        carpetas_principales[fila["Subárea"]] = nodo

    filas_subcarpetas = df[
        (df["Tipo"] == "Carpeta")
        & (df["Área"] != "Sistema")
    ]

    # Agregamos las subcarpetas, las no pertenecientes al sistema
    for _, fila in filas_subcarpetas.iterrows():
        area = fila["Área"]
        subarea = fila["Subárea"]

        padre = carpetas_principales.get(area)

        if padre is None:
            padre = Nodo(None, area, "Carpeta", area, None)
            raiz.agregar_hijo(padre)
            carpetas_principales[area] = padre

        nodo = Nodo(fila["ID"], fila["Nombre"], fila["Tipo"], fila["Área"], fila["Subárea"])

        padre.agregar_hijo(nodo)

        subcarpetas[(area, subarea)] = nodo
        subcarpetas[(area, fila["Nombre"])] = nodo

    filas_archivos = df[df["Tipo"] == "Archivo"]

    for _, fila in filas_archivos.iterrows():
        area = fila["Área"]
        subarea = fila["Subárea"]

        padre = subcarpetas.get((area, subarea))

        if padre is None:
            carpeta_area = carpetas_principales.get(area)

            if carpeta_area is None:
                carpeta_area = Nodo(None, area, "Carpeta", area, None)
                raiz.agregar_hijo(carpeta_area)
                carpetas_principales[area] = carpeta_area

            padre = Nodo(None, subarea, "Carpeta", area, subarea)

            carpeta_area.agregar_hijo(padre)
            subcarpetas[(area, subarea)] = padre

        archivo = Nodo(fila["ID"], fila["Nombre"], fila["Tipo"], fila["Área"], fila["Subárea"])

        padre.agregar_hijo(archivo)

    return arbol

def mostrar_formato_sistema_carpetas(arbol):
    arbol.mostrar_arbol()

def mostrar_notificaciones_carga(arbol):
    """
    Muestra las filas que no pudieron cargarse por tener parametros faltantes
    """
    if not arbol.notificaciones_carga:
        return

    print("\nLineas con falla en la carga:")
    for notificacion in arbol.notificaciones_carga:
        print(f"- {notificacion}")

def mostrar_recorrido_por_niveles(arbol):
    """
    Muestra el recorrido por niveles en consola.
    """
    for nivel, nombre in arbol.recorrido_por_niveles():
        print(f"Nivel {nivel}: {nombre}")

def generar_respaldo(arbol):
    resultado = arbol.preorden()
    return resultado

def eliminar_post_orden(arbol):
    """
    Busca una ruta exacta, pide confirmación, guarda un respaldo
    de lo que se va a borrar, y luego elimina el nodo y su contenido.
    """
    opcion = 1
    respaldo = None
    
    while opcion == 1:
        ruta = input("Ingrese la ruta (ej: Servidor_Principal/Finanzas/Contratos): ").strip()
        
        if not ruta:
            print("La ruta no puede estar vacía.")
            continue
            
        direccion = ruta.split("/")
        
        # 1. Validación: escritura erronea de la raiz
        nodo_actual = arbol.raiz
        if direccion[0] != nodo_actual.nombre:
            print(f"Error: La ruta debe iniciar correctamente con la raiz '{nodo_actual.nombre}'.")
            print("1. Volver a intentar")
            print("2. Cancelar")
            opcion = int(input("Ingrese: "))
            continue

        # 2. Validación: No permitir borrar el servidor entero desde aquí
        if len(direccion) == 1:
            print("Error: No está permitido eliminar el nodo raíz principal.")
            print("1. Volver a intentar")
            print("2. Cancelar")
            opcion = int(input("Ingrese: "))
            continue

        nodo_padre = None
        ruta_valida = True
        
        # 3. Navegacion nivel por nivel (omitimos [0] porque ya validamos la raíz)
        for parte in direccion[1:]:
            nodo_padre = nodo_actual
            encontrado = False
            
            # Buscamos 'parte' entre los hijos del nodo actual
            for hijo in nodo_actual.hijos:
                if hijo.nombre == parte:
                    nodo_actual = hijo
                    encontrado = True
                    break
            
            # 4. Validación: ¿Qué pasa si la carpeta/archivo no existe?
            if not encontrado:
                ruta_valida = False
                print(f"Error: No se encontró '{parte}' en la ruta especificada.")
                break
        
        # Si la ruta fallo
        if not ruta_valida:
            print("1. Volver a intentar")
            print("2. Cancelar")
            opcion = int(input("Ingrese: "))
            continue
            
        # 5. Proceso Final: Si llegamos aquí, la ruta existe y es correcta
        print(f"\nSe encontró: {nodo_actual.nombre} ({nodo_actual.tipo})")
        print("1. Para eliminar el elemento (y su contenido) y guardar el respaldo")
        print("2. Para anular operación")
        opcion_final = int(input("Ingrese: "))
        
        if opcion_final == 1:
            # A) Guardamos el respaldo ANTES de eliminar el contenido.
            respaldo = arbol.preorden(nodo_actual)
            
            # B) Vaciamos el contenido usando la función postorden
            arbol.postorden(nodo_actual)
            
            # C) Eliminamos el nodo de su padre
            nodo_padre.hijos.remove(nodo_actual)
            
            print(f"Elemento '{nodo_actual.nombre}' eliminado.")
            print(f"Respaldo generado: {respaldo}")
            break
        else:
            print("Operacion anulada.")
            break
            
    return respaldo
  
def ver_grados(arbol):
    # Muestro el grado del arbol
    print(f"Grado del arbol: {arbol.grado_arbol()}")
    
    # Muestro el grado de cada nodo del arbol
    def recorrer_preorden_grados(nodo, nivel=0):
        sangria = "    " * nivel
        print(f"{sangria}- {nodo.nombre} [{nodo.tipo}] -> Grado: {nodo.grado()}")

        for hijo in nodo.hijos:
            recorrer_preorden_grados(hijo, nivel + 1)

    recorrer_preorden_grados(arbol.raiz)
    
def ver_altura(arbol):
    print(f"orden: {arbol.altura()}")
    
def ver_orden(arbol):
    print(f"orden: {arbol.orden()}")

def leer_opcion(mensaje):
    try:
        return int(input(mensaje).strip())
    except ValueError:
        print("Debe ingresar un numero valido.")
        return None

def menu():
    print("1. Mostrar la estructura (formato sistema de carpetas)")
    print("2. Mostrar la estructura por niveles")
    print("3. Generar respaldo (comenzando por las carpetas principales)")
    print("4. Eliminar carpeta/archivo (se eliminar su contenido) pero este se respaldara")
    print("5. ver las propiedades del arbol")
    print("6. salir")

def menu_propiedades():
    print("1. mostrar grado")
    print("2. ver altura")
    print("3. ver orden")
    print("4. cancelar")

if __name__ == "__main__":
    opcion_archivo = 0
    opcion = 0
    opcion_propiedades = 0
    respaldo_arbol = []
    respaldo_nodo = Nodo
    
    while(opcion_archivo == 0):
        ruta_excel = input("Ingrese la ruta del archivo Excel: ").strip()
    
        if ruta_excel == "":
            ruta_excel = "Metadatos.xlsx"

        try:
            arbol = generar_arbol(ruta_excel)
            print("\nArchivo cargado correctamente.")
            while(opcion != 6):
                menu()
                opcion = leer_opcion("Seleccione una opcion: ")

                if opcion is None:
                    continue

                match opcion:
                    case 1:
                        mostrar_formato_sistema_carpetas(arbol)
                    case 2:
                        mostrar_recorrido_por_niveles(arbol)
                    case 3:
                        ultima_respaldo = generar_respaldo(arbol) # no se que hacer con este respaldo pero porsiacaso lo guardo.
                    case 4:
                        print("indique el nodo/archivo que desea eliminar con la siguiente estructura")
                        print("ruta/y/nombre/exacto/a/borrar")
                        print("donde la ruta ingresada sera el elemento a borrar")
                        print("si no existe la ruta a borrar se le pedira ingresar una nueva o salir")
                        eliminar_post_orden(arbol)
                    case 5:
                        menu_propiedades()
                        opcion_propiedades = int(input(""))
                        match opcion_propiedades:
                            case 1:
                                ver_grados(arbol)
                            case 2:
                                ver_altura(arbol)
                            case 3:
                                ver_orden(arbol)


        except FileNotFoundError:
            print("No se encontro el archivo")
        except ValueError as error:
            print(f"Hubo un error: {error}")
        except Exception as error:
            print(f"{error}")

        opcion_archivo = leer_opcion("Si desea ingresar otro excel ingrese 0, de lo contrario digite 1: ")
        if opcion_archivo is None:
            opcion_archivo = 1
