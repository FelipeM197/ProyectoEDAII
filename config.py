"""
ARCHIVO DE CONFIGURACIÓN GLOBAL
-------------------------------
1. Cambiar VIDA/DAÑO de Jugadores ............ Ir a Línea 24
2. Cambiar VIDA/DAÑO del JEFE (Trump) ........ Ir a Línea 41
3. Cambiar PROBABILIDAD DE ACIERTO (0.8) ..... Ir a Línea 54
4. Cambiar Daño CRÍTICO o TROPIEZO ........... Ir a Línea 62
5. Cambiar Nombres/IDs de Efectos ............ Ir a Línea 70
6. Modificar HABILIDADES (Costos/Efectos) .... Ir a Línea 86
7. Modificar FRASES/DIÁLOGOS ................. Ir a Línea 145 (TODO)
"""

# ==========================================
# 1. CONFIGURACIÓN TÉCNICA
# ==========================================
ANCHO = 800
ALTO = 600
FPS = 60
TITULO = "Rescate en el Norte" 

# ==========================================
# 2. ESTADÍSTICAS BASE DE PERSONAJES
# ==========================================
"""
Para cambiar la vida o energía base, edita esta sección.
"""
# JUGADOR 1 (Ofensivo - Daño)
P1_NOMBRE = "Soldado Daño"
P1_VIDA_MAX = 100      
P1_ATAQUE = 20         
P1_ENERGIA_MAX = 100   

# JUGADOR 2 (Defensivo - Tanque)
P2_NOMBRE = "Soldado Tanque"
P2_VIDA_MAX = 150      
P2_ATAQUE = 15         
P2_ENERGIA_MAX = 150   

# ==========================================
# 7. CONFIGURACIÓN DE NIVELES (ESCALABILIDAD)
# ==========================================
"""
Lista de niveles del juego.
Para agregar un nuevo nivel, añade un nuevo bloque {} separado por comas.
Para cambiar la dificultad de un nivel, edita los valores dentro de su bloque.
"""
NIVELES = [
    # --- NIVEL 1 (ACTUAL) ---
    {
        "id": 1,
        "boss_nombre": "Donald T.",
        "boss_vida": 300,        # Muevele a lo que le veas conveniente jordy
        "boss_ataque": 25,       
        "fondo": "fondo_n1.png"  # Nombre de archivo para graficos.py
    }
    
    # Cuando quieras añadir el Nivel 2, solo descomenta y edita esto:
    # ,{
    #     "id": 2,
    #     "boss_nombre": "Elon M.",
    #     "boss_vida": 400,
    #     "boss_ataque": 30,
    #     "fondo": "fondo_n2.png"
    # }
]    

# ==========================================
# 3. ÁRBOL DE PROBABILIDAD (ATAQUES BÁSICOS)
# ==========================================
"""
Para ajustar la dificultad de acertar golpes, edita esta sección.
NOTA: Se usan valores decimales (0.0 a 1.0) para consistencia.
"""
# El valor generado (0.0-1.0) debe ser MAYOR a esto para acertar.
PROB_ACIERTO = 0.8
PROB_FALLO = 0.2   

# Probabilidades Internas (Deben sumar 1.0 dentro de su rama)
PROB_CRITICO = 0.3     
PROB_NORMAL = 0.7      
PROB_TROPIEZO = 0.1    
PROB_NADA = 0.9        

# Multiplicadores
MULT_CRITICO = 2.0     
DANO_TROPIEZO = 10    

# ==========================================
# 4. SISTEMA DE IDs Y EFECTOS (GRAFOS)
# ==========================================
"""
Para cambiar qué ID corresponde a qué tipo de ataque, mira esta tabla.
"""
ID_ESTADO_INICIAL = 0
ID_ATAQUE_FISICO = 1   # Acción Directa
ID_ELEMENTAL = 2       # Recurso Especial (Fuego, curacion)
ID_CONTROL = 3         # Habilidad de Estado

# Valores de Efectos
DANO_QUEMADURA = 5    # Daño por turno si está Quemado
DANO_SANGRADO = 5     # Daño al actuar si tiene Sangrado
ESCUDO_VALOR = 30      # Cuánto absorbe el escudo
CURACION_VALOR = 20    # Cuánto cura la habilidad de curación

# ==========================================
# 5. HABILIDADES 
# ==========================================
"""
Todas las habilidades detalladas del los personajes
"""

# Habilidades Personaje 1
HABILIDADES_P1 = [
    {
        "nombre": "Cuchillada",
        "costo": 30,
        "desc": "Sangrado: Recibirá daño hasta curarse.",
        "id": 1,
        "efecto_code": "sangrado"
    },
    {
        "nombre": "Cóctel Molotov",
        "costo": 40,
        "desc": "Quemado: Daño constante por turno.",
        "id": 2,
        "efecto_code": "quemado"
    },
    {
        "nombre": "Motivación",
        "costo": 50,
        "desc": "Motivado: +Crítico y -Costos.",
        "id": 3,
        "efecto_code": "motivado"
    },
    {
        "nombre": "Intimidación",
        "costo": 25,
        "desc": "Vulnerable: Enemigo recibe más daño.",
        "id": 3,
        "efecto_code": "vulnerable"
    }
]

# Habilidades Personaje 2
HABILIDADES_P2 = [
    {
        "nombre": "Muro de Contención",
        "costo": 35,
        "desc": "Escudado: Absorbe daño antes de tocar HP.",
        "id": 3,
        "efecto_code": "escudo"
    },
    {
        "nombre": "Discurso",
        "costo": 45,
        "desc": "Aturdido: Rival pierde siguiente turno.",
        "id": 3,
        "efecto_code": "aturdido"
    },
    {
        "nombre": "Bono de Guerra",
        "costo": 60,
        "desc": "Curado: Recupera porción de vida.",
        "id": 1,
        "efecto_code": "curar"
    },
    {
        "nombre": "Disparo",
        "costo": 30,
        "desc": "Sangrado: Recibirá daño hasta curarse.",
        "id": 1,
        "efecto_code": "sangrado"
    }
]

# ==========================================
# 6. DIÁLOGOS Y TEXTOS (LORE)
# ==========================================
"""
TODO agregar las frases 
"""
FRASES_EXITO = []
FRASES_FALLO = []
FRASES_BOSS = []