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
    # Es la hoja final que devuelve el árbol. Se encarga del transporte de datos.
    def __init__(self, tipo, mensaje, multiplicador_dano=1.0, dano_fijo=0, dano_real=0):
        self.tipo = tipo        # "EXITO", "CRITICO", "FALLO", "TROPIEZO"
        self.mensaje = mensaje
        self.multiplicador = multiplicador_dano
        self.dano_fijo = dano_fijo
        
        # Esta es la variable vital que main.py necesita leer:
        self.dano = dano_real

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
        arbol = ArbolAtaque()
        
        # Aquí recibimos la TUPLA del árbol (Tipo, Mensaje, Valor)
        resultado_tupla = arbol.recorrer(arbol.raiz)
        
        # Desempaquetamos la tupla manualmente para no confundir al programa
        tipo = resultado_tupla[0]
        mensaje = resultado_tupla[1]
        valor = resultado_tupla[2] # Puede ser multiplicador (1.5) o daño fijo (10)
        
        # 1. Calculamos el daño final según el tipo
        if tipo == "TROPIEZO":
            dano_final = valor # En tropiezo, el valor es el daño fijo
        elif tipo == "FALLO":
            dano_final = 0
        else:
            # En Normal o Crítico, el valor es un multiplicador
            dano_final = int(atacante_atk * valor)

        # Devolvemos el objeto final pasando el 'dano_final' al campo correcto
        return ResultadoAtaque(
            tipo, 
            mensaje, 
            multiplicador_dano=valor if tipo not in ["TROPIEZO", "FALLO"] else 0,
            dano_fijo=valor if tipo == "TROPIEZO" else 0,
            dano_real=dano_final # [COHERENCIA]: Aquí guardamos el daño final para main.py
        )

# ==========================================
# ESTRUCTURA 2: GRAFO DIRIGIDO
# ==========================================
class GrafoEfectos:
    """
    Implementación de un Grafo Dirigido utilizando Listas de Adyacencia.
    Cada vértice representa un estado y cada arista representa una transición disparada por un evento.
    """
    def __init__(self):
        # Estructura principal: Diccionario donde la clave es el vértice origen
        # y el valor es otro diccionario con las aristas {evento: vértice_destino}
        self.lista_adyacencia = {}
        
        # Construcción inicial de la lógica del juego
        self.construir_grafo_juego()

    def agregar_vertice(self, estado):
        """
        Inserta un nuevo vértice (estado) en el grafo si no existe.
        """
        if estado not in self.lista_adyacencia:
            self.lista_adyacencia[estado] = {}

    def agregar_arista(self, origen, evento, destino):
        """
        Crea una arista dirigida desde el vértice 'origen' hacia 'destino',
        etiquetada con el 'evento' que dispara la transición.
        """
        # Aseguramos que los vértices existan antes de conectar
        self.agregar_vertice(origen)
        self.agregar_vertice(destino)
        
        # Inserción de la arista en la lista de adyacencia
        self.lista_adyacencia[origen][evento] = destino

    def construir_grafo_juego(self):
        """
        Define la topología del grafo específica para la lógica de combate.
        Se crean los nodos y las conexiones manualmente.
        """
        # Transiciones desde el estado base "Normal"
        self.agregar_arista("Normal", "fuego", "Quemado")
        self.agregar_arista("Normal", "cuchillo", "Sangrado")
        self.agregar_arista("Normal", "defensa", "Escudo")
        self.agregar_arista("Normal", "motivacion", "Motivado")
        self.agregar_arista("Normal", "insulto", "Aturdido")
        self.agregar_arista("Normal", "critico_recibido", "Vulnerable")
        self.agregar_arista("Normal", "migra", "Deportado")

        # Transiciones de recuperación (Vuelta a la normalidad o cura)
        self.agregar_arista("Quemado", "cura", "Curado")
        self.agregar_arista("Quemado", "fin_turno", "Normal")
        
        self.agregar_arista("Sangrado", "cura", "Curado")
        self.agregar_arista("Sangrado", "fin_turno", "Normal")
        
        self.agregar_arista("Escudo", "romper", "Normal")
        self.agregar_arista("Escudo", "fin_turno", "Normal")
        
        self.agregar_arista("Motivado", "fin_turno", "Normal")
        self.agregar_arista("Aturdido", "fin_turno", "Normal")
        self.agregar_arista("Vulnerable", "recibir_golpe", "Normal")
        self.agregar_arista("Deportado", "fin_turno", "Normal")
        
        self.agregar_arista("Curado", "listo", "Normal")

    def transicion(self, estado_actual, evento):
        """
        Recorre el grafo buscando una arista válida para el estado y evento dados.
        Si existe la conexión, retorna el nuevo estado; de lo contrario, mantiene el actual.
        """
        # Búsqueda en la lista de adyacencia
        if estado_actual in self.lista_adyacencia:
            adyacentes = self.lista_adyacencia[estado_actual]
            if evento in adyacentes:
                return adyacentes[evento]
        
        # Si no hay transición definida, se permanece en el mismo vértice
        return estado_actual