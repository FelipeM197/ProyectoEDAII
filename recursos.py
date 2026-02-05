import pygame
import config
import os

"""
GESTOR DE RECURSOS (IMÁGENES Y AUDIO)

GUÍA RÁPIDA DE MODIFICACIÓN (CARGA DE ASSETS):
-----------------------------------------------------------------------------------------
CLASE / SECCIÓN         | MÉTODO / VARIABLE     | ACCIÓN / CÓMO MODIFICAR
-----------------------------------------------------------------------------------------
1. CONFIGURACIÓN        | __init__              | Rutas y Motores.
   (Rutas y Audio)      | - self.ruta_img       | - Cambiar carpeta de imágenes ("img/").
                        | - pygame.mixer.init() | - Inicializa el motor de audio.
-----------------------------------------------------------------------------------------
2. LISTA DE IMÁGENES    | cargar_todos()        | **AQUÍ AGREGAS/CAMBIAS SPRITES**
   (El Inventario)      | - self.cargar(...)    | Formato: ('clave', "archivo.png", (W, H))
                        |                       |
                        |   A. FONDOS/UI        | - Cambiar tamaño (ancho, alto) de cajas.
                        |   B. PERSONAJES       | - Cambiar "soldado1.png" por tu archivo.
                        |   C. PANTALLAS FINAL  | - "victoria_final" y "game_over".
                        |   D. ICONOS/ESTADOS   | - Proyectiles y efectos (fuego/sangre).
-----------------------------------------------------------------------------------------
3. AUDIO                | cargar_todos()        | Carga de SFX (Efectos cortos).
                        | - cargar_sonido(...)  | - Vincula una clave con la ruta de config.
                        |-----------------------|----------------------------------------
                        | cargar_sonido()       | Ajustes del archivo de audio.
                        | - sonido.set_volume   | - Cambiar volumen (0.0 a 1.0).
-----------------------------------------------------------------------------------------
4. SISTEMA DE ERRORES   | cargar()              | Qué pasa si falta una imagen.
   (Seguridad)          | - try / except        | - Si falla, crea un cuadro MAGENTA.
                        | - surf.fill(...)      | - Cambiar color del placeholder error.
-----------------------------------------------------------------------------------------
"""

class AlmacenRecursos:
    """
    Contenedor centralizado de imágenes y sonidos.
    
    Cargar imágenes es una operación lenta porque implica leer el disco duro.
    Por eso lo hacemos todo aquí una sola vez al arrancar el juego, guardamos
    el resultado en un diccionario (`self.assets`) y luego solo consultamos
    ese diccionario en memoria, que es muchísimo más rápido.
    """
    def __init__(self):
        # Diccionario clave-valor. Ejemplo: "jugador1" -> <Objeto Imagen Pygame>
        self.assets = {}
        
        # --- NUEVO: Diccionario para efectos de sonido ---
        self.sonidos = {} 
        
        # Ruta base donde tengo guardados los archivos.
        # Es útil tenerla en una variable por si decido mover la carpeta luego.
        self.ruta_img = "sprites_finales/img/"
        
        # --- NUEVO: Inicializar el sistema de audio (Mixer) ---
        # Es necesario encender el "motor de audio" de Pygame antes de cargar nada.
        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init()
        except Exception as e:
            print(f"Advertencia: No se pudo iniciar el audio: {e}")
        
        # Arrancamos la carga automática.
        self.cargar_todos()

    def cargar_todos(self):
        """
        Aquí definimos la lista de compras: qué archivos necesitamos para jugar.
        Organizo la carga por categorías para mantener el orden.
        """
        # --- 1. ELEMENTOS DE INTERFAZ (UI) Y ESCENARIO ---
        # El fondo debe coincidir con la resolución definida en config.ANCHO/ALTO.
        self.cargar('fondo', "escenario.png", (config.ANCHO, config.ALTO))
        self.cargar('caja_texto', "ui_caja_texto.png", (1100, 200))
        self.cargar('menu_pausa', "ui_menu_pausa.png", (400, 450))
        self.cargar('cursor', "ui_cursor.png", (30, 30))
        
        # Reutilizo la misma imagen del fondo para el menú principal por ahora.
        self.assets["fondo_menu"] = self.assets['fondo']

        # --- 2. PERSONAJES ---
        # Cargo los sprites de los soldados y el jefe.
        self.cargar('jugador1', "soldado1.png", (300, 300))
        self.cargar('jugador2', "soldado2.png", (300, 300))
        self.cargar('boss_idle', "boss_idle.png", (300, 300))
        self.cargar('boss_atacando', "boss_atacando.png", (300, 300))
        self.cargar('boss_dano', "boss_dano.png", (300, 300))
        
        # --- SPRITES DE DAÑO / DERROTA ---
        # Estas imágenes se muestran cuando la vida llega a 0 o reciben un golpe fuerte.
        self.cargar('jugador1_dano', "soldado1_dano.png", (300, 300))
        self.cargar('jugador2_dano', "soldado2_dano.png", (300, 300)) 

        # Imagen especial para la pantalla de victoria.
        self.cargar('victoria_final', "victoria_final.png", (1000, 650)) # Ojo: Asegúrate que el nombre coincida con tu carpeta

        #imagen especial para la pantalla de derrota.
        self.cargar('game_over', 'game_over.png', (1000, 650))

        # --- 3. ICONOS, PROYECTILES Y EFECTOS ---
        # Iconos pequeños para las habilidades y efectos visuales.
        self.cargar('proy_disparo', "icono_disparo.png", (64, 64))
        self.cargar('proy_molotov', "icono_molotov.png", (64, 64))
        self.cargar('proy_cuchillo', "icono_cuchillo.png", (64, 64))
        self.cargar('proy_calavera', "icono_intimidar.png", (64, 64))
        self.cargar('proy_grito', "icono_grito.png", (64, 64))
        self.cargar('icono_escudo', "icono_escudo.png", (80, 80))
        self.cargar('icono_curar', "icono_curar.png", (80, 80))

        # Indicadores de estado (aparecen sobre la cabeza de los personajes).
        self.cargar('est_aturdido', "estado_aturdido.png", (100, 100))
        self.cargar('est_quemado', "estado_quemado.png", (100, 100))
        self.cargar('est_sangrado', "estado_sangrado.png", (100, 100))

        # --- 4. NUEVO: CARGA DE SONIDOS ---
        # Cargamos el efecto de sonido "Start". 
        # La música de fondo no se carga aquí, se hace stream en el main.
        self.cargar_sonido('sfx_start', config.RUTA_SFX_START)

    def cargar(self, nombre_clave, nombre_archivo, tamano):
        """
        Método 'seguro' de carga de IMÁGENES.
        """
        ruta_completa = os.path.join(self.ruta_img, nombre_archivo)
        
        try:
            # Intentamos cargar y convertir la imagen (convert_alpha es vital para transparencias).
            img = pygame.image.load(ruta_completa).convert_alpha()
            # La escalamos al tamaño deseado y la guardamos en el diccionario.
            self.assets[nombre_clave] = pygame.transform.scale(img, tamano)
            
        except Exception as e:
            # Si algo sale mal, avisamos en la consola pero NO detenemos el juego.
            print(f"[ALERTA] Error cargando '{nombre_archivo}': {e}")
            print(f"         -> Generando placeholder para '{nombre_clave}'")
            
            # Generamos un cuadrado magenta de reemplazo.
            surf = pygame.Surface(tamano)
            surf.fill((255, 0, 255)) # RGB: Magenta brillante
            self.assets[nombre_clave] = surf

    # --- NUEVO MÉTODO ---
    def cargar_sonido(self, nombre_clave, ruta_archivo):
        """
        Método seguro para cargar EFECTOS DE SONIDO (WAV).
        """
        try:
            # pygame.mixer.Sound carga el archivo completo en memoria RAM.
            # Ideal para sonidos cortos como disparos, golpes o botones.
            sonido = pygame.mixer.Sound(ruta_archivo)
            sonido.set_volume(0.5) # Volumen al 50% por defecto
            self.sonidos[nombre_clave] = sonido
        except Exception as e:
            print(f"[ERROR AUDIO] No se cargó '{ruta_archivo}': {e}")
            # Si falla, guardamos None para evitar errores al intentar reproducirlo
            self.sonidos[nombre_clave] = None