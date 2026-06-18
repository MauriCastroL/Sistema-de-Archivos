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
    