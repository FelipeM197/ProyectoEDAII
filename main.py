import pygame
import sys
import random
import config
from graficos import GestorGrafico
from entidades import Personaje
from estructuras import ArbolAtaque, GrafoEfectos

"""
MAIN
----------------------------
1. Para cambiar los controles (Teclas), busquen la sección "GESTIÓN DE EVENTOS".
2. Para cambiar qué pasa cuando ganas/pierdes, busquen la lógica de vida <= 0 (a futuro).
3. Para cambiar el orden de los turnos, busquen "LÓGICA DE TURNOS".
"""

def main():
    # ==========================================
    # 1. INICIALIZACIÓN DE PYGAME
    # ==========================================
    pygame.init()
    
    # Creamos la ventana con el tamaño definido en config.py
    pantalla = pygame.display.set_mode((config.ANCHO, config.ALTO))
    pygame.display.set_caption(config.TITULO)
    
    # El reloj controla los FPS para que el juego no vaya demasiado rápido
    reloj = pygame.time.Clock()
    
    # ==========================================
    # 2. CREACIÓN DE OBJETOS (INSTANCIAS)
    # ==========================================
    motor = GestorGrafico(pantalla)   # El encargado de dibujar
    grafo_estados = GrafoEfectos()    # El encargado de los estados (Quemado, etc.)
    
    # Cargamos los datos del Nivel 1
    datos_nivel = config.NIVELES[0]
    
    # Creamos a los personajes reales usando los moldes de config.py
    p1 = Personaje(config.P1_NOMBRE, config.P1_VIDA_MAX, config.P1_ATAQUE, config.P1_ENERGIA_MAX, config.HABILIDADES_P1)
    p2 = Personaje(config.P2_NOMBRE, config.P2_VIDA_MAX, config.P2_ATAQUE, config.P2_ENERGIA_MAX, config.HABILIDADES_P2)
    jefe = Personaje(datos_nivel["boss_nombre"], datos_nivel["boss_vida"], datos_nivel["boss_ataque"], 100, [])
    
    # ==========================================
    # 3. SISTEMA DE TURNOS (LÓGICA DE EQUIPO)
    # ==========================================
    equipo = [p1, p2]      # Lista con nuestros soldados
    indice_turno = 0       # 0 = Le toca al primero (p1), 1 = Le toca al segundo (p2)
    
    # Variables de Control de Estado (Máquina de Estados del Juego)
    estado = "MENU"            # Puede ser: "MENU", "JUEGO", "GAMEOVER" (Futuro)
    pausado = False            # Si es True, se detiene la lógica y muestra el menú azul
    indice_pausa = 0           # Qué opción del menú de pausa está seleccionada
    mostrar_guardado_timer = 0 # Contador para mostrar el mensaje "Partida Guardada"
    
    # Preparamos el primer mensaje para la caja de texto
    atacante_actual = equipo[indice_turno]
    mensaje_log = f"¡Misión Iniciada!\nTurno: {atacante_actual.nombre}\nPresiona ESPACIO para atacar"
    turno_jugador = True       # True = Nos toca a nosotros. False = Le toca a la IA (Boss).

    # ==========================================
    # 4. BUCLE PRINCIPAL (GAME LOOP)
    # ==========================================
    # Este 'while True' se repite 60 veces por segundo.
    while True:
        
        # --- A. GESTIÓN DE EVENTOS (TECLADO Y RATÓN) ---
        for evento in pygame.event.get():
            # Si le dan a la X de la ventana, cerrar todo.
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            # Detectar teclas presionadas
            if evento.type == pygame.KEYDOWN:
                
                # --- LÓGICA DEL MENÚ PRINCIPAL ---
                if estado == "MENU":
                    if evento.key == pygame.K_RETURN: # Tecla ENTER
                        estado = "JUEGO"
                
                # --- LÓGICA DURANTE LA BATALLA ---
                elif estado == "JUEGO":
                    # [MODIFICACIÓN]: Cambiar 'K_p' si quieren otra tecla para pausar.
                    if evento.key == pygame.K_p:
                        pausado = not pausado
                    
                    # SI ESTAMOS EN PAUSA (Menú Azul)
                    if pausado:
                        if evento.key == pygame.K_UP:
                            # Mueve el cursor arriba (Matemática circular con módulo %)
                            indice_pausa = (indice_pausa - 1) % len(config.OPCIONES_PAUSA)
                        elif evento.key == pygame.K_DOWN:
                            # Mueve el cursor abajo
                            indice_pausa = (indice_pausa + 1) % len(config.OPCIONES_PAUSA)
                        elif evento.key == pygame.K_RETURN:
                            # Ejecutar la opción seleccionada
                            seleccion = config.OPCIONES_PAUSA[indice_pausa]
                            
                            if seleccion == "CONTINUAR":
                                pausado = False
                            elif seleccion == "GUARDAR":
                                # Crea un archivo de texto simple con la vida actual
                                with open("partida_guardada.txt", "w") as f:
                                    f.write(f"P1_HP:{p1.vida_actual}\nBOSS_HP:{jefe.vida_actual}")
                                mostrar_guardado_timer = 90 # Muestra el mensaje por 1.5 seg
                            elif seleccion == "SALIR":
                                pygame.quit()
                                sys.exit()
                    
                    # SI ES TURNO DEL JUGADOR (Y NO ESTÁ PAUSADO)
                    elif turno_jugador:
                        # [MODIFICACIÓN]: Cambiar 'K_SPACE' si quieren atacar con otra tecla.
                        if evento.key == pygame.K_SPACE:
                            
                            # 1. Identificar quién ataca
                            atacante = equipo[indice_turno]
                            
                            # Calcular desde dónde sale el disparo (Estética)
                            # Si es P1 sale de la izq (200), si es P2 sale más al centro (350)
                            origen_proyectil = (200, 500) if atacante == p1 else (350, 500)
                            
                            # 2. Animación Visual (Bala viajando)
                            motor.animar_proyectil(p1, p2, jefe, mensaje_log, origen_proyectil, (900, 450), 'proy_disparo')
                            
                            # 3. Lógica Matemática (Árbol de Decisión en estructuras.py)
                            resultado = ArbolAtaque.ejecutar_ataque(atacante.ataque_base)
                            
                            # 4. Procesar el Resultado
                            if resultado.tipo == "TROPIEZO":
                                # Fallo crítico: El jugador se hiere a sí mismo
                                atacante.recibir_dano(resultado.dano)
                                mensaje_log = f"Turno: {atacante.nombre}\nIntenta atacar pero tropieza\nSe causa {resultado.dano} de daño a sí mismo"
                                
                                # Animación de Sangre sobre el jugador
                                motor.animar_impacto(p1, p2, jefe, mensaje_log, objetivo_es_boss=False, tipo_efecto="SANGRE")
                            else:
                                # Éxito: El Boss recibe daño
                                jefe.recibir_dano(resultado.dano)
                                mensaje_log = f"Turno: {atacante.nombre}\nAtaca con su arma\nCausa {resultado.dano} de daño a {jefe.nombre}"
                                
                                # Animación de golpe sobre el Boss (Crítico o Normal)
                                tipo_visual = "CRITICO" if resultado.tipo == "CRITICO" else "NORMAL"
                                motor.animar_impacto(p1, p2, jefe, mensaje_log, objetivo_es_boss=True, tipo_efecto=tipo_visual)
                            
                            # 5. FINALIZAR TURNO
                            # Rotamos al siguiente jugador: (0 + 1) % 2 = 1 -> (1 + 1) % 2 = 0
                            indice_turno = (indice_turno + 1) % 2 
                            
                            # Le pasamos la pelota a la IA
                            turno_jugador = False

        # --- B. TURNO DEL BOSS (INTELIGENCIA ARTIFICIAL) ---
        if estado == "JUEGO" and not turno_jugador and not pausado:
            # Esperamos medio segundo para que no sea instantáneo
            pygame.time.delay(500) 
            
            # 1. Fase de Preparación (Aviso Visual)
            mensaje_log = f"Turno: {jefe.nombre}\nPreparando ataque..."
            
            # Mostramos al Boss en pose de ataque
            motor.dibujar_interfaz(p1, p2, jefe, mensaje_log, sprite_boss_override=motor.assets['boss_atacando'])
            motor.dibujar_barras_vida(p1, p2, jefe)
            pygame.display.flip() # Actualizar pantalla forzosamente
            pygame.time.delay(1000) # Tiempo para leer "Preparando..."

            # 2. Fase de Decisión (A quién atacar)
            objetivo = random.choice([p1, p2]) # Elige al azar entre P1 y P2
            
            mensaje_log = f"Turno: {jefe.nombre}\nLanza un coctel molotov a {objetivo.nombre}\nCausa {jefe.ataque_base} de daño"

            # Animación del proyectil enemigo
            motor.animar_proyectil(p1, p2, jefe, mensaje_log, (850, 400), (200, 500), 'proy_molotov')

            # 3. Aplicar Daño matemático
            objetivo.recibir_dano(jefe.ataque_base)
            
            # 4. Animación de Impacto (Fuego sobre el jugador)
            motor.animar_impacto(p1, p2, jefe, mensaje_log, objetivo_es_boss=False, tipo_efecto="FUEGO")
            
            # 5. Pausa de Lectura
            pygame.time.delay(1500) # Tiempo para leer cuánto daño nos hizo
            
            # 6. Devolver el control al jugador
            siguiente_jugador = equipo[indice_turno]
            mensaje_log = f"Turno: {siguiente_jugador.nombre}\n¡Es tu oportunidad!\nPresiona ESPACIO para atacar"
            
            turno_jugador = True 

        # --- C. RENDERIZADO GENERAL (DIBUJAR TODO) ---
        if estado == "MENU":
            motor.dibujar_menu()
            
        elif estado == "JUEGO":
            # Dibujar la batalla normal
            motor.dibujar_interfaz(p1, p2, jefe, mensaje_log)
            motor.dibujar_barras_vida(p1, p2, jefe)
            
            # Si está pausado, dibujar el menú azul encima
            if pausado:
                motor.dibujar_menu_pausa(indice_pausa, mostrar_guardado_timer > 0)
                # Temporizador para quitar el mensaje de "Guardado"
                if mostrar_guardado_timer > 0:
                    mostrar_guardado_timer -= 1

        # Actualizar la ventana completa con lo que acabamos de dibujar
        pygame.display.flip()
        
        # Mantener los 60 FPS estables
        reloj.tick(config.FPS)

# Esto asegura que el juego solo arranque si ejecutamos este archivo directamente
if __name__ == "__main__":
    main()