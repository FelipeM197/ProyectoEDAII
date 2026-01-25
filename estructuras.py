import random
import config

"""
ESTRUCTURAS DE DATOS 
----------------------------------------------
Archivo donde irán todos los grafos y arboles del proyecto
GUÍA:
1. Clase NodoDecision (La estructura del árbol) ........ Línea 26
2. Construcción del Árbol (Armado manual) .............. Línea 58
3. Recorrido del Árbol (La lógica de paso) ............. Línea 105
"""

class ResultadoAtaque:
    # Es la hoja final que devuelve el árbol. Se encarga del transporte de datos
    def __init__(self, tipo, mensaje, multiplicador_dano=1.0, dano_fijo=0):
        self.tipo = tipo        # "EXITO", "CRITICO", "FALLO", "TROPIEZO"
        self.mensaje = mensaje
        self.multiplicador = multiplicador_dano
        self.dano_fijo = dano_fijo

class NodoDecision:
    def __init__(self, nombre, probabilidad_limite=None, resultado=None):
        self.nombre = nombre
        self.valor_probabilidad = probabilidad_limite # ej: 0.8
        
        self.izquierda = None  # Camino SI (Se cumple la probabilidad)
        self.derecha = None    # Camino NO (No se cumple)
        
        # Si es un nodo hoja, tendrá un resultado; si es rama, será None.
        self.resultado = resultado 

    def es_hoja(self):
        return self.izquierda is None and self.derecha is None

class ArbolAtaque:
    #Se encarga de recorrer el arbol
    def __init__(self):
        self.raiz = self.construir_arbol()

    def construir_arbol(self):
        """
        Arma el árbol conectando los nodos manualmente según el diagrama.
        """
        # Resultados finales (hojas)
        # Rama Éxito
        hoja_critico = NodoDecision("Crítico", 
                                    resultado=ResultadoAtaque("CRITICO", "¡GOLPE CRÍTICO!", 
                                                              config.MULT_CRITICO, 0))
        hoja_normal = NodoDecision("Normal", 
                                   resultado=ResultadoAtaque("NORMAL", "Ataque Efectivo", 
                                                             1.0, 0))
        
        # Rama Fallo
        hoja_tropiezo = NodoDecision("Tropiezo", 
                                     resultado=ResultadoAtaque("TROPIEZO", 
                                                               "¡Te lastimaste!", 0, config.DANO_TROPIEZO))
        #se les pasa 0 en el ataque ya que eso tendra que ver con el tipo de personaje y el multuplicador
        hoja_nada = NodoDecision("Nada", 
                                 resultado=ResultadoAtaque("FALLO", "Fallaste.", 0, 0))

        
        # Izquierda: Decisión Es Crítico? (0.3)
        nodo_tipo_exito = NodoDecision("Es Crítico?", probabilidad_limite=config.PROB_CRITICO)
        nodo_tipo_exito.izquierda = hoja_critico  # Si random <= 0.3 -> Crítico
        nodo_tipo_exito.derecha = hoja_normal     # Si random > 0.3 -> Normal

        # Derecho: Decisión Es Tropiezo? (0.1)
        nodo_tipo_fallo = NodoDecision("Es Tropiezo?", probabilidad_limite=config.PROB_TROPIEZO)
        nodo_tipo_fallo.izquierda = hoja_tropiezo # Si random <= 0.1 -> Tropiezo
        nodo_tipo_fallo.derecha = hoja_nada       # Si random > 0.1 -> Nada

        # Decisión Principal: Acierta el golpe? (0.8)
        #llama al archivo config que contiene todos los datos de probabilidad
        raiz = NodoDecision("Acierta?", probabilidad_limite=config.PROB_ACIERTO)
        raiz.izquierda = nodo_tipo_exito # Si random <= 0.8 -> Vamos a sub-arbol éxito
        raiz.derecha = nodo_tipo_fallo   # Si random > 0.8 -> Vamos a sub-arbol fallo

        return raiz
    
    """Para crear una rama que salga desde la raiz:
    rama.izquierda o rama.derecha
    para crear una hoja:
    nodo_tipo_exito.izquierda o .derecha
    a las hojas debes darles un valor desde la 
    clase porque son las que entregaran el resultado final

    """

    def recorrer(self, nodo_actual):
        """
        Función recursiva para navegar por los punteros self.izquierda/derecha.
        """
        # Si es hoja, devolvemos el resultado almacenado
        if nodo_actual.es_hoja():
            return nodo_actual.resultado
        
        #Tiramos el dado y decidimos a qué hijo ir
        roll = random.random()
        
        # Si el número es menor/igual a la probabilidad, vamos a la izquierda
        if roll <= nodo_actual.valor_probabilidad:
            return self.recorrer(nodo_actual.izquierda)
        else:
            return self.recorrer(nodo_actual.derecha)

    @staticmethod
    def ejecutar_ataque(atacante_atk):
        arbol = ArbolAtaque()
        resultado_hoja = arbol.recorrer(arbol.raiz)
        
        # Aplicamos el multiplicador
        dano_final = int(atacante_atk * resultado_hoja.multiplicador)
        
        # Devolvemos un objeto simple con el daño ya calculado
        return ResultadoAtaque(
            resultado_hoja.tipo, 
            resultado_hoja.mensaje, 
            dano_final, 
            resultado_hoja.dano_fijo
        )