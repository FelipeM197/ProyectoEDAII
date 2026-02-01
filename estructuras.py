import random
import config

"""
ESTRUCTURAS DE DATOS LÓGICAS
---------------------------------------------------
Este archivo contiene la lógica matemática y de decisiones del proyecto.
Se implementan dos Estructuras de Datos No Lineales:

1. ÁRBOL BINARIO DE DECISIÓN: 
   - Se usa para calcular si un ataque acierta, es crítico o falla.
   - Es "Binario" porque cada decisión tiene solo 2 caminos (Sí o No).

2. GRAFO DIRIGIDO (MÁQUINA DE ESTADOS):
   - Se usa para controlar los estados del personaje (Normal -> Quemado -> Curado).
   - Es un "Grafo" porque los estados son nodos conectados por flechas (eventos).
"""

# ==========================================
# CLASE AUXILIAR: PAQUETE DE DATOS
# ==========================================
class ResultadoAtaque:
    """
    Esta clase es solo una 'caja' o 'sobre' para transportar información.
    Cuando el Árbol termina de pensar, devuelve un objeto de este tipo.
    """
    def __init__(self, tipo, mensaje, dano_total):
        self.tipo = tipo            # Ej: "CRITICO", "FALLO", "NORMAL", "TROPIEZO"
        self.mensaje = mensaje      # El texto que sale en la pantalla.
        
        # [IMPORTANTE]: La variable se llama 'dano' porque main.py la busca con ese nombre exacto.
        # Si le cambian el nombre aquí, el juego se romperá.
        self.dano = dano_total      

# ==========================================
# ESTRUCTURA 1: ÁRBOL BINARIO
# ==========================================
class NodoDecision:
    """
    Representa un punto en el diagrama de flujo (un círculo en el dibujo del árbol).
    """
    def __init__(self, nombre, probabilidad_limite=None, resultado_base=None):
        self.nombre = nombre
        
        # Valor entre 0.0 y 1.0. Si el dado saca menos que esto, vamos a la IZQUIERDA.
        self.valor_probabilidad = probabilidad_limite 
        
        # Punteros: Conectan este nodo con los siguientes (las ramas).
        self.izquierda = None  # Camino del ÉXITO (Se cumple la probabilidad)
        self.derecha = None    # Camino del FALLO (No se cumple)
        
        # Si el nodo es el final del camino (Hoja), guardamos aquí qué pasa (daño, mensaje).
        self.resultado_base = resultado_base 

    def es_hoja(self):
        """Devuelve True si este nodo no tiene hijos (es el final del camino)."""
        return self.izquierda is None and self.derecha is None

class ArbolAtaque:
    """
    La clase que ensambla y recorre el Árbol.
    """
    def __init__(self):
        # Al crear la clase, construimos el mapa de decisiones automáticamente.
        self.raiz = self.construir_arbol()

    def construir_arbol(self):
        """
        [MODIFICACIÓN]: Aquí se 'cablea' la lógica del combate.
        Si quieren agregar una nueva posibilidad (ej: 'Golpe Divino'), deben crear
        un nuevo NodoDecision y conectarlo aquí.
        """
        # --- 1. CREAR LAS HOJAS (Los finales posibles) ---
        # config.MULT_CRITICO viene de config.py
        
        hoja_critico = NodoDecision("Crítico", 
                                    resultado_base=("CRITICO", "¡GOLPE CRÍTICO!", config.MULT_CRITICO))
        
        hoja_normal = NodoDecision("Normal", 
                                   resultado_base=("NORMAL", "Ataque Efectivo", 1.0)) # 1.0 = Daño normal
        
        hoja_tropiezo = NodoDecision("Tropiezo", 
                                     resultado_base=("TROPIEZO", "¡Te lastimaste!", config.DANO_TROPIEZO))
        
        hoja_nada = NodoDecision("Nada", 
                                 resultado_base=("FALLO", "Fallaste.", 0)) # 0 de daño

        # --- 2. CREAR LAS RAMAS (Las preguntas intermedias) ---
        
        # Pregunta A: Si acertó el golpe, ¿es tan bueno que es crítico?
        nodo_tipo_exito = NodoDecision("Es Crítico?", probabilidad_limite=config.PROB_CRITICO)
        nodo_tipo_exito.izquierda = hoja_critico  # Si sí -> Crítico
        nodo_tipo_exito.derecha = hoja_normal     # Si no -> Normal

        # Pregunta B: Si falló el golpe, ¿fue tan malo que se tropezó?
        nodo_tipo_fallo = NodoDecision("Es Tropiezo?", probabilidad_limite=config.PROB_TROPIEZO)
        nodo_tipo_fallo.izquierda = hoja_tropiezo # Si sí -> Daño a uno mismo
        nodo_tipo_fallo.derecha = hoja_nada       # Si no -> Solo falló

        # --- 3. CREAR LA RAÍZ (La primera pregunta) ---
        # Pregunta Principal: ¿El ataque conecta con el enemigo?
        raiz = NodoDecision("Acierta?", probabilidad_limite=config.PROB_ACIERTO)
        raiz.izquierda = nodo_tipo_exito # Vamos a la rama de éxitos
        raiz.derecha = nodo_tipo_fallo   # Vamos a la rama de fallos

        return raiz

    def recorrer(self, nodo_actual):
        """
        ALGORITMO RECURSIVO:
        Esta función se llama a sí misma para bajar por el árbol hasta encontrar una hoja.
        """
        # CASO BASE: Si llegamos al final, devolvemos el resultado.
        if nodo_actual.es_hoja():
            return nodo_actual.resultado_base
        
        # Tiramos el dado (número entre 0.0 y 1.0)
        roll = random.random() 
        
        # Decidimos a dónde ir
        if roll <= nodo_actual.valor_probabilidad:
            return self.recorrer(nodo_actual.izquierda)
        else:
            return self.recorrer(nodo_actual.derecha)

    @staticmethod
    def ejecutar_ataque(atacante_atk):
        """
        Esta es la función que llama el main.py.
        1. Crea el árbol.
        2. Lo recorre para obtener un resultado.
        3. Calcula el número final de daño.
        """
        arbol = ArbolAtaque()
        tipo, mensaje, valor = arbol.recorrer(arbol.raiz)
        
        # --- LÓGICA MATEMÁTICA DE DAÑO ---
        if tipo == "TROPIEZO":
            dano_final = valor # En tropiezo, el valor es daño fijo (ej: 10)
        elif tipo == "FALLO":
            dano_final = 0
        else:
            # En Normal o Crítico, el valor es un multiplicador (ej: 1.5)
            # Formula: Ataque Base * Multiplicador
            dano_final = int(atacante_atk * valor)
        
        # Empaquetamos todo en el objeto ResultadoAtaque
        return ResultadoAtaque(tipo, mensaje, dano_final)

# ==========================================
# ESTRUCTURA 2: GRAFO DIRIGIDO
# ==========================================
class GrafoEfectos:
    """
    Controla cómo cambian los estados de los personajes.
    Estructura: Lista de Adyacencia (Diccionario de Diccionarios).
    """
    def __init__(self):
        # [MODIFICACIÓN]: Si quieren agregar un nuevo estado (ej: "Congelado"),
        # agréguenlo como una clave nueva en este diccionario.
        self.nodos = {
            # ESTADO ACTUAL : { CAUSA -> ESTADO SIGUIENTE }
            "Normal": {
                "fuego": "Quemado", 
                "cuchillo": "Sangrado", 
                "defensa": "Escudo",
                "motivacion": "Motivado",
                "insulto": "Aturdido",
                "critico_recibido": "Vulnerable",
                "migra": "Deportado" 
            },
            # Definimos cómo salir de los estados alterados
            "Quemado": {"cura": "Curado", "fin_turno": "Normal"},
            "Sangrado": {"cura": "Curado", "fin_turno": "Normal"},
            "Escudo": {"romper": "Normal", "fin_turno": "Normal"},
            "Motivado": {"fin_turno": "Normal"},
            "Aturdido": {"fin_turno": "Normal"},
            "Vulnerable": {"recibir_golpe": "Normal"},
            "Deportado": {"fin_turno": "Normal"},
            "Curado": {"listo": "Normal"}
        }

    def transicion(self, estado_actual, evento):
        """
        Intenta mover al personaje de un estado a otro.
        Si el evento no existe para el estado actual, se queda igual.
        """
        # .get(evento, estado_actual) significa: 
        # "Busca el evento, si no existe, devuélveme el estado donde ya estaba".
        return self.nodos.get(estado_actual, {}).get(evento, estado_actual)