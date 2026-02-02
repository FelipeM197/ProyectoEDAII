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
        ALGORITMO RECURSIVO CON LOGS DE DEPURACIÓN
        """
        # CASO BASE: Si es hoja, imprimimos el resultado final y retornamos
        if nodo_actual.es_hoja():
            res = nodo_actual.resultado_base
            print(f"   └── [HOJA LLEGADA]: {nodo_actual.nombre} -> {res[0]} (Mult: {res[2]})")
            print("-" * 40)
            return res
        
        # Tiramos el dado (número entre 0.0 y 1.0)
        roll = random.random()
        
        # DEBUG: Imprimir qué está pasando
        print(f"[ÁRBOL] Pregunta: '{nodo_actual.nombre}'")
        print(f"        Probabilidad necesaria: <= {nodo_actual.valor_probabilidad}")
        print(f"        Dado obtenido: {roll:.3f}")
        
        # Decidimos a dónde ir
        if roll <= nodo_actual.valor_probabilidad:
            print("        Respuesta: SÍ -> Rama Izquierda")
            return self.recorrer(nodo_actual.izquierda)
        else:
            print("        Respuesta: NO -> Rama Derecha")
            return self.recorrer(nodo_actual.derecha)

    @staticmethod
    def ejecutar_ataque(atacante_atk):
        print("\n" + "="*40)
        print(" INICIANDO CÁLCULO DE ÁRBOL DE DECISIÓN")
        print("="*40)
        
        arbol = ArbolAtaque()
        
        # Recorremos el árbol (esto imprimirá los logs anteriores)
        resultado_tupla = arbol.recorrer(arbol.raiz)
        
        # Desempaquetamos la tupla manualmente
        tipo = resultado_tupla[0]
        mensaje = resultado_tupla[1]
        valor = resultado_tupla[2]
        
        # Calculamos daño final
        if tipo == "TROPIEZO":
            dano_final = valor
        elif tipo == "FALLO":
            dano_final = 0
        else:
            dano_final = int(atacante_atk * valor)

        return ResultadoAtaque(
            tipo, 
            mensaje, 
            multiplicador_dano=valor if tipo not in ["TROPIEZO", "FALLO"] else 0,
            dano_fijo=valor if tipo == "TROPIEZO" else 0,
            dano_real=dano_final
        )

# ==========================================
# ESTRUCTURA 2: GRAFO DIRIGIDO
# ==========================================
# ==========================================
# ESTRUCTURA 2: GRAFO DIRIGIDO
# ==========================================
class GrafoEfectos:
    def __init__(self):
        self.lista_adyacencia = {}
        self.construir_grafo_juego()

    def agregar_vertice(self, estado):
        if estado not in self.lista_adyacencia:
            self.lista_adyacencia[estado] = {}

    def agregar_arista(self, origen, evento, destino):
        self.agregar_vertice(origen)
        self.agregar_vertice(destino)
        self.lista_adyacencia[origen][evento] = destino

    def construir_grafo_juego(self):
        """
        Define la topología del grafo.
        [MEJORA]: Ahora permitimos cambiar de un estado alterado a otro.
        """
        # 1. Desde NORMAL (Lo que ya tenías)
        self.agregar_arista("Normal", "fuego", "Quemado")
        self.agregar_arista("Normal", "cuchillo", "Sangrado")
        self.agregar_arista("Normal", "insulto", "Aturdido")
        self.agregar_arista("Normal", "defensa", "Escudo")

        # 2. INTERCONEXIONES (Lo que faltaba)
        # Si está Quemado y le pegan con Cuchillo -> Pasa a Sangrado
        self.agregar_arista("Quemado", "cuchillo", "Sangrado")
        self.agregar_arista("Quemado", "insulto", "Aturdido")
        
        # Si está Sangrando y le tiran Fuego -> Pasa a Quemado
        self.agregar_arista("Sangrado", "fuego", "Quemado")
        self.agregar_arista("Sangrado", "insulto", "Aturdido")

        # Si está Aturdido, cualquier golpe fuerte lo despierta o cambia estado
        self.agregar_arista("Aturdido", "fuego", "Quemado")
        self.agregar_arista("Aturdido", "cuchillo", "Sangrado")

        # 3. SALIDAS (Curaciones y Fin de efecto)
        # La palabra clave "cura" limpia cualquier estado malo
        self.agregar_arista("Quemado", "cura", "Normal")
        self.agregar_arista("Sangrado", "cura", "Normal")
        self.agregar_arista("Aturdido", "cura", "Normal")
        
        # El escudo se rompe o se acaba
        self.agregar_arista("Escudo", "romper", "Normal")

    def transicion(self, estado_actual, evento):
        """
        Recorre el grafo y retorna el nuevo estado.
        [DEBUG]: Imprime en consola qué está pasando.
        """
        nuevo_estado = estado_actual
        
        if estado_actual in self.lista_adyacencia:
            adyacentes = self.lista_adyacencia[estado_actual]
            if evento in adyacentes:
                nuevo_estado = adyacentes[evento]
        
        # LOG EN CONSOLA (Lo que pediste)
        if nuevo_estado != estado_actual:
            print(f"[GRAFO] Transición: {estado_actual} + [{evento}] ---> {nuevo_estado}")
        else:
            print(f"[GRAFO] Intento fallido: {estado_actual} + [{evento}] (No hay arista)")
            
        return nuevo_estado