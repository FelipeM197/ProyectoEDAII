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
    
    # --- VARIABLES DE CONTROL DE FLUJO ---
    efectos_ya_procesados = False
    jugador_perdio_turno = False
    boss_perdio_turno = False     
    ataque_realizado = False      
    
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
                    # --- PAUSA ---
                    if evento.key == pygame.K_p:
                        pausado = not pausado

                    if pausado:
                        if evento.key == pygame.K_UP: indice_pausa = (indice_pausa - 1) % 3
                        elif evento.key == pygame.K_DOWN: indice_pausa = (indice_pausa + 1) % 3
                        elif evento.key == pygame.K_RETURN:
                            sel = config.OPCIONES_PAUSA[indice_pausa]
                            if sel == "CONTINUAR": pausado = False
                            elif sel == "SALIR": pygame.quit(); sys.exit()
                            elif sel == "GUARDAR": mostrar_guardado_timer = 90
                    
                    else:
                        # CASO A: Estamos leyendo texto (Esperando Espacio)
                        if esperando_continuar:
                            if evento.key == pygame.K_SPACE:
                                esperando_continuar = False
                                
                                # --- LÓGICA MAESTRA DE CAMBIO DE TURNO ---
                                if turno_jugador: 
                                    # Si ya atacamos O perdimos turno -> Le toca al Boss
                                    if ataque_realizado or jugador_perdio_turno:
                                        turno_jugador = False
                                        efectos_ya_procesados = False 
                                        ataque_realizado = False
                                        boss_perdio_turno = False
                                    else:
                                        # [CORRECCIÓN VISUAL] 
                                        # Si NO hemos atacado (solo leímos efectos), refrescamos el menú
                                        # para que el jugador sepa que puede atacar.
                                        atacante = equipo[indice_turno]
                                        mensaje_log = f"Turno: {atacante.nombre}\nElige tu acción:\n{obtener_texto_habilidades(atacante)}"

                                else: 
                                    # Turno del Boss
                                    if ataque_realizado or boss_perdio_turno:
                                        # Fin turno Boss -> Turno Jugador
                                        indice_turno = (indice_turno + 1) % 2
                                        atacante_actual = equipo[indice_turno]
                                        turno_jugador = True
                                        
                                        efectos_ya_procesados = False 
                                        ataque_realizado = False
                                        jugador_perdio_turno = False
                                        
                                        mensaje_log = f"Turno: {atacante_actual.nombre}\nElige tu acción:\n{obtener_texto_habilidades(atacante_actual)}"
                                    else:
                                        pass
                        
                        # CASO B: Turno del Jugador (Inputs)
                        elif turno_jugador and not jugador_perdio_turno and not ataque_realizado:
                            atacante = equipo[indice_turno]
                            habilidad = None
                            
                            if evento.key == pygame.K_1: habilidad = atacante.habilidades[0]
                            elif evento.key == pygame.K_2: habilidad = atacante.habilidades[1]
                            elif evento.key == pygame.K_3: habilidad = atacante.habilidades[2]
                            elif evento.key == pygame.K_4 and len(atacante.habilidades) > 3:
                                habilidad = atacante.habilidades[3]
                            elif evento.key == pygame.K_5 and len(atacante.habilidades) > 4:
                                habilidad = atacante.habilidades[4]
                            
                            if habilidad:
                                mensaje_log = combate.ejecutar_habilidad(atacante, jefe, habilidad, p1, p2, jefe)
                                ataque_realizado = True 
                                esperando_continuar = True

        # --- B. PROCESAR EFECTOS (FUERA DE EVENTOS) ---
        if estado == "JUEGO" and not pausado and not esperando_continuar and not efectos_ya_procesados:
            
            personaje_a_evaluar = equipo[indice_turno] if turno_jugador else jefe
            
            pierde_turno, msg_efectos = combate.procesar_efectos_pasivos(p1, p2, jefe, personaje_a_evaluar)
            
            efectos_ya_procesados = True
            
            if turno_jugador:
                jugador_perdio_turno = pierde_turno
            else:
                boss_perdio_turno = pierde_turno
            
            if msg_efectos:
                mensaje_log = msg_efectos
                motor.dibujar_interfaz(p1, p2, jefe, mensaje_log, esperando_espacio=True)
                pygame.display.flip()
                pygame.time.delay(500)
                esperando_continuar = True 
                
                if pierde_turno:
                    mensaje_log += "\n(Aturdido: Pierde turno)"

        # --- C. LÓGICA DE IA DEL BOSS ---
        if estado == "JUEGO" and not turno_jugador and not pausado and not esperando_continuar and not ataque_realizado:
            
            if boss_perdio_turno:
                pass 
            else:
                pygame.time.delay(500)
                mensaje_log = f"Turno: {jefe.nombre}\nPreparando ataque..."
                motor.dibujar_interfaz(p1, p2, jefe, mensaje_log, sprite_boss_override=motor.assets['boss_atacando'])
                motor.dibujar_barras_vida(p1, p2, jefe)
                pygame.display.flip()
                pygame.time.delay(800)

                objetivo = random.choice([p1, p2])
                msg_ataque = f"Turno: {jefe.nombre}\nLanza ataque a {objetivo.nombre}"
                
                origen_disparo = (950, 200)
                destino_disparo = (250, 380) if objetivo == p1 else (500, 380)

                motor.animar_proyectil(p1, p2, jefe, msg_ataque, origen_disparo, destino_disparo, 'proy_molotov')
                
                res = objetivo.recibir_dano(jefe.ataque_base)
                msg_final = f"{msg_ataque}\nDaño recibido: {jefe.ataque_base}"
                if isinstance(res, str): msg_final += f"\n{res}"
                
                # Jefe aplica efectos
                evento_boss = "fuego" 
                nuevo_estado_jugador = grafo_estados.transicion(objetivo.estado_actual, evento_boss)
                
                if nuevo_estado_jugador != objetivo.estado_actual:
                    objetivo.estado_actual = nuevo_estado_jugador
                    if nuevo_estado_jugador == "Quemado":
                        objetivo.turnos_quemado = config.DURACION_QUEMADO
                        
                    msg_final += f"\n¡{objetivo.nombre} ahora está {nuevo_estado_jugador}!"

                motor.animar_impacto(p1, p2, jefe, msg_final, objetivo, "FUEGO")
                
                mensaje_log = msg_final
                ataque_realizado = True 
                esperando_continuar = True

        # --- D. DIBUJADO ---
        if estado == "MENU": 
            motor.dibujar_menu()
        elif estado == "JUEGO":
            motor.dibujar_interfaz(p1, p2, jefe, mensaje_log, esperando_espacio=esperando_continuar)
            motor.dibujar_barras_vida(p1, p2, jefe)
            if pausado: 
                motor.dibujar_menu_pausa(indice_pausa, mostrar_guardado_timer > 0)

        pygame.display.flip()
        reloj.tick(config.FPS)

if __name__ == "__main__":
    main()