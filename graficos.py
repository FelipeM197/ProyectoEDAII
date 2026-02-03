import pygame
import config
from recursos import AlmacenRecursos 

"""
GESTOR DE GRÁFICOS
------------------
Este módulo es el artista del equipo. Su única responsabilidad es recibir datos
y dibujar píxeles en la pantalla. No calcula daño ni decide quién gana, solo pinta.

Separamos la lógica de "dibujar" de la lógica de "cargar imágenes" (que está en recursos.py)
para que el código sea más ordenado y la memoria se gestione mejor.

INDICE RÁPIDO:
--------------
Línea 26  -> Configuración inicial y carga de assets
Línea 50  -> dibujar_interfaz (El ciclo principal de renderizado)
Línea 118 -> Sistema de HUD (Barras de vida y energía)
Línea 139 -> Pantallas de Menú, Victoria y Derrota
Línea 174 -> Animaciones (Proyectiles e Impactos)
"""

class GestorGrafico:
    def __init__(self, pantalla):
        self.pantalla = pantalla
        
        # Instanciamos el almacén de recursos.
        # Esto carga todas las imágenes en memoria RAM una sola vez al iniciar.
        self.almacen = AlmacenRecursos()
        
        # Creamos un alias o acceso directo al diccionario de assets.
        # Hacemos esto para escribir menos código luego: en vez de llamar a
        # self.almacen.assets['algo'] cada vez, solo usamos self.assets['algo'].
        self.assets = self.almacen.assets
        
        # Configuración de tipografías.
        # Usamos un bloque try-except para que el juego no se rompa si el sistema
        # operativo no tiene la fuente "Consolas". Si falla, usamos "Arial".
        try:
            self.fuente_log = pygame.font.SysFont("Consolas", 19, bold=True) 
            self.fuente_aviso = pygame.font.SysFont("Consolas", 20, bold=True)
        except:
            self.fuente_log = pygame.font.SysFont("Arial", 19, bold=True)
            self.fuente_aviso = pygame.font.SysFont("Arial", 20, bold=True)
        self.fuente_ui = pygame.font.SysFont("Arial", 22, bold=True)
        
        # Definición de paleta de colores para la interfaz (UI).
        self.VERDE_TERMINAL = (50, 255, 50)
        self.VERDE_OSCURO = (0, 100, 0)
        self.BLANCO = (255, 255, 255)
        self.NEGRO = (0, 0, 0)

    # ==========================================
    # DIBUJADO DE LA BATALLA
    # ==========================================
    def dibujar_interfaz(self, p1, p2, boss, frase_log, sprite_boss_override=None, sprite_p1_override=None, sprite_p2_override=None, esperando_espacio=False):
        """
        Esta es la función más importante. Dibuja un fotograma completo del combate.
        
        El concepto de 'override' (sobreescritura) en los argumentos es clave:
        Normalmente dibujamos al personaje en su estado base. Pero si la función de 
        animación nos pasa una imagen específica (ej. cara de dolor), la usamos 
        temporalmente en este cuadro en lugar de la imagen normal.
        """
        
        # 1. Capa de Fondo
        # Siempre dibujamos esto primero para limpiar el frame anterior.
        self.pantalla.blit(self.assets['fondo'], (0, 0))
        
        # 2. Capa de Personajes
        # Aquí decido qué imagen mostrar basándome en la prioridad:
        # Prioridad A: ¿Hay una animación forzada (override)? -> Úsala.
        # Prioridad B: ¿Está muerto (vida <= 0)? -> Usa el sprite de derrota.
        # Prioridad C: Estado normal -> Usa el sprite estándar.
        
        # --- JUGADOR 1 ---
        if sprite_p1_override:
            spr_p1 = sprite_p1_override 
        elif p1.vida_actual <= 0:
            spr_p1 = self.assets['jugador1_dano'] 
        else:
            spr_p1 = self.assets['jugador1'] 
        self.pantalla.blit(spr_p1, (100, 230)) 
        
        # --- JUGADOR 2 ---
        if sprite_p2_override:
            spr_p2 = sprite_p2_override
        elif p2.vida_actual <= 0:
            spr_p2 = self.assets['jugador2_dano']
        else:
            spr_p2 = self.assets['jugador2']
        self.pantalla.blit(spr_p2, (350, 230)) 
        
        # --- BOSS ---
        if sprite_boss_override:
            spr_boss = sprite_boss_override
        elif boss.vida_actual <= 0:
            spr_boss = self.assets['boss_dano'] 
        else:
            spr_boss = self.assets['boss_idle']
        self.pantalla.blit(spr_boss, (850, 230)) 
        
        # --- ESTADOS VISUALES ---
        # Función auxiliar interna para dibujar iconos sobre las cabezas (fuego, aturdimiento).
        # Ayuda a no repetir el mismo código tres veces.
        def dibujar_estado(personaje, x_centro):
            if personaje.vida_actual <= 0:
                return # Si está muerto, limpiamos la interfaz visual sobre él.

            y_icono = 130
            # Verificamos la cadena de texto del estado actual del objeto Personaje
            if personaje.estado_actual == "Quemado":
                self.pantalla.blit(self.assets['est_quemado'], (x_centro, y_icono))
            elif personaje.estado_actual == "Sangrado":
                self.pantalla.blit(self.assets['est_sangrado'], (x_centro, y_icono))
            elif personaje.estado_actual == "Aturdido":
                self.pantalla.blit(self.assets['est_aturdido'], (x_centro, y_icono))
            
            # El escudo es independiente del estado, se dibuja si la pila tiene elementos.
            if len(personaje.pila_escudo) > 0:
                self.pantalla.blit(self.assets['icono_escudo'], (x_centro, y_icono - 40))

        dibujar_estado(p1, 200)
        dibujar_estado(p2, 450)
        dibujar_estado(boss, 950)

        # 3. Interfaz de Usuario (UI) - Caja de Texto
        pos_caja_x = (config.ANCHO - 1100) // 2
        pos_caja_y = config.ALTO - 210
        self.pantalla.blit(self.assets['caja_texto'], (pos_caja_x, pos_caja_y))
        
        # 4. Renderizado del Log de Batalla
        margen_interno_x = 120
        margen_interno_y = 40
        lineas = frase_log.split('\n')

        # Limitamos el texto a las últimas 5 líneas para que no se salga de la caja.
        MAX_LINEAS = 5 
        if len(lineas) > MAX_LINEAS:
            lineas = lineas[-MAX_LINEAS:] 
            
        for i, linea in enumerate(lineas):
            espaciado = 25
            # Efecto de sombra: dibujamos el texto oscuro un píxel desplazado
            # para darle legibilidad sobre el fondo.
            txt_glow = self.fuente_log.render(linea, True, self.VERDE_OSCURO)
            self.pantalla.blit(txt_glow, (pos_caja_x + margen_interno_x + 1, pos_caja_y + margen_interno_y + 1 + (i * espaciado)))
            
            # Texto principal brillante.
            txt = self.fuente_log.render(linea, True, self.VERDE_TERMINAL)
            self.pantalla.blit(txt, (pos_caja_x + margen_interno_x, pos_caja_y + margen_interno_y + (i * espaciado)))

        # 5. Aviso Intermitente "Press Space"
        if esperando_espacio:
            # Usamos el reloj del sistema para crear un parpadeo (on/off) cada 500ms.
            if (pygame.time.get_ticks() // 500) % 2 == 0: 
                aviso = self.fuente_aviso.render(">> PRESS SPACE TO CONTINUE_ ", True, self.VERDE_TERMINAL)
                self.pantalla.blit(aviso, (pos_caja_x + 750, pos_caja_y + 150))

    def dibujar_barras_vida(self, p1, p2, boss):
        """Fachada para llamar al dibujado individual de cada barra."""
        self.dibujar_hud(100, 30, 250, 60, p1, self.VERDE_TERMINAL)
        self.dibujar_hud(100, 100, 250, 60, p2, self.VERDE_TERMINAL)
        
        ROJO_TERMINAL = (255, 50, 50)
        self.dibujar_hud(config.ANCHO - 350, 30, 250, 60, boss, ROJO_TERMINAL, color_borde=ROJO_TERMINAL)

    def dibujar_hud(self, x, y, ancho, alto, personaje, color_texto, color_borde=None):
        """
        Dibuja el rectángulo de estadísticas (Heads Up Display).
        En lugar de usar imágenes, creamos superficies rectangulares por código
        para que sea más fácil ajustar tamaños dinámicamente.
        """
        if color_borde is None: color_borde = self.VERDE_TERMINAL
        
        bg = pygame.Surface((ancho, alto))
        bg.fill(self.NEGRO)
        # Dibujamos solo el borde (width=2)
        pygame.draw.rect(bg, color_borde, (0, 0, ancho, alto), 2)
        
        self.pantalla.blit(bg, (x, y))
        
        fuente_info = pygame.font.SysFont("Arial", 18, bold=True)
        # Renderizamos texto de vida.
        self.pantalla.blit(fuente_info.render(f"{personaje.nombre}: {personaje.vida_actual}/{personaje.vida_max} HP", True, color_texto), (x + 10, y + 8))
        
        AZUL_ENERGIA = (0, 200, 255)
        # Renderizamos texto de energía.
        self.pantalla.blit(fuente_info.render(f"Energía: {personaje.energia_actual}/{personaje.energia_max} EP", True, AZUL_ENERGIA), (x + 10, y + 32))

    # ==========================================
    # PANTALLAS Y ANIMACIONES
    # ==========================================
    def dibujar_victoria(self):
        # Creamos una capa semitransparente (alpha 200) para oscurecer el fondo.
        overlay = pygame.Surface((config.ANCHO, config.ALTO)); overlay.set_alpha(200); overlay.fill((0, 50, 0))
        self.pantalla.blit(overlay, (0, 0))
        
        t = pygame.font.SysFont("Consolas", 60, bold=True).render("¡RESCATASTE A MADURO :D!", True, (100, 255, 100))
        self.pantalla.blit(t, t.get_rect(center=(config.ANCHO//2, 150)))
        
        if 'vip_victoria' in self.assets:
            self.pantalla.blit(self.assets['vip_victoria'], (config.ANCHO//2 - 150, 250))
            
        s = self.fuente_ui.render("Presiona ENTER para Salir", True, self.BLANCO)
        self.pantalla.blit(s, s.get_rect(center=(config.ANCHO//2, 600)))

    def dibujar_derrota(self):
        overlay = pygame.Surface((config.ANCHO, config.ALTO)); overlay.set_alpha(200); overlay.fill((50, 0, 0))
        self.pantalla.blit(overlay, (0, 0))
        
        t = pygame.font.SysFont("Consolas", 60, bold=True).render("¡MISIÓN FALLIDA!", True, (255, 50, 50))
        self.pantalla.blit(t, t.get_rect(center=(config.ANCHO//2, 300)))
        
        s = self.fuente_ui.render("Tus soldados han caído. ENTER para Salir", True, self.BLANCO)
        self.pantalla.blit(s, s.get_rect(center=(config.ANCHO//2, 400)))

    def dibujar_menu(self):
        self.pantalla.blit(self.assets["fondo_menu"], (0, 0))
        
        # Franja negra inferior para que el texto se lea bien sobre cualquier fondo.
        sombra = pygame.Surface((config.ANCHO, 100)); sombra.set_alpha(150); sombra.fill((0,0,0))
        self.pantalla.blit(sombra, (0, config.ALTO - 150))
        
        t = pygame.font.SysFont("Arial", 40, bold=True).render("PRESIONA ENTER PARA EMPEZAR", True, self.BLANCO)
        self.pantalla.blit(t, t.get_rect(center=(config.ANCHO//2, config.ALTO - 100)))

    def dibujar_menu_pausa(self, indice, guardar_on):
        # Oscurecimiento de pantalla.
        sombra = pygame.Surface((config.ANCHO, config.ALTO)); sombra.set_alpha(128); sombra.fill((0, 0, 0))
        self.pantalla.blit(sombra, (0, 0))
        
        px = config.ANCHO // 2 - 200; py = config.ALTO // 2 - 225
        self.pantalla.blit(self.assets['menu_pausa'], (px, py))
        
        # Ciclo para dibujar las opciones del menú.
        start_y = py + 150
        for i, opcion in enumerate(config.OPCIONES_PAUSA):
            pos = (px + 120, start_y + i * 80)
            self.pantalla.blit(self.fuente_ui.render(opcion, True, self.BLANCO), pos)
            
            # Si esta opción es la seleccionada, dibujamos el cursor al lado.
            if i == indice: self.pantalla.blit(self.assets['cursor'], (pos[0]-40, pos[1]))
            
        if guardar_on:
             aviso = self.fuente_ui.render("¡PARTIDA GUARDADA!", True, self.VERDE_TERMINAL)
             self.pantalla.blit(aviso, aviso.get_rect(center=(config.ANCHO//2, py + 400)))

    def animar_proyectil(self, p1, p2, boss, log, origen, destino, key_img):
        """
        Esta función bloquea momentáneamente el juego para reproducir una animación.
        Calculamos una ruta lineal entre origen y destino y movemos la imagen paso a paso.
        """
        x, y = origen
        # Dividimos la distancia en 20 pasos para crear el movimiento.
        dx = (destino[0] - origen[0]) / 20; dy = (destino[1] - origen[1]) / 20
        
        img = self.assets.get(key_img, self.assets['proy_disparo'])
        
        for _ in range(20):
            # Es vital redibujar toda la interfaz en cada paso, si no,
            # el proyectil dejaría un rastro o borraría el fondo.
            self.dibujar_interfaz(p1, p2, boss, log)
            self.dibujar_barras_vida(p1, p2, boss)
            
            x += dx; y += dy
            self.pantalla.blit(img, (x,y))
            
            pygame.display.flip(); pygame.time.delay(20)

    def animar_impacto(self, p1, p2, boss, log, objetivo_real, tipo_efecto):
        """
        Animación de golpe recibido.
        1. Identificamos quién recibe el golpe.
        2. Cambiamos su sprite a uno de 'dolor' (override).
        3. Mostramos un overlay (fuego, sangre, etc) encima.
        """
        start = pygame.time.get_ticks()
        pos_efecto = (0, 0); sprite_boss = None; sprite_p1 = None; sprite_p2 = None

        # Definimos qué efectos cuentan como "daño" para cambiar la cara del personaje.
        # Si te curan o te dan un escudo, no deberías poner cara de dolor.
        es_dano = tipo_efecto not in ["CURACION", "ESCUDO", "MOTIVACION", "FALLO"]

        # Asignación de coordenadas y sprites temporales.
        if objetivo_real == boss:
            pos_efecto = (950, 130)
            if es_dano: sprite_boss = self.assets['boss_dano']
        elif objetivo_real == p1:
            pos_efecto = (200, 130)
            if es_dano: sprite_p1 = self.assets['jugador1_dano']
        elif objetivo_real == p2:
            pos_efecto = (450, 130)
            if es_dano: sprite_p2 = self.assets['jugador2_dano']

        # Primera fase de la animación (con cara de dolor).
        while pygame.time.get_ticks() - start < 500:
            # Aquí pasamos los sprites temporales (override) a dibujar_interfaz.
            self.dibujar_interfaz(p1, p2, boss, log, sprite_boss_override=sprite_boss, sprite_p1_override=sprite_p1, sprite_p2_override=sprite_p2)
            self.dibujar_barras_vida(p1, p2, boss)
            
            # Seleccionamos el icono del efecto visual.
            overlay = None
            if tipo_efecto == "CRITICO": overlay = self.assets['est_aturdido']
            elif tipo_efecto == "FUEGO": overlay = self.assets['est_quemado']
            elif tipo_efecto == "SANGRE": overlay = self.assets['est_sangrado']
            elif tipo_efecto == "CURACION": overlay = self.assets['icono_curar']
            elif tipo_efecto == "ESCUDO": overlay = self.assets['icono_escudo']
            elif tipo_efecto == "MOTIVACION": overlay = self.assets['proy_grito']
            
            if overlay: self.pantalla.blit(overlay, pos_efecto)
            pygame.display.flip()

        # Segunda fase (opcional): Podríamos repetir el bucle para efectos más largos,
        # pero aquí simplemente mantenemos el efecto visual un poco más.
        while pygame.time.get_ticks() - start < 500:
            self.dibujar_interfaz(p1, p2, boss, log, sprite_boss_override=sprite_boss, sprite_p1_override=sprite_p1, sprite_p2_override=sprite_p2)
            self.dibujar_barras_vida(p1, p2, boss)
            overlay = None
            # ... (repite lógica de selección de overlay) ...
            if tipo_efecto == "CRITICO": overlay = self.assets['est_aturdido']
            elif tipo_efecto == "FUEGO": overlay = self.assets['est_quemado']
            elif tipo_efecto == "SANGRE": overlay = self.assets['est_sangrado']
            elif tipo_efecto == "CURACION": overlay = self.assets['icono_curar']
            elif tipo_efecto == "ESCUDO": overlay = self.assets['icono_escudo']
            elif tipo_efecto == "MOTIVACION": overlay = self.assets['proy_grito']
            
            if overlay: self.pantalla.blit(overlay, pos_efecto)
            pygame.display.flip()