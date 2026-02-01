import pygame

"""
ARCHIVO DE CONFIGURACIÓN (CONSTANTES)
"""

# ==========================================
# 1. CONFIGURACIÓN DE PANTALLA Y SISTEMA
# ==========================================
# Resolución de la ventana. 
# [MODIFICACIÓN]: Si cambian esto, asegúrense de que las imágenes de fondo
# tengan la misma proporción para que no se vean estiradas.
ANCHO = 1280
ALTO = 720

TITULO = "Rescate en el Norte: Operación Libertad"
FPS = 60  # Fotogramas por segundo (Velocidad del juego)

# ==========================================
# 2. COLORES (Formato RGB)
# ==========================================
# Se usan para textos y figuras geométricas si fallan las imágenes.
BLANCO = (255, 255, 255)
NEGRO = (0, 0, 0)
ROJO = (255, 0, 0)
VERDE = (0, 255, 0)
AZUL = (0, 0, 255)

# ==========================================
# 3. MENÚ DE PAUSA
# ==========================================
# Opciones que aparecen al presionar la tecla 'P'.
# [CUIDADO]: Si agregan una opción nueva aquí, deben programar su lógica
# en el archivo main.py dentro del bucle de eventos.
OPCIONES_PAUSA = ["CONTINUAR", "GUARDAR", "SALIR"]

# ==========================================
# 4. ESTADÍSTICAS DE JUGADORES (BALANCEO)
# ==========================================

# --- JUGADOR 1 (DPS / Atacante) ---
P1_NOMBRE = "Jugador 1"
P1_VIDA_MAX = 100      # Vida total. Aumentar para hacerlo más resistente.
P1_ATAQUE = 20         # Daño base de sus ataques normales.
P1_ENERGIA_MAX = 50    # (Reservado para uso futuro de maná/energía).

# [IMPORTANTE]: LISTA DE HABILIDADES
# Cada habilidad es un diccionario {}. 
# SI AGREGAN UNA NUEVA, COPIEN Y PEGUEN LA ESTRUCTURA EXACTA.
# Si falta una clave (ej: "id" o "efecto_code"), el juego se cerrará con error.
HABILIDADES_P1 = [
    {
        "id": "h_disparo",              # Identificador interno (no se ve en pantalla)
        "nombre": "Disparo Preciso",    # Nombre visible
        "dano": 30,                     # Cuánto quita de vida
        "costo": 15,                    # Costo de energía (si se implementa)
        "tipo": "ATAQUE",               # Categoría
        "desc": "Disparo certero a la cabeza.", # Descripción
        "icono": "icono_disparo.png",   # Nombre del archivo en la carpeta de sprites
        "efecto_code": "CRITICO"        # Clave para el Grafo de Estados (ver estructuras.py)
    },
    {
        "id": "h_granada",
        "nombre": "Granada", 
        "dano": 45, 
        "costo": 30, 
        "tipo": "ATAQUE", 
        "desc": "Explosión de área masiva.",
        "icono": "icono_molotov.png",
        "efecto_code": "QUEMADURA"      # Esto activará el estado 'Quemado'
    },
    {
        "id": "h_recarga",
        "nombre": "Recargar", 
        "dano": 0,                      # 0 daño porque es soporte
        "costo": 0, 
        "tipo": "SOPORTE", 
        "desc": "Recupera energía rápidamente.",
        "icono": "icono_grito.png",
        "efecto_code": "RECARGA"
    }
]

# --- JUGADOR 2 (Tanque / Soporte) ---
P2_NOMBRE = "Jugador 2"
P2_VIDA_MAX = 150      # Tiene más vida porque es Tanque
P2_ATAQUE = 12         # Pega menos que el J1
P2_ENERGIA_MAX = 50

HABILIDADES_P2 = [
    {
        "id": "h_escudo",
        "nombre": "Escudo", 
        "dano": 0, 
        "costo": 20, 
        "tipo": "DEFENSA", 
        "desc": "Bloquea el próximo ataque.",
        "icono": "icono_escudo.png",
        "efecto_code": "ESCUDO"
    },
    {
        "id": "h_curar",
        "nombre": "Curar", 
        "dano": -20,                    # [TRUCO]: Daño negativo significa CURACIÓN en la lógica del juego.
        "costo": 30, 
        "tipo": "CURACION", 
        "desc": "Restaura vida a un aliado.",
        "icono": "icono_curar.png",
        "efecto_code": "CURACION"
    },
    {
        "id": "h_intimidar",
        "nombre": "Intimidar", 
        "dano": 5, 
        "costo": 10, 
        "tipo": "DEBUFF", 
        "desc": "Reduce el ataque del enemigo.",
        "icono": "icono_intimidar.png",
        "efecto_code": "DEBILIDAD"
    }
]

# ==========================================
# 5. MATEMÁTICAS DEL ÁRBOL DE DECISIÓN
# ==========================================
# Estos valores controlan la "suerte" en el combate.
# Rango: 0.0 (0%) a 1.0 (100%)

PROB_ACIERTO = 0.85   # 85% de probabilidad de que el ataque conecte.
PROB_CRITICO = 0.20   # 20% de probabilidad de hacer daño extra.
PROB_TROPIEZO = 0.10  # 10% de probabilidad de herirse a uno mismo al fallar.

# --- MULTIPLICADORES DE DAÑO ---
MULT_CRITICO = 1.5    # El crítico hace 1.5 veces el daño normal (50% más).
DANO_TROPIEZO = 10    # Daño fijo que recibe el personaje si se tropieza.

# ==========================================
# 6. CONFIGURACIÓN DEL NIVEL Y BOSS
# ==========================================
NIVELES = [
    {
        "fondo": "escenario.png",       # Imagen de fondo (debe estar en la carpeta de sprites)
        "boss_nombre": "Donald T.",
        "boss_vida": 300,               # [DIFICULTAD]: Aumentar este número para batallas más largas.
        "boss_ataque": 15,              # Daño base del jefe.
        "dialogo_entrada": "¡No pasaran mi muro!"
    }
]

# ==========================================
# 7. SISTEMA DE DIÁLOGOS (Flavor Text)
# ==========================================
# Frases aleatorias que aparecen en la caja de texto.
# [MODIFICACIÓN]: Pueden agregar tantas frases como quieran entre las comillas.

FRASES_EXITO = [
    "¡Blanco acertado!", 
    "¡Golpe directo!", 
    "¡Toma eso!",
    "¡En el blanco!"
]

FRASES_FALLO = [
    "¡Fallaste!", 
    "¡Se movió rápido!", 
    "¡Resbalaste!",
    "El disparo se desvió."
]

FRASES_BOSS = [
    "¡Estás despedido!", 
    "¡Construiré un muro!", 
    "¡Fake News!",
    "¡Tengo inmunidad!"
]