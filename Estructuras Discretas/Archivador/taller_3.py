from collections import deque # Para recorrer por niveles el arbol
import pandas as pd # Para que leamos el excel

class Nodo:
    '''
        La idea es que esta es la clase que guarde la info de los
        metadatos del excel
    '''
    def __init__(self, nombre, tipo, area, subarea, id):
        self.nombre = nombre
        self.tipo = tipo
        self.area = area
        self.subarea = subarea
        self.id = id
        self.hijos = []
    
    def agregar_hijo(self, nodo):
        self.hijos.append(nodo)

    def grado(self):
        return len(self.hijos)

    def es_hoja(self):
        if len(self.hijos) == 0:
            return True
        return False

    def __str__(self):
        return f"{self.nombre} ({self.tipo})"
    

class Arbol:
    '''
        La idea es que esta sea la clase que guarde los
        nodos, los almacene y sea el encargado de la organizacion
    '''
    def __init__(self, raiz):
        self.raiz = raiz

    # Formato tipo linux
    def mostrar_arbol(self, nodo=None, nivel=0):
        if nodo is None:
            nodo = self.raiz

        sangria = "    " * nivel
        print(f"{sangria}- {nodo.nombre} [{nodo.tipo}]")

        for hijo in nodo.hijos:
            self.mostrar_arbol(hijo, nivel + 1)

    def preorden(self, nodo=None, resultado=None):
        if resultado is None:
            resultado = []

        if nodo is None:
            nodo = self.raiz

        resultado.append(nodo.nombre)

        for hijo in nodo.hijos:
            self.preorden(hijo, resultado)

        return resultado

    def postorden(self, nodo=None, resultado=None):
        if resultado is None:
            resultado = []

        if nodo is None:
            nodo = self.raiz

        for hijo in nodo.hijos:
            self.postorden(hijo, resultado)

        resultado.append(nodo.nombre)

        return resultado

    def recorrido_por_niveles(self):
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

if __name__ == '__main__':
    nombre_archivo = ''