import random
import config
import heapq

"""
LÓGICA MATEMÁTICA Y DE DECISIONES (CEREBRO DEL JUEGO)

GUÍA RÁPIDA DE MODIFICACIÓN (REGLAS Y COMPORTAMIENTO):
-----------------------------------------------------------------------------------------
CLASE / LÓGICA          | MÉTODO / VARIABLE     | ACCIÓN / CÓMO MODIFICAR
-----------------------------------------------------------------------------------------
1. ÁRBOL DE COMBATE     | ArbolAtaque ->        | Define la jerarquía de suerte.
   (Suerte/RNG)         | construir_arbol()     | - Cambiar orden de 'probabilidad_limite'
                        |                       |   para priorizar Críticos o Fallos.
                        |                       | - Editar 'resultado_base' para cambiar
                        |                       |   mensajes o multiplicadores (x1.5).
-----------------------------------------------------------------------------------------
2. REACCIONES ELEM.     | GrafoEfectos ->       | Define qué estado vence a cuál.
   (Máquina Estados)    | construir_grafo_juego | - agregar_arista("Origen", "Evento", "Destino")
                        |                       |   Ej: Que 'Agua' quite 'Fuego'.
-----------------------------------------------------------------------------------------
3. PERSONALIDAD BOSS    | GrafoEstados ->       | Define los bonus pasivos del jefe.
   (Estados Emocionales)| self.bonus_estados    | - Editar diccionarios:
                        |                       |   "FURIA": {"ataque": 1.5...}
                        |-----------------------|----------------------------------------
                        | actualizar_estado()   | Define CUÁNDO cambia de humor.
                        |                       | - Modificar 'porc_vida < 30' o
                        |                       |   'boss.st >= 80' (Umbrales).
-----------------------------------------------------------------------------------------
4. ESTRATEGIA BOSS      | GrafoEstrategia ->    | Define el arsenal de ataques.
   (Grafo Ponderado)    | construir_grafo()     | - self.nodos["A"]: Crear/Editar ataques
                        |                       |   (Daño %, Costo HP, Efectos).
                        |                       | - conectar("A", {"B":3...}):
                        |                       |   Define la probabilidad de combos.
                        |                       |   (Peso BAJO = Alta prob. de combo).
                        |-----------------------|----------------------------------------
                        | seleccionar_...()     | Algoritmo de decisión (Prim).
                        |                       | Modificar 'score' para hacer la IA
                        |                       | más o menos inteligente.
-----------------------------------------------------------------------------------------
5. DEBUG / CONSOLA      | imprimir_debug_ia()   | Función global al final.
                        |                       | Comenta los 'print' si quieres
                        |                       | limpiar la consola de texto.
-----------------------------------------------------------------------------------------
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
        self.agregar_arista("Quemado", "cuchillo", "Sangrado")
        self.agregar_arista("Quemado", "insulto", "Aturdido")
        self.agregar_arista("Sangrado", "fuego", "Quemado")
        self.agregar_arista("Sangrado", "insulto", "Aturdido")
        self.agregar_arista("Aturdido", "fuego", "Quemado")
        self.agregar_arista("Aturdido", "cuchillo", "Sangrado")

        # Rutas de salida (Curación o finalización de efecto).
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
        
        # Se verifica si existe una transición definida para este par Estado-Evento.
        if estado_actual in self.lista_adyacencia:
            adyacentes = self.lista_adyacencia[estado_actual]
            if evento in adyacentes:
                nuevo_estado = adyacentes[evento]
        if nuevo_estado != estado_actual:
            print(f"[GRAFO] Transición: {estado_actual} + [{evento}] ---> {nuevo_estado}")
        else:
            print(f"[GRAFO] Intento fallido: {estado_actual} + [{evento}] (No hay arista)")
            
        return nuevo_estado

# ==========================================
# GRAFO DEL JEFE (ESTADOS)
# ==========================================
class GrafoEstados:
    """    
    Controla la actitud del jefe según sus variables de Vida (HP) y Estrés (ST).
    """
    def __init__(self):
        # Se usa el mismo sistema de lista de adyacencia que GrafoEfectos
        self.lista_adyacencia = {}
        self.construir_grafo_comportamiento()
        self.estado_actual = "NORMAL" 
        self.bonus_estados = {
            "NORMAL":    {"ataque": 1.0, "defensa": 1.0},
            "FURIA":     {"ataque": 1.5, "defensa": 0.8},
            "DEFENSIVO": {"ataque": 0.7, "defensa": 1.5},
            "CONFUSION": {"ataque": 0.5, "defensa": 0.5},
            "ESTRESADO": {"ataque": 1.2, "defensa": 0.9}
            }
            
    def agregar_vertice(self, estado):
        """Añade un estado si no existe."""
        if estado not in self.lista_adyacencia:
            self.lista_adyacencia[estado] = {}

    def agregar_arista(self, origen, evento, destino):
        """Crea una transición: Estado A + Evento -> Estado B"""
        self.agregar_vertice(origen)
        self.agregar_vertice(destino)
        self.lista_adyacencia[origen][evento] = destino

    def construir_grafo_comportamiento(self):
        # 1. Transiciones desde NORMAL (Estado Base)
        self.agregar_arista("NORMAL", "estres_alto", "FURIA")
        self.agregar_arista("NORMAL", "vida_baja", "DEFENSIVO")
        self.agregar_arista("NORMAL", "golpe_critico", "CONFUSION")

        # 2. Transiciones desde FURIA (Berserker)
        self.agregar_arista("FURIA", "calmado", "NORMAL")
        self.agregar_arista("FURIA", "colapso", "CONFUSION")

        # 3. Transiciones desde DEFENSIVO (Tortuga)
        self.agregar_arista("DEFENSIVO", "recuperacion", "NORMAL")
        self.agregar_arista("DEFENSIVO", "estres_alto", "FURIA")

        # 4. Transiciones desde CONFUSION (Estado Vulnerable)
        self.agregar_arista("CONFUSION", "recuperacion", "NORMAL")
        self.agregar_arista("CONFUSION", "ataque_recibido", "FURIA")

    def transicion(self, estado_actual, evento):
        """
        Calcula el siguiente estado dado el evento actual.
        """
        nuevo_estado = estado_actual
        
        # Se verifica si existe el estado y el evento en la lista de adyacencia
        if estado_actual in self.lista_adyacencia:
            adyacentes = self.lista_adyacencia[estado_actual]
            if evento in adyacentes:
                nuevo_estado = adyacentes[evento]
        if nuevo_estado != estado_actual:
            print(f"[IA TRUMP] Cambio de Humor: {estado_actual} + [{evento}] ---> {nuevo_estado}")
        
        return nuevo_estado

    def actualizar_estado(self, boss):
        """
        Calcula el nuevo estado emocional del jefe basándose en sus signos vitales.
        """
        # Analizo cuánta vida y estrés tiene el jefe para etiquetar el 
        # momento actual con un 'evento'.
        evento = "neutro"
        porc_vida = (boss.vida_actual / boss.vida_max) * 100
        
        if boss.st >= 80: evento = "estres_alto"
        elif porc_vida < 30: evento = "vida_baja"
        elif boss.st >= 40 and boss.st < 80: evento = "presion"
        elif boss.st < 20 and porc_vida > 50: evento = "calmado"
        elif porc_vida > 60: evento = "recuperado"
        
        # 2. Calcular la transición en el grafo
        # Le pregunto al grafo: "Si estoy en X estado y pasa el evento Y, a dónde voy?"
        nuevo = self.transicion(self.estado_actual, evento)
        
        # Guardo una copia del estado viejo en una variable local 
        # ANTES de actualizar el real.
        # Si no hago esto, pierdo el dato y la función de debug fallará.
        estado_anterior = self.estado_actual 
        
        # Ahora sí, actualizo el estado oficial del jefe.
        self.estado_actual = nuevo
        
        # Le paso todos los datos a la impresora 
        # (incluyendo la variable estado_anterior que acabamos de crear).
        imprimir_debug_ia("ESTADO", (boss, evento, estado_anterior, nuevo))
    def obtener_bonificadores(self):
        return self.bonus_estados.get(self.estado_actual, {"ataque": 1.0, "defensa": 1.0})

    
# ==========================================
# GRAFO DE ESTRATEGIA (PONDERADO)
# ==========================================
class NodoEstrategia:
    def __init__(self, codigo, nombre, efecto_tipo, valor_efecto, boost=None, costo_hp=0, efecto_estado=None):
        self.codigo = codigo
        self.nombre = nombre
        self.efecto_tipo = efecto_tipo 
        self.valor_efecto = valor_efecto
        self.boost = boost
        self.costo_hp = costo_hp
        self.efecto_estado = efecto_estado
        self.conexiones = {} 

class GrafoEstrategia:
    def __init__(self):
        self.nodos = {}
        self.nodo_actual = "A"
        self.construir_grafo()

    def construir_grafo(self):
        """
        Aquí defino el mapa mental del jefe, estableciendo qué ataques conoce y qué tan costoso es pasar de uno a otro.
        """
        #Empieza con el ataque mas basico        
        self.nodos["A"] = NodoEstrategia("A", "Bala (5%)", "dano", 0.05)
        
        self.nodos["B"] = NodoEstrategia("B", "Cuchillo (15%)", "dano", 0.15, efecto_estado="cuchillo")
        
        self.nodos["C"] = NodoEstrategia("C", "Molotov (20%)", "dano", 0.20, efecto_estado="fuego")
        
        
        # Esta es la maniobra defensiva donde el jefe se toma un respiro para curarse y subir su defensa preparándose para resistir.
        self.nodos["D"] = NodoEstrategia("D", "Táctica", "cura", 0.05, boost="defensa")
        
        # Un ataque híbrido un poco raro que mezcla daño y curación, lo dejo simple sin efectos adicionales.
        self.nodos["E"] = NodoEstrategia("E", "Combo Bala", "dano_cura", 0.05)
        
        # La versión definitiva del molotov que pega durísimo y quema, pero es tan intensa que el jefe debe sacrificar su propia salud para lanzarla.
        self.nodos["F"] = NodoEstrategia("F", "Molotov+", "dano", 0.25, boost="ataque", costo_hp=10, efecto_estado="fuego")

        # --- CONEXIONES (PESOS) ---
        
        # Construccion de las neuronas del jefe definiendo el 'costo' de transición entre ideas.
        # Un peso bajo significa que es muy probable y natural que el jefe encadene esos dos ataques seguidos.
        self.conectar("A", {"B":3, "C":3, "D":2})
        self.conectar("B", {"A":3, "D":4, "F":7})
        self.conectar("C", {"A":3, "D":6, "E":7})
        self.conectar("D", {"A":2, "B":4, "C":6, "E":8, "F":10})
        self.conectar("E", {"A":5, "C":7, "D":8, "F":14})
        self.conectar("F", {"A":5, "B":7, "D":10, "E":14})

    def conectar(self, origen, destinos_dict):
        for dest, peso in destinos_dict.items():
            self.nodos[origen].conexiones[dest] = peso

    def nodo_es_elegible(self, codigo_nodo, boss):
        """
        Verifica las condiciones para que un nodo sea 'Eligible y Usable'.
        """
        nodo = self.nodos[codigo_nodo]
        
        # 1. Condición de Vida (Costos)
        if boss.vida_actual <= nodo.costo_hp:
            return False
            
        # 2. Condición de Utilidad (No curarse si está lleno)
        if nodo.efecto_tipo == "cura" and boss.vida_actual == boss.vida_max:
            return False
            
        return True

    def aplicar_prim(self, nodo_inicio, boss):
        """
        Algoritmo de Prim para evaluar el Recorrido Óptimo (MST).
        Retorna la lista de aristas que forman la estrategia de menor costo
        considerando solo nodos elegibles.
        """
        visitados = set([nodo_inicio])
        mst_aristas = []
        
        # Inicializamos con las conexiones del nodo actual
        edges = []
        for dest, peso in self.nodos[nodo_inicio].conexiones.items():
            if self.nodo_es_elegible(dest, boss):
                heapq.heappush(edges, (peso, nodo_inicio, dest))
        
        # Bucle principal de Prim
        while edges:
            peso, u, v = heapq.heappop(edges)
            
            if v not in visitados:
                visitados.add(v)
                mst_aristas.append((u, v, peso))
                
                # Expandir desde el nuevo nodo v
                for vecino, peso_vecino in self.nodos[v].conexiones.items():
                    if vecino not in visitados and self.nodo_es_elegible(vecino, boss):
                        heapq.heappush(edges, (peso_vecino, v, vecino))
                        
        return mst_aristas

    def seleccionar_siguiente_ataque(self, boss):
        nodo_origen = self.nodo_actual
        mst = self.aplicar_prim(self.nodo_actual, boss)
        
        opciones_validas = []
        debug_opciones = [] # Lista temporal solo para el log
        
        vecinos = self.nodos[self.nodo_actual].conexiones
        for dest, peso in vecinos.items():
            if self.nodo_es_elegible(dest, boss):
                es_optimo = any(u == self.nodo_actual and v == dest for u, v, w in mst)
                score = 1.0 / (peso + 0.1)
                if es_optimo: score *= 2.0
                
                opciones_validas.append((dest, score))
                
                # Guardamos datos para la impresora
                debug_opciones.append({
                    "nodo": dest, 
                    "peso": peso, 
                    "score": score, 
                    "es_optimo": es_optimo
                })
        
        if not opciones_validas:
            self.nodo_actual = "A"
            return self.nodos["A"]

        # Selección
        destinos = [x[0] for x in opciones_validas]
        pesos = [x[1] for x in opciones_validas]
        seleccion = random.choices(destinos, weights=pesos, k=1)[0]
        
        imprimir_debug_ia("ESTRATEGIA", (
            nodo_origen, 
            self.nodos[nodo_origen].nombre, 
            mst, 
            debug_opciones, 
            seleccion
        ))
        
        self.nodo_actual = seleccion
        return self.nodos[seleccion]

def imprimir_debug_ia(tipo, datos):
    """
    Función universal para imprimir logs de la IA sin ensuciar las clases.
    Uso: imprimir_debug_ia("ESTADO", {datos...}) o imprimir_debug_ia("ESTRATEGIA", {datos...})
    """
    if tipo == "ESTADO":
        # Desempaquetamos los datos
        boss, evento, anterior, actual = datos
        porc = (boss.vida_actual / boss.vida_max) * 100
        
        print("\n" + "="*40)
        print(" INICIANDO IA DEL JEFE (DONALD T.)")
        print("="*40)
        print(f"[IA] Signos Vitales: HP {boss.vida_actual}/{boss.vida_max} ({porc:.1f}%) | Estrés {boss.st}/{boss.st_max}")
        print(f"[IA] Evento Interpretado: '{evento}'")
        
        if anterior != actual:
            print(f"[IA] ¡CAMBIO DE HUMOR!: {anterior} -> {actual}")
        else:
            print(f"[IA] Mantiene humor: {actual}")

    elif tipo == "ESTRATEGIA":
        # Desempaquetamos
        origen, nombre_origen, mst, opciones, decision = datos
        
        print("-" * 40)
        print(f"[ESTRATEGIA] Nodo Mental Actual: '{origen}' ({nombre_origen})")
        print("[ESTRATEGIA] Ejecutando Algoritmo de Prim (MST)...")
        
        if mst:
            for u, v, w in mst:
                print(f"   └── Conexión Óptima sugerida: {u} -> {v} (Peso {w})")
        else:
            print("   └── (Sin expansión: usando solo adyacentes)")

        print("[ESTRATEGIA] Evaluando probabilidades:")
        for op in opciones:
            tag = " [BONUS PRIM x2]" if op['es_optimo'] else ""
            print(f"   - Opción '{op['nodo']}': Peso {op['peso']} -> Score {op['score']:.3f}{tag}")
            
        print(f"[ESTRATEGIA] Decisión Final: '{decision}'")
        print("-" * 40)