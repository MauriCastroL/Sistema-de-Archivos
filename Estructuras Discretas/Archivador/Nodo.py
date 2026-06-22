class Nodo:
    def __init__(self, id_nodo, nombre, tipo, area="", subarea=""):
        self.id = str(id_nodo).strip()
        self.nombre = str(nombre).strip()
        self.tipo = self.limpiar_tipo(tipo)
        self.area = str(area).strip()
        self.subarea = str(subarea).strip()

        self.padre = None
        self.hijos = []

    def limpiar_tipo(self, tipo):
        tipo = str(tipo).strip().lower()

        if tipo == "carpeta":
            return "Carpeta"

        if tipo == "archivo":
            return "Archivo"

        raise ValueError("El tipo del nodo deber ser Archivo o Carpeta")

    def agregar_hijo(self, nodo_hijo):
        if self.tipo == "Archivo":
            raise ValueError("Un archivo no puede tener hijos.")

        if self.tiene_hijo_con_nombre(nodo_hijo.nombre):
            raise ValueError(f"Ya existe un nodo llamado '{nodo_hijo.nombre}' dentro de '{self.nombre}'.")

        nodo_hijo.padre = self
        self.hijos.append(nodo_hijo)
 
    def quitar_hijo(self, nodo_hijo):
        if nodo_hijo in self.hijos:
            self.hijos.remove(nodo_hijo)
            nodo_hijo.padre = None 
            return True

        return False
 
    def grado(self):
        return len(self.hijos)
 
    def ruta(self):
        partes = []
        actual = self

        while actual is not None:
            partes.append(actual.nombre)
            actual = actual.padre

        partes.reverse()
        return "/".join(partes)
 
    def tiene_hijo_con_nombre(self, nombre):
        nombre = str(nombre).strip().lower()

        for hijo in self.hijos:
            if hijo.nombre.strip().lower() == nombre:
                return True

        return False
 
    def obtener_hijo_por_nombre(self, nombre):
        nombre = str(nombre).strip().lower()

        for hijo in self.hijos:
            if hijo.nombre.strip().lower() == nombre:
                return hijo

        return None

    def __str__(self):
        return f"[{self.id}] {self.nombre} ({self.tipo})"