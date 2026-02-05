import pygame
import sys
import random
import config
from graficos import GestorGrafico
from entidades import Personaje, Habilidad, Boss
from estructuras import GrafoEfectos, GrafoEstrategia, GrafoEstados
from sistema_combate import ControladorCombate
from recursos import AlmacenRecursos 
from sistema_guardado import SistemaGuardado

"""
PUNTO DE ENTRADA PRINCIPAL (ORQUESTADOR DEL BUCLE)

GUÍA RÁPIDA DE MODIFICACIÓN (FLUJO Y CONTROLES):
-----------------------------------------------------------------------------------------
SECCIÓN / LÓGICA        | MÉTODO / VARIABLE     | ACCIÓN / CÓMO MODIFICAR
-----------------------------------------------------------------------------------------
1. CONFIGURACIÓN INICIAL| main() -> pygame.init | Arranque del motor.
   (Música y Objetos)   | - mixer.music.load    | - Cambiar música o volumen (0.3).
                        | - p1, p2, jefe        | - Instanciación de objetos iniciales.
-----------------------------------------------------------------------------------------
2. INTERFAZ DE TEXTO    | obtener_texto_habil.. | Formatea el menú de ataques.
   (UI Dinámica)        | - txt += f"[{idx}]"   | - Cambiar cómo se ven las opciones
                        |                       |   (Ej: "[1] Disparo" vs "1. Disparo").
                        | - costo // 2          | - Visualización del descuento 'Motivado'.
-----------------------------------------------------------------------------------------
3. SISTEMA DE GUARDADO  | if datos_cargados:    | Lógica al detectar 'savegame.json'.
   (Carga al inicio)    | - turno_jugador       | - Restaura quién tenía el turno.
                        | - esperando_continuar | - Fuerza una pausa al cargar.
-----------------------------------------------------------------------------------------
4. CONTROLES (INPUT)    | Bucle for evento...   | Mapeo de Teclado.
   (Jugador)            | - K_SPACE             | - Avanzar texto / Confirmar turno.
                        | - K_p / K_UP / K_DOWN | - Control del Menú de Pausa.
                        | - K_1, K_2... K_q     | - Vincular teclas a habilidades.
                        |                       |   (Aquí añades cheats si quieres).
-----------------------------------------------------------------------------------------
5. TURNO DEL JUGADOR    | if turno_jugador...   | Lógica de disparo.
   (Acción)             | - gastar_energia()    | - Verifica si tienes maná.
                        | - ejecutar_habilidad()| - Llama al árbitro (sistema_combate).
-----------------------------------------------------------------------------------------
6. TURNO DEL JEFE (IA)  | if not turno_jugador  | Lógica del enemigo.
   (Cerebro)            | - actualizar_estado() | - Define si está Furioso/Defensivo.
                        | - seleccionar_...()   | - Ejecuta Algoritmo de Prim (Estrategia).
                        | - animar_proyectil()  | - **IMPORTANTE**: Aquí se eligen los
                        |                       |   gráficos de los ataques del jefe.
-----------------------------------------------------------------------------------------
7. FINAL DEL TURNO      | if estado == "JUEGO"  | Gestión de Estados Pasivos.
   (Sangrado/Fuego)     | - procesar_efectos... | - Aplica daño por quemadura al inicio
                        |                       |   del turno (antes de atacar).
-----------------------------------------------------------------------------------------
8. RENDERIZADO          | Bloque final if/elif  | Dibuja la escena según estado.
   (Draw Loop)          | - dibujar_interfaz    | - Mantiene actualizada la pantalla.
                        | - dibujar_menu_pausa  | - Dibuja la capa superior (Overlay).
-----------------------------------------------------------------------------------------
"""

def obtener_texto_habilidades(personaje):
    # Empiezo el texto mostrando la habilidad de emergencia que siempre es gratis y accesible.
    txt = "[Q] Golpe Táctico (0 EP)\n"
    
    # Uso enumerate para recorrer la lista porque necesito tener al mismo tiempo 
    # el índice (para saber qué tecla asignar: 1, 2, 3...) y el objeto de la 
    # habilidad para sacar sus datos.
    for i, h in enumerate(personaje.habilidades):
        idx = i + 1
        
        # Si el personaje está motivado, calculo la mitad del costo al vuelo 
        # para que el jugador vea el descuento real.
        costo_visual = h.costo
        if personaje.turnos_motivado > 0:
            costo_visual = h.costo // 2
        
        # Armo la cadena de texto usando el costo visual calculado arriba en 
        # lugar del valor estático.
        txt += f"[{idx}] {h.nombre} ({costo_visual})   "
        
        # Acomodo el texto haciendo un salto de línea cada dos habilidades 
        # para que no se salga de la caja de interfaz.
        if idx % 2 == 0:
            txt += "\n"
            
    # Si el buff sigue activo, agrego un pequeño indicador al 
    # final para saber cuántos turnos de ventaja quedan.
    if personaje.turnos_motivado > 0:
        txt += f"\n[MOTIVADO: {personaje.turnos_motivado} turnos]"
        
    return txt

def main():
    # Iniciamos el motor de Pygame y la ventana.
    pygame.init()

    # Asegurarnos de que el mixer esté iniciado (por si acaso recursos.py no lo hizo)
    if not pygame.mixer.get_init():
        pygame.mixer.init()

    pantalla = pygame.display.set_mode((config.ANCHO, config.ALTO))
    pygame.display.set_caption(config.TITULO)
    reloj = pygame.time.Clock()

    # --- MÚSICA DE FONDO ---
    try:
        # Cargar el archivo de música
        pygame.mixer.music.load(config.RUTA_MUSICA)
        pygame.mixer.music.set_volume(0.3) # Volumen al 30% para no aturdir
        # Reproducir en loop (-1 significa infinito)
        pygame.mixer.music.play(-1)
    except Exception as e:
        print(f"No se pudo cargar la música: {e}")
    
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
    sistema = SistemaGuardado()

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

    # Lista para alternar turnos entre los dos soldados.
    equipo = [p1, p2]
    indice_turno = 0
    turno_jugador = True # Por defecto empieza el jugador

    # Variables de Control de Flujo (Valores por defecto)
    estado = "MENU"      # Puede ser: MENU, JUEGO, VICTORIA, DERROTA
    pausado = False
    
    # Bandera crítica: detiene el juego para que el usuario pueda leer el texto.
    esperando_continuar = False 
    
    # Banderas para controlar qué ya pasó en el turno actual.
    efectos_ya_procesados = False # Ya aplicamos el daño por fuego este turno?
    jugador_perdio_turno = False  # Está aturdido?
    boss_perdio_turno = False     
    ataque_realizado = False      # Ya eligió una acción?
    
    # Variables para la interfaz del menú de pausa.
    indice_pausa = 0
    mostrar_guardado_timer = 0

    # Intentar cargar partida al iniciar
    datos_cargados = sistema.cargar_partida()
    
    if datos_cargados:
        print("Datos encontrados. Cargando partida...")
        # Restaurar variables globales
        turno_jugador = datos_cargados["global"]["es_turno_jugador"]
        indice_turno = datos_cargados["global"]["indice_actual"]
        
        # Restaurar personajes
        sistema.aplicar_datos(p1, datos_cargados["jugador1"])
        sistema.aplicar_datos(p2, datos_cargados["jugador2"])
        sistema.aplicar_datos(jefe, datos_cargados["jefe"])
        
        # Actualizar referencia del atacante actual
        atacante_actual = equipo[indice_turno]
        
        # Configuración para entrar directo a la acción
        estado = "JUEGO"
        # Marcamos efectos como procesados para que no salten quemaduras al cargar
        efectos_ya_procesados = True 
        
        # Mensaje de bienvenida y PAUSA
        mensaje_log = f"Partida recuperada.\nTurno de: {atacante_actual.nombre}\n>> PRENSA ESPACIO <<"
        
        # Forzamos la espera. Al dar espacio, el bucle principal
        # se encargará de refrescar el menú de habilidades automáticamente.
        esperando_continuar = True 

    else:
        # Si no hay datos, iniciamos normal
        atacante_actual = equipo[indice_turno]
        mensaje_log = f"¡Misión Iniciada!\nTurno: {atacante_actual.nombre}\n{obtener_texto_habilidades(atacante_actual)}"
    
    while True:
        # --- A. CONTROL DE EVENTOS (TECLADO/RATÓN) ---
        # Aquí capturo todo lo que hace el usuario.
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            
            if evento.type == pygame.KEYDOWN:
                #  Lógica del Menú Principal
                if estado == "MENU":
                    if evento.key == pygame.K_RETURN:
                        
                        # --- REPRODUCIR SONIDO START ---
                        sfx = motor.sonidos.get('sfx_start') # Obtenemos el sonido
                        if sfx: sfx.play() # Lo reproducimos

                        estado = "JUEGO"
                
                # Pantallas de fin de juego
                elif estado in ["VICTORIA", "DERROTA"]:
                    if evento.key == pygame.K_RETURN:
                        pygame.quit(); sys.exit() # Aquí podría poner un reset()

                # Lógica durante el combate
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
                            elif sel == "GUARDAR":
                                # Llamamos al sistema para guardar los datos reales
                                exito = sistema.guardar_partida(p1, p2, jefe, turno_jugador, indice_turno)
                                
                                # Si funcionó, mostramos el mensaje visual
                                if exito:
                                    mostrar_guardado_timer = 90
                    
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
                                if evento.key == pygame.K_q: 
                                    habilidad = atk_basico
                                    habilidad.dano = atacante.ataque_base 
                                    
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
                sistema.borrar_partida() 
            
            if not p1.esta_vivo() and not p2.esta_vivo():
                estado = "DERROTA"
                sistema.borrar_partida()

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
                
                # ACTUALIZAR ESTADO DE ÁNIMO 
                # Primero reviso las variables vitales del jefe para ver si entra en Furia o se pone a la defensiva.
                cerebro_comportamiento.actualizar_estado(jefe)
                estado_boss = cerebro_comportamiento.estado_actual
                bonus = cerebro_comportamiento.obtener_bonificadores()
                
                # Aquí verifico si el jefe viene "cebado" de un turno anterior.
                # Si activó un boost de ataque recientemente, aplico el multiplicador extra y descuento un turno del contador.
                mult_extra_ataque = 1.0
                if jefe.turnos_buff_ataque > 0:
                    mult_extra_ataque = 1.3 
                    jefe.turnos_buff_ataque -= 1 

                # Armo el mensaje de cabecera, avisando si hay buffs activos para que el jugador sepa por qué le pegan tan duro.
                mensaje_log = f"Turno: {jefe.nombre} [{estado_boss}]"
                if jefe.turnos_buff_ataque > 0: mensaje_log += " (ATK UP)"
                if jefe.turnos_buff_defensa > 0: mensaje_log += " (DEF UP)"
                
                #  SELECCIONAR ESTRATEGIA ÓPTIMA (ALGORITMO DE PRIM)
                # Le pregunto al grafo cuál es el siguiente movimiento más eficiente según los costos.
                nodo_ataque = cerebro_estrategia.seleccionar_siguiente_ataque(jefe)
                
                # EJECUTAR LA ACCIÓN DEL NODO
                # Calculo el daño base combinando su estadística natural, el estado de ánimo (Furia/Normal) y el buff temporal si lo tuviera.
                dmg_base = jefe.ataque_base * bonus["ataque"] * mult_extra_ataque
                
                # Elijo una víctima al azar entre los que sigan vivos.
                candidatos = [p for p in equipo if p.esta_vivo()]
                objetivo = random.choice(candidatos) if candidatos else p1
                
                # Extraigo los datos del nodo elegido para saber qué hacer.
                efecto = nodo_ataque.efecto_tipo
                valor = nodo_ataque.valor_efecto 
                
                msg_accion = ""
                dano_final = 0
                
                if "dano" in efecto:
                    # Calculo el daño final sumando el porcentaje de potencia de la habilidad (ej. Molotov pega más que Bala).
                    factor_dano = 1.0 + valor 
                    dano_final = int(dmg_base * factor_dano)
                    
                    # Aplico el daño y capturo el mensaje por si el jugador tenía un escudo activo.
                    msg_escudo = objetivo.recibir_dano(dano_final)
                    msg_accion = f"¡{nodo_ataque.nombre}!\nDaño: {dano_final}"
                    if isinstance(msg_escudo, str) and "bloqueó" in msg_escudo:
                         msg_accion += "\n(Bloqueado)"

                    # Aquí está la clave: reviso si este ataque trae un efecto secundario (como fuego o cuchillo)
                    # para aplicárselo al jugador y actualizar su estado.
                    codigo_evento = nodo_ataque.efecto_estado
                    
                    if codigo_evento:
                        # El grafo de efectos me dice en qué se convierte el jugador (ej. Normal + Fuego -> Quemado).
                        nuevo_estado = grafo_estados.transicion(objetivo.estado_actual, codigo_evento)
                        
                        if nuevo_estado != objetivo.estado_actual:
                            objetivo.estado_actual = nuevo_estado
                            msg_accion += f"\n¡{objetivo.nombre} está {nuevo_estado}!"
                            
                            # Si logré quemarlo, inicio el contador para que sufra daño en los siguientes turnos.
                            if nuevo_estado == "Quemado":
                                objetivo.turnos_quemado = config.DURACION_QUEMADO 
                    
                    # Elijo la animación correcta dependiendo de si lo quemé, lo corté o fue un golpe seco.
                    nombre_ataque = nodo_ataque.nombre
                    sprite_proyectil = 'proy_molotov' # Imagen por defecto
                    
                    if "Bala" in nombre_ataque:
                        sprite_proyectil = 'proy_disparo'
                    elif "Cuchillo" in nombre_ataque:
                        sprite_proyectil = 'proy_cuchillo'
                    
                    #  SELECCIÓN DE EFECTO DE IMPACTO (Fuego, Sangre o Normal)
                    tipo_anim = "FUEGO" if nodo_ataque.efecto_estado == "fuego" else "SANGRE" if nodo_ataque.efecto_estado == "cuchillo" else "NORMAL"
                    
                    # EJECUCIÓN CON LA VARIABLE DINÁMICA
                    # Usamos 'sprite_proyectil' en lugar del texto fijo
                    motor.animar_proyectil(p1, p2, jefe, msg_accion, (950, 200), (300, 380), sprite_proyectil)
                    motor.animar_impacto(p1, p2, jefe, msg_accion, objetivo, tipo_anim)

                if "cura" in efecto:
                    cura = int(jefe.vida_max * valor)
                    jefe.curar(cura)
                    msg_accion += f"\nSe cura {cura} HP."
                    motor.animar_impacto(p1, p2, jefe, msg_accion, jefe, "CURACION")

                # Por último, si la habilidad que usó era de soporte (como Táctica), activo los contadores
                # para que el jefe quede potenciado durante los próximos 3 turnos.
                if nodo_ataque.boost == "ataque":
                    jefe.turnos_buff_ataque = 3 
                    msg_accion += "\n¡Sube su ATAQUE!"
                    
                if nodo_ataque.boost == "defensa":
                    jefe.turnos_buff_defensa = 3 
                    msg_accion += "\n¡Sube su DEFENSA!"
                    motor.animar_impacto(p1, p2, jefe, msg_accion, jefe, "ESCUDO")

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
