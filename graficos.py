import pygame
import os
import config

"""
GESTOR DE GRÁFICOS (INTERFAZ VISUAL)
------------------------------------
Se encarga de cargar imágenes y dibujar en pantalla.
Si falta una imagen en 'assets/img/', usará un cuadro de color (PLACEHOLDER).
"""

class GestorGrafico:
    def __init__(self):
        # Inicializar pantalla
        self.pantalla = pygame.display.set_mode((config.ANCHO, config.ALTO))
        pygame.display.set_caption(config.TITULO)
        
        # Fuentes (Texto)
        self.fuente_ui = pygame.font.SysFont("Arial", 20, bold=True)
        self.fuente_grande = pygame.font.SysFont("Arial", 40, bold=True)
        
        # Diccionario de imágenes cargadas
        self.imgs = {}
        self.cargar_todos_los_assets()

    def cargar_imagen(self, nombre_archivo, color_placeholder=(255, 0, 255), tamaño=None):
        """Intenta cargar una imagen. Si falla, crea un cuadrado de color."""
        ruta = os.path.join("assets", "img", nombre_archivo)
        try:
            imagen = pygame.image.load(ruta).convert_alpha()
            if tamaño:
                imagen = pygame.transform.scale(imagen, tamaño)
            return imagen
        except FileNotFoundError:
            # Si no existe la imagen, creamos un cuadrado (Placeholder)
            print(f"AVISO: No se encontró '{nombre_archivo}'. Usando placeholder.")
            surf = pygame.Surface(tamaño if tamaño else (64, 64))
            surf.fill(color_placeholder)
            return surf

    def cargar_todos_los_assets(self):
        # 1. Fondos
        self.imgs["fondo_menu"] = self.cargar_imagen("fondo_menu.png", (0,0,100), (config.ANCHO, config.ALTO))
        
        # Cargar fondo del Nivel 1 (Donald T.)
        nivel1 = config.NIVELES[0]
        self.imgs["fondo_n1"] = self.cargar_imagen(nivel1["fondo"], (100,100,0), (config.ANCHO, config.ALTO))

        # 2. Personajes
        self.imgs["boss_idle"] = self.cargar_imagen("boss_idle.png", (255,0,0), (150, 150))
        self.imgs["soldado_idle"] = self.cargar_imagen("soldado_idle.png", (0,255,0), (100, 100)) # Necesitas este archivo o placeholder
        
        # 3. UI
        self.imgs["caja_texto"] = self.cargar_imagen("ui_caja_texto.png", (200,200,200), (600, 150))
        
        # 4. Iconos Habilidades (Ejemplo)
        self.imgs["icono_cuchillo"] = self.cargar_imagen("icono_cuchillo.png", (100,100,100), (50, 50))

    def dibujar_menu(self):
        """Dibuja la pantalla de inicio"""
        self.pantalla.blit(self.imgs["fondo_menu"], (0,0))
        
        texto = self.fuente_grande.render("PRESIONA ENTER PARA EMPEZAR", True, (255, 255, 255))
        rect_texto = texto.get_rect(center=(config.ANCHO//2, config.ALTO - 100))
        self.pantalla.blit(texto, rect_texto)

    def dibujar_batalla(self, jugador, jefe, texto_log):
        """Dibuja la escena de combate"""
        # 1. Fondo
        self.pantalla.blit(self.imgs["fondo_n1"], (0,0))
        
        # 2. Personajes (Posiciones fijas por ahora)
        # Jugador a la izquierda
        self.pantalla.blit(self.imgs["soldado_idle"], (100, 350))
        # Jefe a la derecha
        self.pantalla.blit(self.imgs["boss_idle"], (550, 300))
        
        # 3. UI - Caja de Texto
        pos_caja = (config.ANCHO//2 - 300, config.ALTO - 160)
        self.pantalla.blit(self.imgs["caja_texto"], pos_caja)
        
        # Texto dentro de la caja
        render_log = self.fuente_ui.render(texto_log, True, (0,0,0)) # Texto negro
        self.pantalla.blit(render_log, (pos_caja[0] + 20, pos_caja[1] + 20))
        
        # 4. Barras de Vida (Numéricas por ahora)
        txt_p1 = self.fuente_ui.render(f"{jugador.nombre}: {jugador.vida_actual}/{jugador.vida_max}", True, (255, 255, 255))
        self.pantalla.blit(txt_p1, (50, 50))
        
        txt_boss = self.fuente_ui.render(f"{jefe.nombre}: {jefe.vida_actual}/{jefe.vida_max}", True, (255, 255, 255))
        self.pantalla.blit(txt_boss, (500, 50))