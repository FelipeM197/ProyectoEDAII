import pygame
import os
import config
import time

"""
GESTOR DE GRÁFICOS (INTERFAZ VISUAL)
- Si quieren cambiar CÓMO SE VE el juego (imágenes, posiciones, colores), toquen aquí.
- Si quieren cambiar la LÓGICA (daño, turnos), vayan a main.py.
"""

class GestorGrafico:
    def __init__(self, pantalla):
        self.pantalla = pantalla
        
        # --- CONFIGURACIÓN DE FUENTES (LETRAS) ---
        # [MODIFICACIÓN]: Cambien el número (24, 18, 40) para hacer la letra más grande o pequeña.
        self.fuente_ui = pygame.font.SysFont("Arial", 24, bold=True)      # Para la vida (HP)
        self.fuente_log = pygame.font.SysFont("Arial", 18)                # Para la caja de texto
        self.fuente_grande = pygame.font.SysFont("Arial", 40, bold=True)  # Para el menú principal
        
        # Diccionario donde guardamos todas las imágenes cargadas en memoria
        self.assets = {}
        
        # Ejecutamos la carga inicial
        self.cargar_recursos()
        self.cargar_todos_los_assets()

    def cargar_recursos(self):
        """
        Carga las imágenes principales.
        [MODIFICACIÓN]: Si cambian el nombre de un archivo en la carpeta, CAMBIENLO AQUÍ TAMBIÉN.
        """
        try:
            # --- CARPETA SPRITES_JHON (Imágenes Base) ---
            img_fondo = pygame.image.load("sprites_jhon/escenario.png").convert()
            self.assets['fondo'] = pygame.transform.scale(img_fondo, (config.ANCHO, config.ALTO))
            
            # Jugadores y Boss (Estado normal)
            img_p1 = pygame.image.load("sprites_jhon/soldado1.png").convert_alpha()
            self.assets['jugador1'] = pygame.transform.scale(img_p1, (180, 180)) # (Ancho, Alto)
            
            img_p2 = pygame.image.load("sprites_jhon/soldado2.png").convert_alpha()
            self.assets['jugador2'] = pygame.transform.scale(img_p2, (180, 180))
            
            img_boss = pygame.image.load("sprites_jhon/boss_idle.png").convert_alpha()
            self.assets['boss_idle'] = pygame.transform.scale(img_boss, (280, 280))
            
            # Caja de texto blanca
            img_caja = pygame.image.load("sprites_jhon/cajadeTexto.png").convert_alpha()
            self.assets['caja_texto'] = pygame.transform.scale(img_caja, (900, 120))

            # --- CARPETA SPRITES_FINALES (Efectos y UI) ---
            ruta_finales = "sprites_finales/img/"
            
            # Variaciones del Boss (Herido y Atacando)
            self.assets['boss_dano'] = self.cargar_y_escalar(ruta_finales + "boss_dano.png", (280, 280))
            self.assets['boss_atacando'] = self.cargar_y_escalar(ruta_finales + "boss_atacando.png", (280, 280))
            
            # Interfaz de Usuario (UI)
            self.assets['menu_pausa'] = self.cargar_y_escalar(ruta_finales + "ui_menu_pausa.png", (400, 450))
            self.assets['cursor'] = self.cargar_y_escalar(ruta_finales + "ui_cursor.png", (30, 30))
            
            # Proyectiles (Lo que se lanza)
            self.assets['proy_disparo'] = self.cargar_y_escalar(ruta_finales + "icono_disparo.png", (64, 64))
            self.assets['proy_molotov'] = self.cargar_y_escalar(ruta_finales + "icono_molotov.png", (64, 64))
            self.assets['proy_cuchillo'] = self.cargar_y_escalar(ruta_finales + "icono_cuchillo.png", (64, 64))
            
            # Estados Alterados (Iconos sobre la cabeza)
            self.assets['est_aturdido'] = self.cargar_y_escalar(ruta_finales + "estado_aturdido.png", (100, 100))
            self.assets['est_quemado'] = self.cargar_y_escalar(ruta_finales + "estado_quemado.png", (100, 100))
            self.assets['est_sangrado'] = self.cargar_y_escalar(ruta_finales + "estado_sangrado.png", (100, 100))

        except pygame.error as e:
            print(f"Error cargando imágenes: {e}")

    def cargar_y_escalar(self, ruta, tamano):
        """
        Función auxiliar de seguridad. 
        Si falta una imagen, crea un cuadro rosa en vez de cerrar el juego.
        """
        try:
            img = pygame.image.load(ruta).convert_alpha()
            return pygame.transform.scale(img, tamano)
        except:
            print(f"Falta imagen: {ruta}")
            surf = pygame.Surface(tamano)
            surf.fill((255, 0, 255)) # Color Rosa Mágico (Placeholder)
            return surf

    def cargar_todos_los_assets(self):
        """Carga fondos específicos de niveles definidos en config.py"""
        self.assets["fondo_menu"] = self.assets['fondo']
        try:
            self.assets["fondo_n1"] = pygame.image.load(f"sprites_jhon/{config.NIVELES[0]['fondo']}").convert()
            self.assets["fondo_n1"] = pygame.transform.scale(self.assets["fondo_n1"], (config.ANCHO, config.ALTO))
        except:
            self.assets["fondo_n1"] = self.assets['fondo']

    # ==========================================
    # FUNCIONES DE DIBUJADO (RENDER)
    # ==========================================

    def dibujar_menu(self):
        """Pantalla de inicio"""
        self.pantalla.blit(self.assets["fondo_menu"], (0, 0))
        texto = self.fuente_grande.render("PRESIONA ENTER PARA EMPEZAR", True, (255, 255, 255))
        rect_texto = texto.get_rect(center=(config.ANCHO//2, config.ALTO - 100))
        self.pantalla.blit(texto, rect_texto)

    def dibujar_interfaz(self, p1, p2, boss, frase_log, sprite_boss_override=None):
        """
        Dibuja toda la escena de batalla.
        [MODIFICACIÓN]: Aquí se cambian las coordenadas (X, Y) de los personajes.
        """
        self.pantalla.blit(self.assets['fondo'], (0, 0))
        
        # --- DIBUJAR PERSONAJES ---
        # (X, Y) -> (Izquierda/Derecha, Arriba/Abajo)
        self.pantalla.blit(self.assets['jugador1'], (150, 480)) # Jugador 1 a la izquierda
        self.pantalla.blit(self.assets['jugador2'], (300, 480)) # Jugador 2 un poco más al centro
        
        # --- DIBUJAR BOSS ---
        # Si 'sprite_boss_override' tiene valor (ej: está atacando), dibujamos ese sprite.
        # Si no, dibujamos el sprite normal (idle).
        if sprite_boss_override:
            self.pantalla.blit(sprite_boss_override, (850, 400))
        else:
            self.pantalla.blit(self.assets['boss_idle'], (850, 400))
        
        # --- DIBUJAR CAJA DE TEXTO ---
        pos_caja = (190, 580)
        self.pantalla.blit(self.assets['caja_texto'], pos_caja)
        
        # --- LÓGICA DE TEXTO MULTILÍNEA ---
        # Separamos el mensaje cada vez que encontramos el símbolo '\n' (Enter)
        lineas = frase_log.split('\n')
        
        for i, linea in enumerate(lineas):
            txt = self.fuente_log.render(linea, True, (0, 0, 0)) # Texto en Negro
            # 'i * 22' significa que cada línea baja 22 píxeles respecto a la anterior.
            self.pantalla.blit(txt, (pos_caja[0] + 60, pos_caja[1] + 20 + (i * 22)))

    def dibujar_barras_vida(self, p1, p2, boss):
        """Muestra los números de HP en la parte superior"""
        txt_p1 = self.fuente_ui.render(f"{p1.nombre}: {p1.vida_actual}/{p1.vida_max}", True, (255, 255, 255))
        self.pantalla.blit(txt_p1, (50, 30))
        
        txt_p2 = self.fuente_ui.render(f"{p2.nombre}: {p2.vida_actual}/{p2.vida_max}", True, (255, 255, 255))
        self.pantalla.blit(txt_p2, (50, 70))
        
        txt_boss = self.fuente_ui.render(f"{boss.nombre}: {boss.vida_actual}/{boss.vida_max}", True, (255, 0, 0))
        self.pantalla.blit(txt_boss, (config.ANCHO - 300, 30))

    def dibujar_menu_pausa(self, indice_seleccionado, mostrar_confirmacion=False):
        """Dibuja el recuadro gris transparente y las opciones"""
        # 1. Crear fondo oscuro transparente
        sombra = pygame.Surface((config.ANCHO, config.ALTO))
        sombra.set_alpha(128) # Transparencia (0 invisible - 255 solido)
        sombra.fill((0, 0, 0))
        self.pantalla.blit(sombra, (0, 0))

        # 2. Dibujar imagen del menú
        pos_menu = (config.ANCHO // 2 - 200, config.ALTO // 2 - 225)
        self.pantalla.blit(self.assets['menu_pausa'], pos_menu)

        # 3. Dibujar opciones de texto
        for i, opcion in enumerate(config.OPCIONES_PAUSA):
            color = (255, 255, 255)
            txt = self.fuente_ui.render(opcion, True, color)
            pos_txt = (pos_menu[0] + 120, pos_menu[1] + 100 + (i * 80))
            self.pantalla.blit(txt, pos_txt)

            # Dibujar el cursor (flechita) al lado de la opción seleccionada
            if i == indice_seleccionado:
                self.pantalla.blit(self.assets['cursor'], (pos_txt[0] - 40, pos_txt[1]))

        # 4. Mensaje "Partida Guardada"
        if mostrar_confirmacion:
            caja = pygame.transform.scale(self.assets['caja_texto'], (400, 80))
            pos_aviso = (config.ANCHO // 2 - 200, config.ALTO - 150)
            self.pantalla.blit(caja, pos_aviso)
            txt_aviso = self.fuente_log.render("¡PARTIDA GUARDADA!", True, (0, 0, 0))
            self.pantalla.blit(txt_aviso, (pos_aviso[0] + 100, pos_aviso[1] + 25))

    # ==========================================
    # ANIMACIONES
    # ==========================================

    def animar_proyectil(self, p1, p2, boss, log, origen_pos, destino_pos, key_imagen):
        """
        Mueve una imagen pequeña desde el punto A al punto B.
        [MODIFICACIÓN]: Cambien el número '20' en el 'range' para cambiar la velocidad.
        - Menos de 20: Más rápido (teletransportación).
        - Más de 20: Más lento (matrix).
        """
        x, y = origen_pos
        # Calculamos cuánto debe moverse en X y Y en cada paso
        dx = (destino_pos[0] - origen_pos[0]) / 20
        dy = (destino_pos[1] - origen_pos[1]) / 20
        
        img_proy = self.assets.get(key_imagen, self.assets['proy_disparo'])

        for _ in range(20): # Repetir 20 veces
            # Redibujamos todo el fondo para que no quede la estela del proyectil
            self.dibujar_interfaz(p1, p2, boss, log)
            self.dibujar_barras_vida(p1, p2, boss)
            
            x += dx
            y += dy
            self.pantalla.blit(img_proy, (x, y))
            
            pygame.display.flip()   # Actualizar pantalla
            pygame.time.delay(20)   # Esperar 20 milisegundos

    def animar_impacto(self, p1, p2, boss, log, objetivo_es_boss, tipo_efecto="NORMAL"):
        """
        Muestra la reacción al golpe durante 0.5 segundos.
        - Si el objetivo es el Boss: Cambia su sprite a 'boss_dano'.
        - Si hay efecto (Fuego/Sangre): Dibuja el icono sobre el personaje.
        """
        tiempo_inicio = pygame.time.get_ticks()
        duracion = 500 # Duración en milisegundos (0.5 segundos)
        
        while pygame.time.get_ticks() - tiempo_inicio < duracion:
            # Seleccionamos qué sprite usar para el boss
            sprite_boss = self.assets['boss_dano'] if objetivo_es_boss else None
            
            self.dibujar_interfaz(p1, p2, boss, log, sprite_boss_override=sprite_boss)
            self.dibujar_barras_vida(p1, p2, boss)

            # Seleccionamos el icono de estado
            overlay = None
            if tipo_efecto == "CRITICO": overlay = self.assets['est_aturdido']
            elif tipo_efecto == "FUEGO": overlay = self.assets['est_quemado']
            elif tipo_efecto == "SANGRE": overlay = self.assets['est_sangrado']

            # Dibujamos el icono sobre la cabeza del afectado
            if overlay:
                pos_x = 850 if objetivo_es_boss else 200
                pos_y = 350
                self.pantalla.blit(overlay, (pos_x, pos_y))

            pygame.display.flip()