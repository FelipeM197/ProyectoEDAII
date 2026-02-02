import pygame
import sys
import random
import config
from graficos import GestorGrafico
from entidades import Personaje
from estructuras import GrafoEfectos
from sistema_combate import ControladorCombate

def obtener_texto_habilidades(personaje):
    nombres = [f"{i+1}:{h.nombre}" for i, h in enumerate(personaje.habilidades)]
    return "   ".join(nombres)

def main():
    pygame.init()
    pantalla = pygame.display.set_mode((config.ANCHO, config.ALTO))
    pygame.display.set_caption(config.TITULO)
    reloj = pygame.time.Clock()
    
    motor = GestorGrafico(pantalla)
    grafo_estados = GrafoEfectos()
    combate = ControladorCombate(grafo_estados, motor)
    
    datos_nivel = config.NIVELES[0]
    p1 = Personaje(config.P1_NOMBRE, config.P1_VIDA_MAX, config.P1_ATAQUE, config.P1_ENERGIA_MAX, config.HABILIDADES_P1)
    p2 = Personaje(config.P2_NOMBRE, config.P2_VIDA_MAX, config.P2_ATAQUE, config.P2_ENERGIA_MAX, config.HABILIDADES_P2)
    jefe = Personaje(datos_nivel["boss_nombre"], datos_nivel["boss_vida"], datos_nivel["boss_ataque"], 100, [])
    
    equipo = [p1, p2]
    indice_turno = 0
    estado = "MENU"
    pausado = False
    
    esperando_continuar = False 
    
    atacante_actual = equipo[indice_turno]
    mensaje_log = f"¡Misión Iniciada!\nTurno: {atacante_actual.nombre}\n{obtener_texto_habilidades(atacante_actual)}"
    turno_jugador = True
    
    indice_pausa = 0
    mostrar_guardado_timer = 0

    while True:
        # --- A. CONTROL DE EVENTOS ---
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            
            if evento.type == pygame.KEYDOWN:
                # 1. MENU PRINCIPAL
                if estado == "MENU":
                    if evento.key == pygame.K_RETURN: estado = "JUEGO"
                
                # 2. JUEGO
                elif estado == "JUEGO":
                    
                    # --- [PRIORIDAD ABSOLUTA] DETECTAR PAUSA ---
                    # Esto se revisa ANTES de saber si estamos esperando espacio o atacando
                    if evento.key == pygame.K_p:
                        pausado = not pausado

                    # --- SI EL JUEGO ESTÁ PAUSADO: CONTROLAR MENÚ AZUL ---
                    if pausado:
                        if evento.key == pygame.K_UP: indice_pausa = (indice_pausa - 1) % 3
                        elif evento.key == pygame.K_DOWN: indice_pausa = (indice_pausa + 1) % 3
                        elif evento.key == pygame.K_RETURN:
                            sel = config.OPCIONES_PAUSA[indice_pausa]
                            if sel == "CONTINUAR": pausado = False
                            elif sel == "SALIR": pygame.quit(); sys.exit()
                            elif sel == "GUARDAR": mostrar_guardado_timer = 90
                    
                    # --- SI NO ESTÁ PAUSADO: CONTROLAR JUEGO ---
                    else:
                        # CASO A: Estamos leyendo texto (Esperando Espacio)
                        if esperando_continuar:
                            if evento.key == pygame.K_SPACE:
                                esperando_continuar = False
                                
                                if turno_jugador: 
                                    turno_jugador = False
                                else: 
                                    indice_turno = (indice_turno + 1) % 2
                                    atacante_actual = equipo[indice_turno]
                                    turno_jugador = True
                                    mensaje_log = f"Turno: {atacante_actual.nombre}\nElige tu acción:\n{obtener_texto_habilidades(atacante_actual)}"
                        
                        # CASO B: Turno del Jugador (Elegir Habilidad)
                        elif turno_jugador:
                            atacante = equipo[indice_turno]
                            habilidad = None
                            
                            # Teclas 1, 2, 3, 4
                            if evento.key == pygame.K_1: habilidad = atacante.habilidades[0]
                            elif evento.key == pygame.K_2: habilidad = atacante.habilidades[1]
                            elif evento.key == pygame.K_3: habilidad = atacante.habilidades[2]
                            elif evento.key == pygame.K_4 and len(atacante.habilidades) > 3:
                                habilidad = atacante.habilidades[3]
                                
                            if habilidad:
                                mensaje_log = combate.ejecutar_habilidad(atacante, jefe, habilidad, p1, p2, jefe)
                                esperando_continuar = True

        # --- B. LÓGICA DEL BOSS ---
        # Solo actúa si NO está pausado y NO estamos leyendo texto
        if estado == "JUEGO" and not turno_jugador and not pausado and not esperando_continuar:
            pygame.time.delay(500)
            
            # 1. Efectos Pasivos
            pierde_turno, msg_efectos = combate.procesar_efectos_pasivos(p1, p2, jefe)
            
            if pierde_turno:
                mensaje_log = f"{msg_efectos}\n(El Boss pierde su turno)"
                esperando_continuar = True 
            else:
                if msg_efectos:
                    mensaje_log = msg_efectos
                    motor.dibujar_interfaz(p1, p2, jefe, mensaje_log, esperando_espacio=True)
                    pygame.display.flip()
                    pygame.time.delay(1500) 

                # 2. Ataque
                mensaje_log = f"Turno: {jefe.nombre}\nPreparando ataque..."
                motor.dibujar_interfaz(p1, p2, jefe, mensaje_log, sprite_boss_override=motor.assets['boss_atacando'])
                motor.dibujar_barras_vida(p1, p2, jefe)
                pygame.display.flip()
                pygame.time.delay(800)

                # Selección de Objetivo
                objetivo = random.choice([p1, p2])
                msg_ataque = f"Turno: {jefe.nombre}\nLanza ataque a {objetivo.nombre}"
                
                # Coordenadas ajustadas (Desde arriba de Trump hacia el centro del soldado)
                origen_disparo = (950, 200)
                if objetivo == p1:
                    destino_disparo = (250, 380)
                else:
                    destino_disparo = (500, 380)

                motor.animar_proyectil(p1, p2, jefe, msg_ataque, origen_disparo, destino_disparo, 'proy_molotov')
                
                res = objetivo.recibir_dano(jefe.ataque_base)
                msg_final = f"{msg_ataque}\nDaño recibido: {jefe.ataque_base}"
                if isinstance(res, str): msg_final += f"\n{res}"
                
                motor.animar_impacto(p1, p2, jefe, msg_final, objetivo, "FUEGO")
                
                mensaje_log = msg_final
                esperando_continuar = True

        # --- C. DIBUJADO ---
        if estado == "MENU": 
            motor.dibujar_menu()
        elif estado == "JUEGO":
            motor.dibujar_interfaz(p1, p2, jefe, mensaje_log, esperando_espacio=esperando_continuar)
            motor.dibujar_barras_vida(p1, p2, jefe)
            
            # Si está pausado, dibujamos el menú ENCIMA de todo lo demás
            if pausado: 
                motor.dibujar_menu_pausa(indice_pausa, mostrar_guardado_timer > 0)

        pygame.display.flip()
        reloj.tick(config.FPS)

if __name__ == "__main__":
    main()