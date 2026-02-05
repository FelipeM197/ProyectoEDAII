import pygame

"""
ARCHIVO DE CONFIGURACIÓN (CONSTANTES)

GUÍA RÁPIDA DE MODIFICACIÓN (VARIABLES CLAVE):
-----------------------------------------------------------------------------------------
SECCIÓN                 | VARIABLE(S) BUSCAR    | ACCIÓN / CÓMO MODIFICAR
-----------------------------------------------------------------------------------------
1. PANTALLA             | ANCHO, ALTO           | Cambiar resolución de ventana (px).
                        | FPS                   | Ajustar velocidad del juego (30/60).
-----------------------------------------------------------------------------------------
2. COLORES              | BLANCO, NEGRO, ETC.   | Cambiar valores RGB (0-255).
-----------------------------------------------------------------------------------------
3. MENÚ PAUSA           | OPCIONES_PAUSA        | Editar textos de botones ["Texto",..].
-----------------------------------------------------------------------------------------
4. ESTADÍSTICAS JUGADOR | P1_VIDA_MAX, P1_ATAQUE| Balancear vida/daño base.
                        | P2_VIDA_MAX, P2_ATAQUE| (Igual para el Jugador 2).
-----------------------------------------------------------------------------------------
5. HABILIDADES          | HABILIDADES_P1 (Lista)| En cada {}:
                        | HABILIDADES_P2 (Lista)| - 'dano': Potencia (negativo cura).
                        |                       | - 'costo': Energía requerida.
                        |                       | - 'desc': Texto descriptivo.
-----------------------------------------------------------------------------------------
6. MATEMÁTICAS (AZAR)   | PROB_ACIERTO          | Probabilidad base (0.0 a 1.0).
                        | PROB_CRITICO          | Probabilidad de golpe x1.5.
                        | MULT_CRITICO          | Multiplicador de daño crítico.
-----------------------------------------------------------------------------------------
7. NIVEL Y BOSS         | NIVELES (Lista)       | En 'boss_vida' y 'boss_ataque':
                        |                       | Ajustar dificultad del jefe final.
-----------------------------------------------------------------------------------------
8. TEXTOS (FLAVOR)      | FRASES_EXITO,         | Añadir/Editar frases aleatorias
                        | FRASES_FALLO, BOSS    | dentro de las comillas " ".
-----------------------------------------------------------------------------------------
"""

# ==========================================
# 1. CONFIGURACIÓN DE PANTALLA Y SISTEMA
# ==========================================
# Aquí establezco las dimensiones de la ventana del juego.
# Tengo que cuidar que el fondo coincida con esta proporción.
ANCHO = 1280
ALTO = 720

TITULO = "Rescate en el Norte: Operación Libertad"
FPS = 60  # Defino la velocidad del bucle del juego (cuadros por segundo).

# ==========================================
# 2. COLORES (Formato RGB)
# ==========================================
# Defino una paleta básica de colores para usar en textos
# o elementos gráficos si no cargan las imágenes.
BLANCO = (255, 255, 255)
NEGRO = (0, 0, 0)
ROJO = (255, 0, 0)
VERDE = (0, 255, 0)
AZUL = (0, 0, 255)

# ==========================================
# 3. MENÚ DE PAUSA
# ==========================================
# Estas son las opciones que muestro cuando pauso el juego.
# Nota: Si se agrega algo aquí, necesito programar la acción en el main.
OPCIONES_PAUSA = ["CONTINUAR", "GUARDAR", "SALIR"]

# ==========================================
# 4. ESTADÍSTICAS DE JUGADORES (BALANCEO)
# ==========================================

# --- JUGADOR 1 (DPS / Atacante) ---
P1_NOMBRE = "Jugador 1"
P1_VIDA_MAX = 100   # Vida total actual del personaje.
P1_ATAQUE = 20       # Daño base que hago con ataques normales.
P1_ENERGIA_MAX = 100  

# --- JUGADOR 2 (Tanque / Soporte) ---
P2_NOMBRE = "Jugador 2"
P2_VIDA_MAX = 100  # Vida total actual del segundo personaje.
P2_ATAQUE = 15       # Daño base un poco más bajo que el P1.
P2_ENERGIA_MAX = 150 # Reservo esto por si implemento maná luego.

# Definición de habilidades individuales.
# Cada diccionario representa una acción posible en el combate.

DATO_BOTIQUIN = {
    "id": "h_botiquin",
    "nombre": "Botiquín Táctico",
    "dano": 0,
    "costo": 0,             # Lo dejo gratis para que siempre se pueda usar.
    "tipo": "LIMPIEZA",     # Tipo especial para quitar estados alterados.
    "desc": "Antídoto: Elimina Fuego, Sangrado y Aturdimiento.",
    "icono": "icono_curar.png",
    "efecto_code": "cura"   # Identificador para la lógica interna.
}

DATO_BASICO = {
    "nombre": "Golpe Táctico",
    "dano": 15,             # Ataque débil de emergencia.
    "costo": 0,             # Sin costo de energía.
    "tipo": "ATAQUE",
    "desc": "Ataque cuerpo a cuerpo de emergencia.",
    "icono": "icono_cuchillo.png",
    "efecto_code": "fisico"
}

# Lista de habilidades asignadas al Jugador 1
HABILIDADES_P1 = [
    {
        "id": "h_cuchillada",
        "nombre": "Cuchillada",
        "dano": 30,
        "costo": 30,
        "tipo": "ATAQUE",
        "desc": "Sangrado: Recibirá daño hasta curarse.",
        "icono": "icono_cuchillo.png",
        "efecto_code": "cuchillo"
    },
    {
        "id": "h_molotov",
        "nombre": "Cóctel Molotov",
        "dano": 40,
        "costo": 40,
        "tipo": "ATAQUE",
        "desc": "Quemado: Daño constante por turno.",
        "icono": "icono_molotov.png",
        "efecto_code": "fuego"
    },
    {
        "id": "h_motivacion",
        "nombre": "Motivación",
        "dano": 0,
        "costo": 50,
        "tipo": "BUFF",
        "desc": "Motivado: -Costos.",
        "icono": "icono_grito.png",
        "efecto_code": "motivacion"
    },
    {
        "id": "h_intimidacion",
        "nombre": "Intimidación",
        "dano": 0,
        "costo": 25,
        "tipo": "DEBUFF",
        "desc": "Vulnerable: Enemigo recibe más daño.",
        "icono": "icono_intimidar.png",
        "efecto_code": "insulto"
    },
    DATO_BOTIQUIN  # Añado el botiquín al final de la lista.
]

# Lista de habilidades asignadas al Jugador 2
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
        "dano": 0,
        "costo": 45,
        "tipo": "DEBUFF",
        "desc": "Aturdido: Rival pierde siguiente turno.",
        "icono": "icono_grito.png",
        "efecto_code": "insulto"
    },
    {
        "id": "h_bono",
        "nombre": "Bono de Guerra",
        "dano": -30,
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
    },
    DATO_BOTIQUIN  # El botiquín también lo tiene este jugador.
]

# ==========================================
# 5. MATEMÁTICAS DEL ÁRBOL DE DECISIÓN
# ==========================================

PROB_ACIERTO = 0.80   # Probabilidad base de golpear.
PROB_CRITICO = 0.20   # Probabilidad de hacer un golpe crítico.
PROB_TROPIEZO = 0.10  # Probabilidad de fallar y recibir daño propio.

# --- MULTIPLICADORES DE DAÑO ---
MULT_CRITICO = 1.5    # Si es crítico, multiplico el daño por 1.5.
DANO_TROPIEZO = 10    # Daño fijo que me hago si me tropiezo.
DURACION_QUEMADO = 3  # Turnos que dura el efecto de fuego.
DURACION_MOTIVACION = 3
# ==========================================
# 6. CONFIGURACIÓN DEL NIVEL Y BOSS
# ==========================================
# Lista de niveles. Aquí defino quién es el jefe y sus estadísticas. Solo pudimos hacer 1 :c
NIVELES = [
    {
        "fondo": "escenario.png",       # Archivo de imagen para el fondo.
        "boss_nombre": "Donald T.",
        "boss_vida": 100,             
        "boss_ataque": 15,              
        #"dialogo_entrada": "holi"
    }
]

# ==========================================
# 7. SISTEMA DE DIÁLOGOS (Flavor Text)
# ==========================================
# Frases que el juego selecciona al azar para mostrar en la caja de texto.
# Puedo agregar más frases simplemente añadiendo strings a las listas.

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

# --- SONIDOS ---
RUTA_MUSICA = "sonidos/batalla.mp3"
RUTA_SFX_START = "sonidos/intro.wav"