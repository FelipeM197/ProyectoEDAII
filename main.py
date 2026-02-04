import pygame
import sys
import random
import config
from graficos import GestorGrafico
from entidades import Personaje, Habilidad, Boss
from estructuras import GrafoEfectos, GrafoEstrategia, GrafoEstados
from sistema_combate import ControladorCombate
from recursos import AlmacenRecursos 

"""
PUNTO DE ENTRADA PRINCIPAL (MAIN LOOP)
--------------------------------------
Aquí es donde ensamblo todas las piezas del rompecabezas.
Este archivo orquesta el bucle infinito del juego, escucha el teclado
y coordina los turnos entre el jugador y la IA.

INDICE RÁPIDO:
--------------
Línea 25  -> Configuración e Inicialización de objetos
Línea 65  -> Bucle Principal (While True)
Línea 70  -> A. Manejo de Eventos (Teclado)
Línea 105 -> Lógica de cambio de turno (La parte difícil)
Línea 155 -> Ejecución de habilidades del jugador
Línea 180 -> B. Condiciones de Victoria/Derrota
Línea 190 -> C. Procesamiento de efectos pasivos (Fuego/Sangrado)
Línea 215 -> D. Inteligencia Artificial del Boss
Línea 250 -> E. Renderizado final
"""

def obtener_texto_habilidades(personaje):
    """
    Pequeña utilidad para formatear el menú de ataques en la caja de texto.
    Crea un string limpio mostrando qué tecla [1, 2, 3...] activa qué poder.
    """
    txt = "[Q] Golpe Táctico (0 EP)\n"
    for i, h in enumerate(personaje.habilidades):
        idx = i + 1
        txt += f"[{idx}] {h.nombre} ({h.costo})   "
        # Salto de línea cada 2 habilidades para que no se salga de la caja.
        if idx % 2 == 0:
            txt += "\n"
    return txt

def main():
    # Iniciamos el motor de Pygame y la ventana.
    pygame.init()
    pantalla = pygame.display.set_mode((config.ANCHO, config.ALTO))
    pygame.display.set_caption(config.TITULO)
    reloj = pygame.time.Clock()
    
    # Instancio mis módulos personalizados.
    # GestorGrafico se encarga de pintar y ControladorCombate de las reglas.
    motor = GestorGrafico(pantalla)
    grafo_estados = GrafoEfectos()
    combate = ControladorCombate(grafo_estados, motor)

    # Instancias de la IA del Jefe
    cerebro_comportamiento = GrafoEstados() 
    cerebro_estrategia = GrafoEstrategia()
    
    # Carga de datos desde el archivo de configuración.
    # Creo los objetos reales (Instancias) usando los moldes de clases.
    datos_nivel = config.NIVELES[0]
    p1 = Personaje(config.P1_NOMBRE, config.P1_VIDA_MAX, config.P1_ATAQUE, config.P1_ENERGIA_MAX, config.HABILIDADES_P1)
    p2 = Personaje(config.P2_NOMBRE, config.P2_VIDA_MAX, config.P2_ATAQUE, config.P2_ENERGIA_MAX, config.HABILIDADES_P2)
    jefe = Boss(datos_nivel["boss_nombre"], datos_nivel["boss_vida"], datos_nivel["boss_ataque"], 100, [])
    
    # Habilidad de emergencia (Tecla Q).
    # La defino aquí 'hardcoded' por seguridad, por si falla la carga externa.
    try:
        atk_basico = Habilidad(config.DATO_BASICO)
    except AttributeError:
        atk_basico = Habilidad({"nombre": "Básico", "dano": 10, "costo": 0, "tipo":"ATAQUE", "desc":"", "icono":"", "efecto_code":"fisico"})

    # Lista para alternar turnos entre mis dos soldados.
    equipo = [p1, p2]
    indice_turno = 0
    
    # Variables de Control de Flujo (State Machine).
    estado = "MENU"      # Puede ser: MENU, JUEGO, VICTORIA, DERROTA
    pausado = False
    
    # Bandera crítica: detiene el juego para que el usuario pueda leer el texto.
    esperando_continuar = False 
    
    # Banderas para controlar qué ya pasó en el turno actual.
    efectos_ya_procesados = False # Ya aplicamos el daño por fuego este turno?
    jugador_perdio_turno = False  # Está aturdido?
    boss_perdio_turno = False     
    ataque_realizado = False      # Ya eligió una acción?
    
    # Preparación del primer turno.
    atacante_actual = equipo[indice_turno]
    mensaje_log = f"¡Misión Iniciada!\nTurno: {atacante_actual.nombre}\n{obtener_texto_habilidades(atacante_actual)}"
    turno_jugador = True
    
    # Variables para la interfaz del menú de pausa.
    indice_pausa = 0
    mostrar_guardado_timer = 0

    while True:
        # --- A. CONTROL DE EVENTOS (TECLADO/RATÓN) ---
        # Aquí capturo todo lo que hace el usuario.
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            
            if evento.type == pygame.KEYDOWN:
                # 1. Lógica del Menú Principal
                if estado == "MENU":
                    if evento.key == pygame.K_RETURN: estado = "JUEGO"
                
                # 2. Pantallas de fin de juego
                elif estado in ["VICTORIA", "DERROTA"]:
                    if evento.key == pygame.K_RETURN:
                        pygame.quit(); sys.exit() # Aquí podría poner un reset()

                # 3. Lógica durante el combate
                elif estado == "JUEGO":
                    # Tecla P para pausar
                    if evento.key == pygame.K_p:
                        pausado = not pausado

                    if pausado:
                        # Navegación en el menú de pausa
                        if evento.key == pygame.K_UP: indice_pausa = (indice_pausa - 1) % 3
                        elif evento.key == pygame.K_DOWN: indice_pausa = (indice_pausa + 1) % 3
                        elif evento.key == pygame.K_RETURN:
                            sel = config.OPCIONES_PAUSA[indice_pausa]
                            if sel == "CONTINUAR": pausado = False
                            elif sel == "SALIR": pygame.quit(); sys.exit()
                            elif sel == "GUARDAR": mostrar_guardado_timer = 90
                    
                    else:
                        # AVANCE DE TEXTO (Barra Espaciadora)
                        # Esta es la parte más importante del ritmo del juego.
                        if esperando_continuar:
                            if evento.key == pygame.K_SPACE:
                                esperando_continuar = False
                                
                                # --- Lógica de Cambio de Turno ---
                                # Si era mi turno y ya ataqué (o estaba aturdido), le toca al Boss.
                                if turno_jugador: 
                                    if ataque_realizado or jugador_perdio_turno:
                                        turno_jugador = False
                                        # Reseteo las banderas para el turno del Boss
                                        efectos_ya_procesados = False 
                                        ataque_realizado = False
                                        boss_perdio_turno = False
                                    else:
                                        # Si presionó espacio pero aún no ataca (ej. mensaje inicial)
                                        atacante = equipo[indice_turno]
                                        mensaje_log = f"Turno: {atacante.nombre}\nElige tu acción:\n{obtener_texto_habilidades(atacante)}"

                                else: 
                                    # Era turno del Boss y ya terminó -> Le toca al Jugador.
                                    if ataque_realizado or boss_perdio_turno:
                                        # Cambio el índice para seleccionar al otro soldado del equipo.
                                        indice_turno = (indice_turno + 1) % 2
                                        atacante_actual = equipo[indice_turno]
                                        
                                        # Verificación vital: Si el soldado que le toca está muerto,
                                        # salto automáticamente al otro compañero.
                                        if not atacante_actual.esta_vivo():
                                            indice_turno = (indice_turno + 1) % 2
                                            atacante_actual = equipo[indice_turno]

                                        turno_jugador = True
                                        atacante_actual.recuperar_energia_turno()
                                        
                                        # Reseteo banderas para el jugador
                                        efectos_ya_procesados = False 
                                        ataque_realizado = False
                                        jugador_perdio_turno = False
                                        
                                        mensaje_log = f"Turno: {atacante_actual.nombre}\nElige tu acción:\n{obtener_texto_habilidades(atacante_actual)}"
                        
                        # SELECCIÓN DE HABILIDADES
                        # Solo permito input si es mi turno, no estoy aturdido y no he atacado ya.
                        elif turno_jugador and not jugador_perdio_turno and not ataque_realizado:
                            atacante = equipo[indice_turno]
                            habilidad = None
                            
                            # Prevención de errores: si por algún bug el atacante está muerto.
                            if not atacante.esta_vivo():
                                mensaje_log = f"{atacante.nombre} ha caído..."
                                esperando_continuar = True
                            else:
                                # Mapeo de teclas a índices de la lista de habilidades
                                if evento.key == pygame.K_q: habilidad = atk_basico
                                elif evento.key == pygame.K_1: habilidad = atacante.habilidades[0]
                                elif evento.key == pygame.K_2: habilidad = atacante.habilidades[1]
                                elif evento.key == pygame.K_3: habilidad = atacante.habilidades[2]
                                elif evento.key == pygame.K_4 and len(atacante.habilidades) > 3:
                                    habilidad = atacante.habilidades[3]
                                elif evento.key == pygame.K_5 and len(atacante.habilidades) > 4:
                                    habilidad = atacante.habilidades[4]
                                
                                if habilidad:
                                    # Verifico energía antes de lanzar la lógica de combate
                                    if atacante.gastar_energia(habilidad.costo):
                                        # Aquí llamo al ControladorCombate para que haga los cálculos
                                        mensaje_log = combate.ejecutar_habilidad(atacante, jefe, habilidad, p1, p2, jefe)
                                        ataque_realizado = True 
                                        esperando_continuar = True
                                    else:
                                        # Feedback visual si no hay maná
                                        mensaje_err = f"¡Sin energía! Requiere {habilidad.costo} EP"
                                        motor.dibujar_interfaz(p1, p2, jefe, mensaje_err)
                                        pygame.display.flip(); pygame.time.delay(1000)

        # --- B. VERIFICACIÓN DE ESTADO DEL JUEGO ---
        # Compruebo en cada frame si alguien ganó para cambiar de pantalla.
        if estado == "JUEGO":
            if jefe.vida_actual <= 0:
                estado = "VICTORIA"
            
            if not p1.esta_vivo() and not p2.esta_vivo():
                estado = "DERROTA"

        # --- C. PROCESAMIENTO DE EFECTOS PASIVOS ---
        # Esto ocurre justo al iniciar el turno, antes de que nadie mueva un dedo.
        # Gestiona quemaduras, sangrados y checkea si alguien está aturdido.
        if estado == "JUEGO" and not pausado and not esperando_continuar and not efectos_ya_procesados:
            
            personaje_a_evaluar = equipo[indice_turno] if turno_jugador else jefe
            
            # Si el personaje actual murió por un efecto anterior, saltamos.
            if turno_jugador and not personaje_a_evaluar.esta_vivo():
                 efectos_ya_procesados = True
                 ataque_realizado = True # Forzamos el pase de turno
                 esperando_continuar = True
                 mensaje_log = f"{personaje_a_evaluar.nombre} está abatido."
            else:
                # Delegamos la lógica matemática al controlador
                pierde_turno, msg_efectos = combate.procesar_efectos_pasivos(p1, p2, jefe, personaje_a_evaluar)
                efectos_ya_procesados = True
                
                # Actualizamos las banderas de aturdimiento según el resultado
                if turno_jugador: jugador_perdio_turno = pierde_turno
                else: boss_perdio_turno = pierde_turno
                
                # Si hubo algún efecto (daño o curación), lo mostramos y pausamos.
                if msg_efectos:
                    mensaje_log = msg_efectos
                    motor.dibujar_interfaz(p1, p2, jefe, mensaje_log, esperando_espacio=True)
                    pygame.display.flip(); pygame.time.delay(500)
                    esperando_continuar = True 
                    if pierde_turno: mensaje_log += "\n(Aturdido: Pierde turno)"

        # --- D. INTELIGENCIA ARTIFICIAL (BOSS) ---
        if estado == "JUEGO" and not turno_jugador and not pausado and not esperando_continuar and not ataque_realizado:
            
            if boss_perdio_turno:
                pass 
            else:
                pygame.time.delay(500)
                
                # 1. ACTUALIZAR ESTADO DE ÁNIMO (FSM)
                # El grafo decide si está Normal, Furioso o Defensivo según HP y Estrés
                cerebro_comportamiento.actualizar_estado(jefe)
                estado_boss = cerebro_comportamiento.estado_actual
                bonus = cerebro_comportamiento.obtener_bonificadores()
                
                mensaje_log = f"Turno: {jefe.nombre} [{estado_boss}]"
                
                # 2. SELECCIONAR ESTRATEGIA ÓPTIMA (ALGORITMO DE PRIM)
                # El grafo elige el mejor nodo (A, B... F) basándose en costos y elegibilidad
                nodo_ataque = cerebro_estrategia.seleccionar_siguiente_ataque(jefe)
                
                # 3. EJECUTAR LA ACCIÓN DEL NODO
                # Traducimos los datos abstractos del nodo a acciones del juego
                dmg_base = jefe.ataque_base * bonus["ataque"]
                
                # Definir objetivo (Random por ahora)
                candidatos = [p for p in equipo if p.esta_vivo()]
                objetivo = random.choice(candidatos) if candidatos else p1
                
                # Lógica según el tipo de efecto del nodo (Tabla 4 PDF)
                efecto = nodo_ataque.efecto_tipo
                valor = nodo_ataque.valor_efecto # Porcentaje (ej. 0.05)
                
                msg_accion = ""
                dano_final = 0
                
                if "dano" in efecto:
                    # Daño porcentual basado en la vida MAX del objetivo (o ataque del boss)
                    # Aquí usaremos el ataque del boss escalado por el porcentaje del nodo
                    factor_dano = 1.0 + valor # Ej: 0.20 -> 120% daño
                    dano_final = int(dmg_base * factor_dano)
                    
                    res = objetivo.recibir_dano(dano_final)
                    msg_accion = f"¡{nodo_ataque.nombre}!\nDaño: {dano_final}"
                    
                    # Animación
                    motor.animar_proyectil(p1, p2, jefe, msg_accion, (950, 200), (300, 380), 'proy_molotov')
                    motor.animar_impacto(p1, p2, jefe, msg_accion, objetivo, "FUEGO")

                if "cura" in efecto:
                    cura = int(jefe.vida_max * valor)
                    jefe.curar(cura)
                    msg_accion += f"\nSe cura {cura} HP."
                    motor.animar_impacto(p1, p2, jefe, msg_accion, jefe, "CURACION")

                # Actualizar log y pasar turno
                mensaje_log = f"{mensaje_log}\n{msg_accion}"
                ataque_realizado = True 
                esperando_continuar = True
        # --- E. RENDERIZADO (DIBUJADO) ---
        # Dependiendo del estado global, le pido al motor que dibuje una cosa u otra.
        if estado == "MENU": 
            motor.dibujar_menu()
        elif estado == "VICTORIA":
            motor.dibujar_interfaz(p1, p2, jefe, "¡VICTORIA!") # Fondo base
            motor.dibujar_victoria() # Capa superior
        elif estado == "DERROTA":
            motor.dibujar_interfaz(p1, p2, jefe, "¡DERROTA!") 
            motor.dibujar_derrota()  
        elif estado == "JUEGO":
            motor.dibujar_interfaz(p1, p2, jefe, mensaje_log, esperando_espacio=esperando_continuar)
            motor.dibujar_barras_vida(p1, p2, jefe)
            
            # Si estamos en pausa, dibujamos el menú flotante encima de todo.
            if pausado: 
                motor.dibujar_menu_pausa(indice_pausa, mostrar_guardado_timer > 0)

        # Actualizamos la pantalla real y mantenemos los FPS estables.
        pygame.display.flip()
        reloj.tick(config.FPS)

if __name__ == "__main__":
    main()
