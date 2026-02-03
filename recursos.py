import pygame
import config
import os

"""
GESTOR DE RECURSOS Y ASSETS
---------------------------
Este módulo funciona como el bibliotecario del juego. Su trabajo es ir al disco duro,
buscar las imágenes, cargarlas en la memoria RAM y tenerlas listas para cuando
el módulo de gráficos las pida.

INDICE RÁPIDO:
--------------
Línea 20 -> Clase AlmacenRecursos (Inicialización)
Línea 30 -> Carga masiva de imágenes (Lista de archivos)
Línea 65 -> Método seguro de carga (Manejo de errores/Placeholders)
"""

class AlmacenRecursos:
    """
    Contenedor centralizado de imágenes.
    
    Cargar imágenes es una operación lenta porque implica leer el disco duro.
    Por eso lo hacemos todo aquí una sola vez al arrancar el juego, guardamos
    el resultado en un diccionario (`self.assets`) y luego solo consultamos
    ese diccionario en memoria, que es muchísimo más rápido.
    """
    def __init__(self):
        # Diccionario clave-valor. Ejemplo: "jugador1" -> <Objeto Imagen Pygame>
        self.assets = {}
        
        # Ruta base donde tengo guardados los archivos.
        # Es útil tenerla en una variable por si decido mover la carpeta luego.
        self.ruta_img = "sprites_finales/img/"
        
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
        self.cargar('vip_victoria', "vip_victoria.png", (300, 300))

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

    def cargar(self, nombre_clave, nombre_archivo, tamano):
        """
        Método 'seguro' de carga.
        
        Si usamos pygame.image.load() directamente y el archivo no existe (ej. error de dedo),
        el juego se cierra de golpe (crash).
        
        Aquí usamos un bloque try-except. Si la imagen falla, creamos un cuadrado 
        color magenta (el color universal de 'textura perdida') y seguimos ejecutando.
        Esto me permite probar el juego aunque me falten assets.
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