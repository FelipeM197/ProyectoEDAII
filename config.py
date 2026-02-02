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
P1_ENERGIA_MAX = 10   

P2_NOMBRE = "Jugador 2"
P2_VIDA_MAX = 150      # Vida total. Aumentar para hacerlo más resistente.
P2_ATAQUE = 15         # Daño base de sus ataques normales.
P2_ENERGIA_MAX = 150    # (Reservado para uso futuro de maná/energía).

# Cada habilidad es un diccionario {}. .
# Si falta una clave (ej: "id" o "efecto_code"), el juego se cerrará con error.

HABILIDADES_P1 = [
    {
        "id": "h_cuchillada",
        "nombre": "Cuchillada",
        "dano": 30,
        "costo": 30,
        "tipo": "ATAQUE",
        "desc": "Sangrado: Recibirá daño hasta curarse.",
        "icono": "icono_cuchillo.png",
        "efecto_code": "cuchillo"  # Conecta con Grafo: Normal -> Sangrado
    },
    {
        "id": "h_molotov",
        "nombre": "Cóctel Molotov",
        "dano": 40,
        "costo": 40,
        "tipo": "ATAQUE",
        "desc": "Quemado: Daño constante por turno.",
        "icono": "icono_molotov.png",
        "efecto_code": "fuego"     # Conecta con Grafo: Normal -> Quemado
    },
    {
        "id": "h_motivacion",
        "nombre": "Motivación",
        "dano": 0,                # No hace daño, es un buff
        "costo": 50,
        "tipo": "BUFF",
        "desc": "Motivado: +Crítico y -Costos.",
        "icono": "icono_grito.png",
        "efecto_code": "motivacion"
    },
    {
        "id": "h_intimidacion",
        "nombre": "Intimidación",
        "dano": 10,
        "costo": 25,
        "tipo": "DEBUFF",
        "desc": "Vulnerable: Enemigo recibe más daño.",
        "icono": "icono_intimidar.png",
        "efecto_code": "insulto"   # Conecta con Grafo: Normal -> Aturdido/Vulnerable
    }
]

HABILIDADES_P2 = [
    {
        "id": "h_muro",
        "nombre": "Muro Contención",
        "dano": 0,
        "costo": 35,
        "tipo": "DEFENSA",
        "desc": "Escudado: Absorbe daño antes de tocar HP.",
        "icono": "icono_escudo.png",
        "efecto_code": "defensa"
    },
    {
        "id": "h_discurso",
        "nombre": "Discurso",
        "dano": 15,
        "costo": 45,
        "tipo": "DEBUFF",
        "desc": "Aturdido: Rival pierde siguiente turno.",
        "icono": "icono_grito.png",
        "efecto_code": "insulto"
    },
    {
        "id": "h_bono",
        "nombre": "Bono de Guerra",
        "dano": -30,              # Negativo = Curación
        "costo": 60,
        "tipo": "CURACION",
        "desc": "Curado: Recupera porción de vida.",
        "icono": "icono_curar.png",
        "efecto_code": "cura"
    },
    {
        "id": "h_disparo_p2",
        "nombre": "Disparo Táctico",
        "dano": 25,
        "costo": 30,
        "tipo": "ATAQUE",
        "desc": "Ataque básico a distancia.",
        "icono": "icono_disparo.png",
        "efecto_code": "CRITICO"
    }
]
# ==========================================
# 5. MATEMÁTICAS DEL ÁRBOL DE DECISIÓN
# ==========================================
# Estos valores controlan la "suerte" en el combate.

PROB_ACIERTO = 0.85   
PROB_CRITICO = 0.20  
PROB_TROPIEZO = 0.10  

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
        "boss_vida": 300,             
        "boss_ataque": 15,              
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