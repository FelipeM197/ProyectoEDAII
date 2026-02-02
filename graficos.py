import pygame
import os
import config
import time

"""
GESTOR DE GRÁFICOS (FIX FINAL)
------------------------------
- Error de indentación corregido (animar_impacto ahora es parte de la clase).
- Coordenadas de efectos ajustadas para flotar sobre las cabezas (Y=130).
- Soporte visual completo para Soldados y Boss.
"""

class GestorGrafico:
    def __init__(self, pantalla):
        self.pantalla = pantalla
        
        # --- FUENTES ---
        try:
            self.fuente_log = pygame.font.SysFont("Consolas", 19, bold=True) 
            self.fuente_aviso = pygame.font.SysFont("Consolas", 20, bold=True)
        except:
            self.fuente_log = pygame.font.SysFont("Arial", 19, bold=True)
            self.fuente_aviso = pygame.font.SysFont("Arial", 20, bold=True)
            
        self.fuente_ui = pygame.font.SysFont("Arial", 22, bold=True)
        
        # COLORES
        self.VERDE_TERMINAL = (50, 255, 50)
        self.VERDE_OSCURO = (0, 100, 0)
        self.BLANCO = (255, 255, 255)
        self.NEGRO = (0, 0, 0)
        
        self.assets = {}
        self.cargar_recursos()
        self.cargar_todos_los_assets()

    def cargar_recursos(self):
        ruta_img = "sprites_finales/img/"
        try:
            # --- CARGA BÁSICA ---
            img_fondo = pygame.image.load(ruta_img + "escenario.png").convert()
            self.assets['fondo'] = pygame.transform.scale(img_fondo, (config.ANCHO, config.ALTO))
            
            # --- PERSONAJES (300x300) ---
            img_p1 = pygame.image.load(ruta_img + "soldado1.png").convert_alpha()
            self.assets['jugador1'] = pygame.transform.scale(img_p1, (300, 300))
            
            img_p2 = pygame.image.load(ruta_img + "soldado2.png").convert_alpha()
            self.assets['jugador2'] = pygame.transform.scale(img_p2, (300, 300))
            
            img_boss = pygame.image.load(ruta_img + "boss_idle.png").convert_alpha()
            self.assets['boss_idle'] = pygame.transform.scale(img_boss, (300, 300))
            
            # --- CAJA DE TEXTO ---
            img_caja = pygame.image.load(ruta_img + "ui_caja_texto.png").convert_alpha()
            self.assets['caja_texto'] = pygame.transform.scale(img_caja, (1100, 200))

            # --- UI PAUSA Y CURSOR ---
            self.assets['menu_pausa'] = self.cargar_y_escalar(ruta_img + "ui_menu_pausa.png", (400, 450))
            self.assets['cursor'] = self.cargar_y_escalar(ruta_img + "ui_cursor.png", (30, 30))

            # --- RESTO DE ASSETS ---
            self.assets['boss_dano'] = self.cargar_y_escalar(ruta_img + "boss_dano.png", (300, 300))
            self.assets['boss_atacando'] = self.cargar_y_escalar(ruta_img + "boss_atacando.png", (300, 300))
            
            # Iconos y efectos
            self.assets['proy_disparo'] = self.cargar_y_escalar(ruta_img + "icono_disparo.png", (64, 64))
            self.assets['proy_molotov'] = self.cargar_y_escalar(ruta_img + "icono_molotov.png", (64, 64))
            self.assets['proy_cuchillo'] = self.cargar_y_escalar(ruta_img + "icono_cuchillo.png", (64, 64))
            self.assets['est_aturdido'] = self.cargar_y_escalar(ruta_img + "estado_aturdido.png", (100, 100))
            self.assets['est_quemado'] = self.cargar_y_escalar(ruta_img + "estado_quemado.png", (100, 100))
            self.assets['est_sangrado'] = self.cargar_y_escalar(ruta_img + "estado_sangrado.png", (100, 100))

        except Exception as e:
            print(f"Error cargando: {e}")

    def cargar_y_escalar(self, ruta, tamano):
        try:
            return pygame.transform.scale(pygame.image.load(ruta).convert_alpha(), tamano)
        except:
            s = pygame.Surface(tamano)
            s.fill((255,0,255))
            return s

    def cargar_todos_los_assets(self):
        self.assets["fondo_menu"] = self.assets['fondo']

    # ==========================================
    # DIBUJADO DE LA BATALLA
    # ==========================================

    def dibujar_interfaz(self, p1, p2, boss, frase_log, sprite_boss_override=None, esperando_espacio=False):
        # 1. Fondo
        self.pantalla.blit(self.assets['fondo'], (0, 0))
        
        # 2. Personajes
        # Posición Y=230 para alinearlos al suelo
        self.pantalla.blit(self.assets['jugador1'], (100, 230)) 
        self.pantalla.blit(self.assets['jugador2'], (350, 230)) 
        
        spr_boss = sprite_boss_override if sprite_boss_override else self.assets['boss_idle']
        self.pantalla.blit(spr_boss, (850, 230)) 
        
        # 3. Caja de Texto
        pos_caja_x = (config.ANCHO - 1100) // 2
        pos_caja_y = config.ALTO - 210
        self.pantalla.blit(self.assets['caja_texto'], (pos_caja_x, pos_caja_y))
        
        # 4. Texto Log
        margen_interno_x = 100
        margen_interno_y = 60
        lineas = frase_log.split('\n')
        for i, linea in enumerate(lineas):
            txt_glow = self.fuente_log.render(linea, True, self.VERDE_OSCURO)
            self.pantalla.blit(txt_glow, (pos_caja_x + margen_interno_x + 1, pos_caja_y + margen_interno_y + 1 + (i * 30)))
            txt = self.fuente_log.render(linea, True, self.VERDE_TERMINAL)
            self.pantalla.blit(txt, (pos_caja_x + margen_interno_x, pos_caja_y + margen_interno_y + (i * 30)))

        # 5. Aviso Espacio
        if esperando_espacio:
            if (pygame.time.get_ticks() // 500) % 2 == 0: 
                aviso = self.fuente_aviso.render(">> PRESS SPACE TO CONTINUE_ ", True, self.VERDE_TERMINAL)
                self.pantalla.blit(aviso, (pos_caja_x + 750, pos_caja_y + 150))

    def dibujar_barras_vida(self, p1, p2, boss):
        self.dibujar_hud(50, 30, 250, 40, p1.nombre, p1.vida_actual, p1.vida_max, self.VERDE_TERMINAL)
        self.dibujar_hud(50, 80, 250, 40, p2.nombre, p2.vida_actual, p2.vida_max, self.VERDE_TERMINAL)
        ROJO_TERMINAL = (255, 50, 50)
        self.dibujar_hud(config.ANCHO - 300, 30, 250, 40, boss.nombre, boss.vida_actual, boss.vida_max, ROJO_TERMINAL, color_borde=ROJO_TERMINAL)

    def dibujar_hud(self, x, y, ancho, alto, nombre, hp_actual, hp_max, color_texto, color_borde=None):
        if color_borde is None: color_borde = self.VERDE_TERMINAL
        bg = pygame.Surface((ancho, alto))
        bg.fill(self.NEGRO)
        pygame.draw.rect(bg, color_borde, (0, 0, ancho, alto), 2)
        self.pantalla.blit(bg, (x, y))
        txt = self.fuente_ui.render(f"{nombre}: {hp_actual}/{hp_max}", True, color_texto)
        rect = txt.get_rect(center=(x + ancho//2, y + alto//2))
        self.pantalla.blit(txt, rect)

    # ==========================================
    # MENÚS Y ANIMACIONES
    # ==========================================

    def dibujar_menu(self):
        self.pantalla.blit(self.assets["fondo_menu"], (0, 0))
        sombra = pygame.Surface((config.ANCHO, 100))
        sombra.set_alpha(150); sombra.fill((0,0,0))
        self.pantalla.blit(sombra, (0, config.ALTO - 150))
        t = pygame.font.SysFont("Arial", 40, bold=True).render("PRESIONA ENTER PARA EMPEZAR", True, self.BLANCO)
        r = t.get_rect(center=(config.ANCHO//2, config.ALTO - 100))
        self.pantalla.blit(t, r)

    def dibujar_menu_pausa(self, indice, guardar_on):
        sombra = pygame.Surface((config.ANCHO, config.ALTO))
        sombra.set_alpha(128); sombra.fill((0, 0, 0))
        self.pantalla.blit(sombra, (0, 0))
        pos_menu_x = config.ANCHO // 2 - 200
        pos_menu_y = config.ALTO // 2 - 225
        self.pantalla.blit(self.assets['menu_pausa'], (pos_menu_x, pos_menu_y))
        start_y_text = pos_menu_y + 150
        spacing = 80
        for i, opcion in enumerate(config.OPCIONES_PAUSA):
            color = self.BLANCO
            txt = self.fuente_ui.render(opcion, True, color)
            pos_txt = (pos_menu_x + 120, start_y_text + i * spacing)
            self.pantalla.blit(txt, pos_txt)
            if i == indice:
                self.pantalla.blit(self.assets['cursor'], (pos_txt[0] - 40, pos_txt[1]))
        if guardar_on:
             aviso = self.fuente_ui.render("¡PARTIDA GUARDADA!", True, self.VERDE_TERMINAL)
             rect_aviso = aviso.get_rect(center=(config.ANCHO//2, pos_menu_y + 400))
             self.pantalla.blit(aviso, rect_aviso)

    def animar_proyectil(self, p1, p2, boss, log, origen, destino, key_img):
        x, y = origen
        dx = (destino[0] - origen[0]) / 20
        dy = (destino[1] - origen[1]) / 20
        img = self.assets.get(key_img, self.assets['proy_disparo'])
        for _ in range(20):
            self.dibujar_interfaz(p1, p2, boss, log)
            self.dibujar_barras_vida(p1, p2, boss)
            x += dx; y += dy
            self.pantalla.blit(img, (x,y))
            pygame.display.flip()
            pygame.time.delay(20)

    # [CORRECCIÓN] Esta función ahora está DENTRO de la clase (identada)
    def animar_impacto(self, p1, p2, boss, log, objetivo_real, tipo_efecto):
        """
        Dibuja el efecto (Fuego, Sangre, Aturdido) ENCIMA de la cabeza del objetivo.
        """
        start = pygame.time.get_ticks()
        
        # --- CÁLCULO DE POSICIONES PARA EFECTOS ---
        # Personajes están en Y=230 y miden 300px de alto.
        # Queremos que el efecto flote sobre sus cabezas (aprox Y=130).
        # Centramos X respecto a la imagen del personaje (ancho 300).
        
        pos_efecto = (0, 0)
        sprite_boss = None

        if objetivo_real == boss:
            # Boss X=850. Centro=1000. Efecto(100px) -> X=950.
            pos_efecto = (950, 130)
            sprite_boss = self.assets['boss_dano']
        elif objetivo_real == p1:
            # P1 X=100. Centro=250. Efecto -> X=200.
            pos_efecto = (200, 130)
        elif objetivo_real == p2:
            # P2 X=350. Centro=500. Efecto -> X=450.
            pos_efecto = (450, 130)
        else:
            # Fallback
            pos_efecto = (500, 130)

        while pygame.time.get_ticks() - start < 500:
            self.dibujar_interfaz(p1, p2, boss, log, sprite_boss_override=sprite_boss)
            self.dibujar_barras_vida(p1, p2, boss)
            
            overlay = None
            if tipo_efecto == "CRITICO": overlay = self.assets['est_aturdido']
            elif tipo_efecto == "FUEGO": overlay = self.assets['est_quemado']
            elif tipo_efecto == "SANGRE": overlay = self.assets['est_sangrado']
            elif tipo_efecto == "CURACION": overlay = self.assets['est_aturdido'] # Opcional
            
            if overlay:
                self.pantalla.blit(overlay, pos_efecto)
                
            pygame.display.flip()