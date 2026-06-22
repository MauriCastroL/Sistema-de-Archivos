from collections import deque
from Nodo import Nodo

class Arbol:
    def __init__(self):
        self.raiz = None

        self.nodos_por_id = {}
        self.nodos_por_ruta = {}
        self.carpetas_por_clave = {}

        self.errores = []
        self.advertencias = []
        self.respaldo_eliminados = []

    def reiniciar(self):
        self.raiz = None

        self.nodos_por_id = {}
        self.nodos_por_ruta = {}
        self.carpetas_por_clave = {}

        self.errores = []
        self.advertencias = []
        self.respaldo_eliminados = []

    def esta_vacio(self):
        return self.raiz is None

    def normalizar_clave(self, texto):
        if texto is None:
            return ""

        return str(texto).strip().lower()

    def registrar_nodo(self, nodo):
        if nodo.id in self.nodos_por_id:
            raise ValueError(f"Ya hay un nodo con este id '{nodo.id}'.")

        ruta = self.normalizar_clave(nodo.ruta())

        if ruta in self.nodos_por_ruta:
            raise ValueError(f"Ya hay un nodo con la ruta '{nodo.ruta()}'.")

        self.nodos_por_id[nodo.id] = nodo
        self.nodos_por_ruta[ruta] = nodo

        if nodo.tipo == "Carpeta":
            clave = (
                self.normalizar_clave(nodo.area),
                self.normalizar_clave(nodo.subarea)
            )

            if clave in self.carpetas_por_clave:
                raise ValueError(
                    f"Ya hay una carpeta con área '{nodo.area}' "
                    f"y subárea '{nodo.subarea}'."
                )

            self.carpetas_por_clave[clave] = nodo

    def reconstruir_indices(self):
        self.nodos_por_id = {}
        self.nodos_por_ruta = {}
        self.carpetas_por_clave = {}

        def recorrer(nodo):
            self.registrar_nodo(nodo)

            for hijo in nodo.hijos:
                recorrer(hijo)

        if self.raiz is not None:
            recorrer(self.raiz)

    def construir_desde_registros(self, registros):
        self.reiniciar()

        raices = []

        for registro in registros:
            tipo = self.normalizar_clave(registro["tipo"])
            area = self.normalizar_clave(registro["area"])
            subarea = self.normalizar_clave(registro["subarea"])

            if tipo == "carpeta" and area == "sistema" and subarea in ["raiz", "raíz"]:
                raices.append(registro)

        if len(raices) == 0:
            self.errores.append("Dado que no hay raíz no se puede construir el árbol")
            return False

        if len(raices) > 1:
            self.errores.append("Se encontró más de una raíz no se puede construir el árbol")
            return False

        raiz_registro = raices[0]

        try:
            self.raiz = Nodo(raiz_registro["id"],raiz_registro["nombre"],raiz_registro["tipo"],raiz_registro["area"], raiz_registro["subarea"])
            self.registrar_nodo(self.raiz)

        except ValueError as error:
            self.errores.append(f"{error}")
            self.raiz = None
            return False

        for registro in registros:
            tipo = self.normalizar_clave(registro["tipo"])
            area = self.normalizar_clave(registro["area"])
            subarea = self.normalizar_clave(registro["subarea"])

            es_raiz = (tipo == "carpeta" and area == "sistema" and subarea in ["raiz", "raíz"])

            if tipo == "carpeta" and area == "sistema" and not es_raiz:
                carpeta = None

                try:
                    carpeta = Nodo(registro["id"], registro["nombre"],registro["tipo"], registro["area"],registro["subarea"])

                    self.raiz.agregar_hijo(carpeta)
                    self.registrar_nodo(carpeta)

                except ValueError as error:
                    if carpeta is not None and carpeta.padre == self.raiz:
                        self.raiz.quitar_hijo(carpeta)

                    self.errores.append(
                        f"Error al cargar carpeta principal '{registro['nombre']}': {error}"
                    )

        for registro in registros:
            tipo = self.normalizar_clave(registro["tipo"])
            area = self.normalizar_clave(registro["area"])

            if tipo == "carpeta" and area != "sistema":
                clave_padre = ("sistema", area)
                padre = self.carpetas_por_clave.get(clave_padre)

                if padre is None:
                    self.errores.append(
                        f"No se pudo cargar la subcarpeta '{registro['nombre']}'. "
                        f"No existe la carpeta principal '{registro['area']}'."
                    )
                    continue

                subcarpeta = None

                try:
                    subcarpeta = Nodo(registro["id"], registro["nombre"], registro["tipo"], registro["area"], registro["subarea"])

                    padre.agregar_hijo(subcarpeta)
                    self.registrar_nodo(subcarpeta)

                except ValueError as error:
                    if subcarpeta is not None and subcarpeta.padre == padre:
                        padre.quitar_hijo(subcarpeta)

                    self.errores.append(f"Error al cargar subcarpeta '{registro['nombre']}': {error}")

        for registro in registros:
            tipo = self.normalizar_clave(registro["tipo"])
            area = self.normalizar_clave(registro["area"])
            subarea = self.normalizar_clave(registro["subarea"])

            if tipo == "archivo":
                clave_padre = (area, subarea)
                padre = self.carpetas_por_clave.get(clave_padre)

                if padre is None:
                    self.errores.append(
                        f"No se pudo cargar el archivo '{registro['nombre']}'. "
                        f"No existe la carpeta padre con área '{registro['area']}' "
                        f"y subárea '{registro['subarea']}'."
                    )
                    continue

                archivo = None

                try:
                    archivo = Nodo(registro["id"], registro["nombre"], registro["tipo"], registro["area"], registro["subarea"])

                    padre.agregar_hijo(archivo)
                    self.registrar_nodo(archivo)

                except ValueError as error:
                    if archivo is not None and archivo.padre == padre:
                        padre.quitar_hijo(archivo)

                    self.errores.append(
                        f"Error al cargar archivo '{registro['nombre']}': {error}"
                    )

        self.reconstruir_indices()

        return True

    def buscar_por_id(self, id_nodo):
        id_nodo = str(id_nodo).strip()
        return self.nodos_por_id.get(id_nodo)

    def buscar_por_ruta(self, ruta):
        ruta = self.normalizar_clave(ruta)
        return self.nodos_por_ruta.get(ruta)

    def buscar_por_nombre(self, nombre):
        nombre = self.normalizar_clave(nombre)
        encontrados = []

        for nodo in self.nodos_por_id.values():
            if self.normalizar_clave(nodo.nombre) == nombre:
                encontrados.append(nodo)

        return encontrados

    def lineas_arbol(self):
        if self.raiz is None:
            return ["Árbol vacío."]

        lineas = [str(self.raiz)]

        def recorrer(nodo, prefijo):
            total_hijos = len(nodo.hijos)

            for indice, hijo in enumerate(nodo.hijos):
                es_ultimo = indice == total_hijos - 1

                conector = "└── " if es_ultimo else "├── "
                lineas.append(prefijo + conector + str(hijo))

                nuevo_prefijo = prefijo + ("    " if es_ultimo else "│   ")
                recorrer(hijo, nuevo_prefijo)

        recorrer(self.raiz, "")

        return lineas

    def orden(self):
        return len(self.nodos_por_id)

    def grado_arbol(self):
        if self.raiz is None:
            return 0

        mayor_grado = 0

        for nodo in self.nodos_por_id.values():
            if nodo.grado() > mayor_grado:
                mayor_grado = nodo.grado()

        return mayor_grado

    def altura(self):
        if self.raiz is None:
            return -1

        def calcular_altura(nodo):
            if len(nodo.hijos) == 0:
                return 0

            alturas_hijos = []

            for hijo in nodo.hijos:
                alturas_hijos.append(calcular_altura(hijo))

            return 1 + max(alturas_hijos)

        return calcular_altura(self.raiz)

    def grados_por_nodo(self):
        grados = []

        for nodo in self.recorrido_preorden():
            grados.append({"id": nodo.id, "nombre": nodo.nombre, "tipo": nodo.tipo, "ruta": nodo.ruta(), "grado": nodo.grado()})

        return grados

    def recorrido_preorden(self):
        resultado = []

        def recorrer(nodo):
            resultado.append(nodo)

            for hijo in nodo.hijos:
                recorrer(hijo)

        if self.raiz is not None:
            recorrer(self.raiz)

        return resultado

    def recorrido_postorden(self):
        resultado = []

        def recorrer(nodo):
            for hijo in nodo.hijos:
                recorrer(hijo)

            resultado.append(nodo)

        if self.raiz is not None:
            recorrer(self.raiz)

        return resultado

    def recorrido_por_niveles(self):
        if self.raiz is None:
            return []

        resultado = []
        cola = deque()

        cola.append((self.raiz, 0))

        while len(cola) > 0:
            nodo, nivel = cola.popleft()

            resultado.append({"nodo": nodo, "nivel": nivel})

            for hijo in nodo.hijos:
                cola.append((hijo, nivel + 1))

        return resultado

    def subarbol_postorden(self, nodo):
        resultado = []

        def recorrer(actual):
            for hijo in actual.hijos:
                recorrer(hijo)

            resultado.append(actual)

        if nodo is not None:
            recorrer(nodo)

        return resultado

    def respaldar_eliminacion(self, nodo):
        if nodo is None:
            return []

        respaldados = []
        nodos_a_respaldar = self.subarbol_postorden(nodo)

        for actual in nodos_a_respaldar:
            datos = {"id": actual.id, "nombre": actual.nombre, "tipo": actual.tipo, "area": actual.area, "subarea": actual.subarea, "ruta": actual.ruta(), "grado": actual.grado()}

            self.respaldo_eliminados.append(datos)
            respaldados.append(datos)

        return respaldados



    def eliminar_con_respaldo(self, nodo):
        if nodo is None:
            return False, "El nodo no existe"

        if self.raiz is None:
            return False, "El árbol está vacío"

        if nodo == self.raiz:
            return False, "No se puede eliminar la raíz del árbol"

        if nodo.padre is None:
            return False, "El nodo no tiene padre"

        respaldados = self.respaldar_eliminacion(nodo)
        nodos_a_eliminar = self.subarbol_postorden(nodo)

        for actual in nodos_a_eliminar:
            if actual.padre is not None:
                actual.padre.quitar_hijo(actual)

            actual.hijos = []

        self.reconstruir_indices()

        return True, (
            f"Se eliminó '{nodo.nombre}' con respaldo previo. "
            f"Elementos respaldados y eliminados: {len(respaldados)}."
        )