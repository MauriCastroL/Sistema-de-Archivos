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
        if nodo is None:
            nodo = self.raiz

        maximo = nodo.grado()

        for hijo in nodo.hijos:
            maximo = max(maximo, self.grado_arbol(hijo))

        return maximo

    def orden(self):
        return self.grado_arbol()

    def buscar_por_nombre(self, nombre_buscado, nodo=None, encontrados=None):
        """
        Busca nodos por nombre, devuelve una lista de coincidencias
        """
        if encontrados is None:
            encontrados = []

        if nodo is None:
            nodo = self.raiz

        if nodo.nombre.lower() == nombre_buscado.lower():
            encontrados.append(nodo)

        for hijo in nodo.hijos:
            self.buscar_por_nombre(nombre_buscado, hijo, encontrados)

        return encontrados

    def buscar_por_tipo(self, tipo_buscado, nodo=None, encontrados=None):
        """
        Con esto podemos buscar de acuerdo al tipo de archivo
        """
        if encontrados is None:
            encontrados = []

        if nodo is None:
            nodo = self.raiz

        if nodo.tipo.lower() == tipo_buscado.lower():
            encontrados.append(nodo)

        for hijo in nodo.hijos:
            self.buscar_por_tipo(tipo_buscado, hijo, encontrados)

        return encontrados


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
        raise ValueError("El archivo excel está vacío")

    if df["ID"].duplicated().any():
        raise ValueError("Existen ID duplicados en el archivo")

    df["Nombre"] = df["Nombre"].astype(str).str.strip()
    df["Tipo"] = df["Tipo"].astype(str).str.strip()
    df["Área"] = df["Área"].astype(str).str.strip()
    df["Subárea"] = df["Subárea"].astype(str).str.strip()

    tipos_validos = {"Carpeta", "Archivo"}

    for tipo in df["Tipo"]:
        if tipo not in tipos_validos:
            raise ValueError(f"{tipo} es un tipo no valido de archivo, debe probar con: {tipos_validos}")

    return df


def generar_arbol(ruta_excel):
    """
    Agrega los nodos y aplica el modelo del sistema
    """

    df = pd.read_excel(ruta_excel, sheet_name="Registro de archivos")
    df = validar_archivo(df)

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

    arbol = Arbol(raiz)

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

def mostrar_recorrido_por_niveles(arbol):
    """
    Muestra el recorrido por niveles en consola.
    """
    for nivel, nombre in arbol.recorrido_por_niveles():
        print(f"Nivel {nivel}: {nombre}")

def generar_respaldo(arbol):
    resultado = arbol.preorden()
    return resultado

def eliminar_post_orden(arbol): #hay que eliminar post orden pero antes hay que guardar lo que se borra
    opcion = 0
    while(opcion == 0):
        ruta = input("ingrese la ruta:")
        direccion = ruta.split("/")
        largo_ruta = len(direccion)
        temporal = 0
        nodo = arbol
        nodo_padre = arbol
        lista_hijos = []
        temporal_lista = 1
        while(temporal < largo_ruta):
            if(direccion[temporal] == nodo.nombre):
                temporal = temporal + 1
                lista_hijos = nodo.hijos()
                nodo_padre = nodo
                nodo = lista_hijos[0]
                if(temporal == largo_ruta):
                    break
                temporal_lista = 1
            else:
                if(temporal_lista < len(lista_hijos)):
                    nodo = lista_hijos[temporal_lista]
                    temporal_lista = temporal_lista + 1
                else:
                    print("la ruta no existe")
                    print("1. volver a ingresar ruta")
                    print("2. cancelar")
                    opcion = int(input("ingrese: "))
                    break
        respaldo = nodo
        arbol.postorden(nodo)
        nodo_padre.hijos.pop(temporal_lista)

    
def ver_grados(arbol):
    pass #intuyo que se refiere a ver el grado de todos los nodos.
    
def ver_altura(arbol):
    print(f"orden: {arbol.altura()}")
    
def ver_orden(arbol):
    print(f"orden: {arbol.orden()}")

def menu():
    print("1. Mostrar la estructura (formato sistema de carpetas)")
    print("2. Mostrar la estructura por niveles")
    print("3. Generar respaldo (comenzando por las carpetas principales)")
    print("4. Eliminar carpeta/archivo (se eliminar su contenido) pero este se respaldara")
    print("5. ver las propiedades del arbol")
    print("6. salir")

"""
para eliminar hay que crear un formato que el usuario ingrese
cuando ingrese este formato hay que validar que sea correcto y
validar que el archivo o carpeta existe.
Nota: el eliminar con su contenido se puede hacer con el post-orden.
"""

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
                opcion = int(input(""))
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

        opcion_archivo = int(input("si desea ingresar otro excel ingrese 0, de lo contrario digite 1."))
