import random
import config

"""
LÓGICA MATEMÁTICA Y DE DECISIONES
---------------------------------
Este módulo actúa como el cerebro del juego. Aquí no dibujamos nada en pantalla,
sino que procesamos los números y las reglas que definen qué sucede.

Implementamos dos modelos lógicos principales:
1. Un árbol de decisión probabilístico para calcular el resultado de los ataques.
2. Un grafo dirigido (máquina de estados) para gestionar los efectos de estado.

INDICE RÁPIDO:
--------------
Línea 25 -> Clase ResultadoAtaque (Paquete de datos)
Línea 40 -> Nodos del Árbol de Decisión
Línea 65 -> Clase ArbolAtaque (Lógica de combate)
Línea 145 -> Clase GrafoEfectos (Máquina de estados)
"""

# ==========================================
# PAQUETE DE DATOS AUXILIAR
# ==========================================
class ResultadoAtaque:
    """
    Esta clase funciona como un contenedor de datos (Data Transfer Object).
    
    Cuando el árbol de decisión termina de pensar, necesitamos una forma limpia
    de enviar toda la información (daño, mensajes, tipo de golpe) de vuelta
    al bucle principal del juego sin pasar múltiples variables sueltas.
    """
    def __init__(self, tipo, mensaje, multiplicador_dano=1.0, dano_fijo=0, dano_real=0):
        self.tipo = tipo        # Categoría del resultado (ej. critico, fallo).
        self.mensaje = mensaje  # Texto que verá el usuario.
        self.multiplicador = multiplicador_dano
        self.dano_fijo = dano_fijo
        
        # Este es el valor final calculado que se restará de la vida del objetivo.
        self.dano = dano_real

# ==========================================
# LÓGICA DE COMBATE (ÁRBOL DE PROBABILIDAD)
# ==========================================
class NodoDecision:
    """
    Representa un punto de bifurcación en nuestro diagrama de flujo lógico.
    Cada nodo plantea una pregunta basada en probabilidades (ej. ¿Acertó?).
    """
    def __init__(self, nombre, probabilidad_limite=None, resultado_base=None):
        self.nombre = nombre
        
        # Umbral de decisión (0.0 a 1.0).
        # Si el número aleatorio generado es menor a este valor, tomamos el camino izquierdo.
        self.valor_probabilidad = probabilidad_limite 
        
        # Enlaces a los siguientes nodos (las ramas del árbol).
        self.izquierda = None  # Camino afirmativo / éxito.
        self.derecha = None    # Camino negativo / fallo.
        
        # Si este nodo es una hoja (final del camino), aquí guardamos el resultado.
        self.resultado_base = resultado_base 

    def es_hoja(self):
        """
        Nos dice si hemos llegado al final de una rama y ya tenemos un resultado.
        """
        return self.izquierda is None and self.derecha is None

class ArbolAtaque:
    """
    Esta clase gestiona la lógica de 'suerte' del combate.
    Construye y recorre un árbol binario donde cada nivel es una tirada de dados.
    """
    def __init__(self):
        # Al instanciar la clase, armamos la estructura del árbol en memoria.
        self.raiz = self.construir_arbol()

    def construir_arbol(self):
        """
        Aquí definimos la topología del árbol. Es donde 'cableamos' las reglas del juego.
        Conectamos nodos de decisión con nodos hoja (resultados finales).
        """
        # 1. Definición de los resultados posibles (Hojas del árbol)
        # Estos son los puntos finales a los que queremos llegar.
        
        hoja_critico = NodoDecision("Crítico", 
                                    resultado_base=("CRITICO", "¡GOLPE CRÍTICO!", config.MULT_CRITICO))
        
        hoja_normal = NodoDecision("Normal", 
                                   resultado_base=("NORMAL", "Ataque Efectivo", 1.0)) # 1.0 = 100% del daño base
        
        hoja_tropiezo = NodoDecision("Tropiezo", 
                                     resultado_base=("TROPIEZO", "¡Te lastimaste!", config.DANO_TROPIEZO))
        
        hoja_nada = NodoDecision("Nada", 
                                 resultado_base=("FALLO", "Fallaste.", 0)) # 0 daño
        
        # 2. Construcción de las ramas intermedias (Nodos de decisión)
        
        # Rama del éxito: Si ya acertamos, verificamos si es un golpe crítico.
        nodo_tipo_exito = NodoDecision("Es Crítico?", probabilidad_limite=config.PROB_CRITICO)
        nodo_tipo_exito.izquierda = hoja_critico  
        nodo_tipo_exito.derecha = hoja_normal     

        # Rama del fallo: Si fallamos, verificamos si fue un error catastrófico (tropiezo).
        nodo_tipo_fallo = NodoDecision("Es Tropiezo?", probabilidad_limite=config.PROB_TROPIEZO)
        nodo_tipo_fallo.izquierda = hoja_tropiezo 
        nodo_tipo_fallo.derecha = hoja_nada       

        # 3. Nodo Raíz (El inicio de todo)
        # La primera pregunta es simplemente: ¿Logramos conectar el golpe?
        raiz = NodoDecision("Acierta?", probabilidad_limite=config.PROB_ACIERTO)
        raiz.izquierda = nodo_tipo_exito # Si sí, vamos a evaluar si es crítico.
        raiz.derecha = nodo_tipo_fallo   # Si no, vamos a evaluar si nos tropezamos.

        return raiz

    def recorrer(self, nodo_actual):
        """
        Algoritmo recursivo para navegar el árbol.
        Se llama a sí mismo descendiendo por las ramas hasta encontrar una hoja.
        """
        # Caso base: Si el nodo no tiene hijos, es una hoja. Devolvemos el resultado.
        if nodo_actual.es_hoja():
            res = nodo_actual.resultado_base
            print(f"   └── [HOJA LLEGADA]: {nodo_actual.nombre} -> {res[0]} (Mult: {res[2]})")
            print("-" * 40)
            return res
        
        # Generamos un número aleatorio entre 0.0 y 1.0 (nuestro 'dado').
        roll = random.random()
        
        # Imprimimos trazas para poder depurar la lógica en la consola.
        print(f"[ÁRBOL] Pregunta: '{nodo_actual.nombre}'")
        print(f"        Probabilidad necesaria: <= {nodo_actual.valor_probabilidad}")
        print(f"        Dado obtenido: {roll:.3f}")
        
        # Lógica de bifurcación: Comparamos el dado con la probabilidad del nodo.
        if roll <= nodo_actual.valor_probabilidad:
            print("        Respuesta: SÍ -> Rama Izquierda")
            return self.recorrer(nodo_actual.izquierda)
        else:
            print("        Respuesta: NO -> Rama Derecha")
            return self.recorrer(nodo_actual.derecha)

    @staticmethod
    def ejecutar_ataque(atacante_atk):
        """
        Método estático de fachada. Simplifica el uso del árbol para el resto del código.
        Instancia el árbol, lo recorre y empaqueta el resultado final.
        """
        print("\n" + "="*40)
        print(" INICIANDO CÁLCULO DE ÁRBOL DE DECISIÓN")
        print("="*40)
        
        arbol = ArbolAtaque()
        
        # Iniciamos la recursión desde la raíz.
        resultado_tupla = arbol.recorrer(arbol.raiz)
        
        # Desempaquetamos la tupla cruda que devuelve el nodo hoja.
        tipo = resultado_tupla[0]
        mensaje = resultado_tupla[1]
        valor = resultado_tupla[2]
        
        # Calculamos el daño numérico final basado en el tipo de resultado.
        if tipo == "TROPIEZO":
            dano_final = valor # En tropiezo, el valor es daño fijo autoinfligido.
        elif tipo == "FALLO":
            dano_final = 0
        else:
            # En éxito o crítico, el valor es un multiplicador (ej. 1.0 o 1.5).
            dano_final = int(atacante_atk * valor)

        # Retornamos el objeto limpio y estructurado.
        return ResultadoAtaque(
            tipo, 
            mensaje, 
            multiplicador_dano=valor if tipo not in ["TROPIEZO", "FALLO"] else 0,
            dano_fijo=valor if tipo == "TROPIEZO" else 0,
            dano_real=dano_final
        )

# ==========================================
# MÁQUINA DE ESTADOS (GRAFO)
# ==========================================
class GrafoEfectos:
    """
    Controla cómo los personajes cambian de estado (ej. de Normal a Quemado)
    basándose en eventos (ataques recibidos).
    """
    def __init__(self):
        # Usamos un diccionario de adyacencia para representar el grafo.
        # Clave: Estado Origen -> Valor: {Evento -> Estado Destino}
        self.lista_adyacencia = {}
        self.construir_grafo_juego()

    def agregar_vertice(self, estado):
        """Asegura que el nodo (estado) exista en nuestro grafo."""
        if estado not in self.lista_adyacencia:
            self.lista_adyacencia[estado] = {}

    def agregar_arista(self, origen, evento, destino):
        """Define una transición válida entre dos estados disparada por un evento."""
        self.agregar_vertice(origen)
        self.agregar_vertice(destino)
        self.lista_adyacencia[origen][evento] = destino

    def construir_grafo_juego(self):
        """
        Aquí definimos las reglas de transición de estados del juego.
        Esencialmente, programamos la lógica de 'qué vence a qué' o 'qué causa qué'.
        """
        # Transiciones desde el estado base (Normal).
        self.agregar_arista("Normal", "fuego", "Quemado")
        self.agregar_arista("Normal", "cuchillo", "Sangrado")
        self.agregar_arista("Normal", "insulto", "Aturdido")
        self.agregar_arista("Normal", "defensa", "Escudo")

        # Interacciones entre estados alterados.
        # Esto permite dinámicas complejas, como cambiar un estado por otro.
        self.agregar_arista("Quemado", "cuchillo", "Sangrado") # El sangrado sobrescribe al fuego.
        self.agregar_arista("Quemado", "insulto", "Aturdido")
        
        self.agregar_arista("Sangrado", "fuego", "Quemado") # El fuego cauteriza/sobrescribe el sangrado.
        self.agregar_arista("Sangrado", "insulto", "Aturdido")

        # El aturdimiento es frágil; cualquier daño físico lo rompe y aplica su propio efecto.
        self.agregar_arista("Aturdido", "fuego", "Quemado")
        self.agregar_arista("Aturdido", "cuchillo", "Sangrado")

        # Rutas de salida (Curación o finalización de efecto).
        # El evento 'cura' sirve como reset universal para volver al estado normal.
        self.agregar_arista("Quemado", "cura", "Normal")
        self.agregar_arista("Sangrado", "cura", "Normal")
        self.agregar_arista("Aturdido", "cura", "Normal")
        
        self.agregar_arista("Escudo", "romper", "Normal")

    def transicion(self, estado_actual, evento):
        """
        Función motora del grafo. Dado donde estamos y qué pasó, 
        nos dice a dónde debemos ir.
        """
        nuevo_estado = estado_actual
        
        # Verificamos si existe una transición definida para este par Estado-Evento.
        if estado_actual in self.lista_adyacencia:
            adyacentes = self.lista_adyacencia[estado_actual]
            if evento in adyacentes:
                nuevo_estado = adyacentes[evento]
        
        # Feedback en consola para entender el flujo durante la partida.
        if nuevo_estado != estado_actual:
            print(f"[GRAFO] Transición: {estado_actual} + [{evento}] ---> {nuevo_estado}")
        else:
            print(f"[GRAFO] Intento fallido: {estado_actual} + [{evento}] (No hay arista)")
            
        return nuevo_estado