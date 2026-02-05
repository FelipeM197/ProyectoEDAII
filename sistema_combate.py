import pygame
from estructuras import ArbolAtaque
import config 

"""
SISTEMA DE COMBATE (CONTROLADOR LÓGICO)

GUÍA RÁPIDA DE MODIFICACIÓN (MECÁNICAS Y TURNOS):
-----------------------------------------------------------------------------------------
CLASE / LÓGICA          | MÉTODO / VARIABLE     | ACCIÓN / CÓMO MODIFICAR
-----------------------------------------------------------------------------------------
1. DAÑO POR TIEMPO      | procesar_efectos...() | Controla quemaduras y sangrados.
   (Inicio de Turno)    | - if estado=="Quemado"| - Cambiar 'dano = 15' para ajustar
                        |                       |   lo que quita el fuego por turno.
                        | - turnos_quemado -= 1 | - Lógica de duración del efecto.
-----------------------------------------------------------------------------------------
2. ANIMACIONES ATAQUE   | ejecutar_habilidad()  | Vincula el nombre con el dibujo.
   (Proyectiles)        | - if "Molotov" in...  | - SI CAMBIAS NOMBRES EN CONFIG.PY,
                        |                       |   debes actualizar estos 'if' para
                        |                       |   que salga el proyectil correcto.
-----------------------------------------------------------------------------------------
3. LÓGICA DE APOYO      | ejecutar_habilidad()  | Bloques IF por 'tipo':
   (Curas y Escudos)    | - TIPO "CURACION"     | - Define a quién cura (IA simple).
                        | - TIPO "DEFENSA"      | - 'agregar_capa_escudo(1)':
                        |                       |   Cambiar '1' por más capas.
-----------------------------------------------------------------------------------------
4. SISTEMA DE ESTRÉS    | ejecutar_habilidad()  | **IMPORTANTE PARA EL BOSS**
   (Mecánica Única)     | - aumento_st = 15     | - Estrés base por golpe.
                        | - if "Quemado"...     | - Sinergias: Aquí defines que el
                        |                       |   dolor físico aumenta el estrés (+10).
                        | - if "Vulnerable"...  | - Multiplicadores (x2) de daño mental.
-----------------------------------------------------------------------------------------
5. APLICAR EFECTOS      | ejecutar_habilidad()  | Conexión con el Grafo.
   (Final del ataque)   | - grafo.transicion()  | Pregunta al grafo si el estado cambia.
                        | - turnos_quemado = X  | Si el estado cambia a fuego, aquí
                        |                       | se reinicia el contador de turnos.
-----------------------------------------------------------------------------------------
"""

class ControladorCombate:
    """
    Clase mediadora. Recibe las intenciones del jugador (teclas), calcula los resultados
    matemáticos y luego ordena al motor gráfico que muestre lo que pasó.
    """
    def __init__(self, grafo_estados, motor_grafico):
        self.grafo = grafo_estados
        self.motor = motor_grafico 

    def procesar_efectos_pasivos(self, p1, p2, jefe, personaje_activo):
        """
        Esta función se ejecuta al inicio de CADA turno, antes de que el jugador
        pueda hacer nada. Revisa si el personaje está sufriendo efectos persistentes.
        
        Args:
            p1, p2, jefe: Necesarios para que el motor gráfico pueda redibujar 
                          la escena completa mientras muestra la animación del efecto.
            personaje_activo: Quien tiene el turno actualmente.
        """
        estado = personaje_activo.estado_actual
        mensaje = ""
        efecto_aplicado = False
        pierde_turno = False

        # --- CASO 1: QUEMADURA ---
        if estado == "Quemado":
            dano = 15
            personaje_activo.recibir_dano(dano)
            mensaje = f"¡{personaje_activo.nombre} se quema!\nPierde {dano} HP."
            
            # Ordenamos la animación visual de fuego sobre el personaje.
            self.motor.animar_impacto(p1, p2, jefe, mensaje, personaje_activo, "FUEGO")
            efecto_aplicado = True
            
            # Lógica de contadores: El fuego se apaga solo después de X turnos.
            if personaje_activo.turnos_quemado > 0:
                personaje_activo.turnos_quemado -= 1
            
            if personaje_activo.turnos_quemado <= 0:
                personaje_activo.estado_actual = "Normal"
                mensaje += "\nEl fuego se ha extinguido."

        # --- CASO 2: SANGRADO ---
        elif estado == "Sangrado":
            dano = 10
            personaje_activo.recibir_dano(dano)
            mensaje = f"¡{personaje_activo.nombre} sangra!\nPierde {dano} HP."
            
            self.motor.animar_impacto(p1, p2, jefe, mensaje, personaje_activo, "SANGRE")
            efecto_aplicado = True

        # --- CASO 3: ATURDIMIENTO ---
        elif estado == "Aturdido":
            mensaje = f"¡{personaje_activo.nombre} está ATURDIDO!\nPierde su turno."
            # El aturdimiento suele durar solo 1 turno, así que lo reseteamos aquí.
            personaje_activo.estado_actual = "Normal"
            pierde_turno = True
            
            # Mostramos el mensaje pero sin animación de daño específica.
            self.motor.dibujar_interfaz(p1, p2, jefe, mensaje) 
            pygame.display.flip()
            pygame.time.delay(2000)
        if personaje_activo.turnos_motivado > 0:
            personaje_activo.turnos_motivado -= 1
            if personaje_activo.turnos_motivado == 0:
                mensaje += f"\n{personaje_activo.nombre} ya no está motivado."
        # Pequeña pausa dramática si pasó algo, para que el jugador entienda qué ocurrió.
        if efecto_aplicado:
            pygame.time.delay(1000)
        
        return pierde_turno, mensaje

    def ejecutar_habilidad(self, atacante, defensor, habilidad, p1, p2, jefe):
        """
        El núcleo de la acción. Esta función toma una habilidad seleccionada y
        resuelve todo lo que conlleva: animaciones, cálculos de daño y cambios de estado.
        """
        mensaje_log = f"{atacante.nombre} usa {habilidad.nombre}!"
        
        # 1. COORDENADAS VISUALES
        # Definimos desde dónde sale el disparo y hacia dónde va.
        origen = (100, 230) if atacante == p1 else (350, 230)
        destino = (850, 230) 
        
        # 2. SELECCIÓN DE ASSETS VISUALES
        # Mapeamos el nombre de la habilidad con su imagen de proyectil correspondiente.
        img_proyectil = None
        if "Molotov" in habilidad.nombre: img_proyectil = 'proy_molotov'
        elif "Disparo" in habilidad.nombre: img_proyectil = 'proy_disparo'
        elif "Cuchillada" in habilidad.nombre: img_proyectil = 'proy_cuchillo'
        elif "Intimidación" in habilidad.nombre: img_proyectil = 'proy_calavera'
        elif "Discurso" in habilidad.nombre: img_proyectil = 'proy_grito'

        # Si hay proyectil, detenemos el juego un momento para animar su viaje.
        if img_proyectil:
             self.motor.animar_proyectil(p1, p2, jefe, mensaje_log, origen, destino, img_proyectil)

        # 3. RESOLUCIÓN LÓGICA POR TIPO
        # Dependiendo del 'tipo' definido en config.py, hacemos cosas distintas.

        if habilidad.tipo == "CURACION":
            # IA simple de curación: cura al que tenga menos vida.
            objetivo = p1 if p1.vida_actual < p2.vida_actual else p2
            cantidad = abs(habilidad.dano) # Usamos abs() por si definí el daño como negativo en config.
            objetivo.curar(cantidad)
            
            mensaje_log += f"\nRecupera {cantidad} HP a {objetivo.nombre}"
            self.motor.animar_impacto(p1, p2, jefe, mensaje_log, objetivo, "CURACION")
        
        elif habilidad.tipo == "LIMPIEZA":
            # Consultamos al Grafo: ¿Qué pasa si aplico 'limpieza' al estado actual?
            nuevo_estado = self.grafo.transicion(atacante.estado_actual, habilidad.codigo_efecto)
            
            if nuevo_estado != atacante.estado_actual:
                atacante.estado_actual = nuevo_estado
                mensaje_log += "\n¡Efectos eliminados! Estado: Normal."
                self.motor.animar_impacto(p1, p2, jefe, mensaje_log, atacante, "CURACION")
            else:
                mensaje_log += "\nEl botiquín no era necesario."
                self.motor.animar_impacto(p1, p2, jefe, mensaje_log, atacante, "NORMAL")

        elif habilidad.tipo == "BUFF":
            atacante.turnos_motivado = config.DURACION_MOTIVACION 
            
            mensaje_log += f"\n¡{atacante.nombre} se motiva! (Costos reducidos)"
            self.motor.animar_impacto(p1, p2, jefe, mensaje_log, atacante, "MOTIVACION")
            
        elif habilidad.tipo == "DEFENSA":
            # Añadimos una capa a la pila de escudos del personaje.
            atacante.agregar_capa_escudo(1)
            mensaje_log += f"\n¡{atacante.nombre} levanta un Muro!"
            self.motor.animar_impacto(p1, p2, jefe, mensaje_log, atacante, "ESCUDO")

        else: 
            # --- LÓGICA DE COMBATE OFENSIVO ---
            # Aquí es donde usamos el Árbol de Decisión Probabilístico.
            
            # Pedimos al árbol que tire los dados y nos dé un resultado.
            resultado = ArbolAtaque.ejecutar_ataque(habilidad.dano)
            
            if resultado.tipo == "TROPIEZO":
                # Fallo crítico: el atacante se hiere a sí mismo.
                atacante.recibir_dano(resultado.dano)
                mensaje_log += f"\n¡Tropiezo! Se hiere a sí mismo ({resultado.dano})"
                self.motor.animar_impacto(p1, p2, jefe, mensaje_log, atacante, "SANGRE")
            
            elif resultado.tipo == "FALLO":
                mensaje_log += f"\n{resultado.mensaje}"
                self.motor.animar_impacto(p1, p2, jefe, mensaje_log, defensor, "FALLO")

            else: # ÉXITO O CRÍTICO
                # Aplicamos el daño al defensor.
                msg_escudo = defensor.recibir_dano(resultado.dano)
                mensaje_log += f"\n{resultado.mensaje} Daño: {resultado.dano}"
                if isinstance(msg_escudo, str): mensaje_log += f"\n{msg_escudo}"
                # --- LÓGICA DE ESTRÉS ---
                # Solo aplica si es el Jefe (tiene atributo 'estres')
                if hasattr(defensor, 'st'):
                    aumento_st = 15 # Estrés base por impacto
                
                    # 1. Modificador por Intensidad del Golpe
                    if resultado.tipo == "CRITICO":
                        aumento_st = 25 
                    # 2. Modificador por Estado Actual (Sinergia de Dolor)
                    # Si el jefe ya está sufriendo, se estresa más.
                    estado_actual = defensor.estado_actual
                
                    if estado_actual in ["Quemado", "Sangrado"]:
                        aumento_st += 10 # El dolor físico constante aumenta la ansiedad
                    
                    elif estado_actual == "Vulnerable":
                        aumento_st *= 2 # Si está vulnerable, el impacto emocional es doble
                    
                    elif estado_actual == "Enfurecido":
                        aumento_st = 5 # En estado de furia, es más resistente al estrés externo (adrenalina)

                    defensor.aumentar_estres(aumento_st)

                # --- INTERACCIÓN CON EL GRAFO DE ESTADOS ---
                # Si el ataque acertó, verificamos si aplica algún efecto especial (Fuego, etc.)
                evento = habilidad.codigo_efecto 
                nuevo_estado = self.grafo.transicion(defensor.estado_actual, evento)
                
                # Si el grafo dice que cambiamos de estado, actualizamos al personaje.
                if nuevo_estado != defensor.estado_actual:
                    defensor.estado_actual = nuevo_estado
                    mensaje_log += f"\n[EFECTO] ¡{defensor.nombre} pasa a {nuevo_estado}!"
                    
                    # Si el nuevo estado es quemadura, iniciamos el contador de turnos.
                    if nuevo_estado == "Quemado":
                        defensor.turnos_quemado = config.DURACION_QUEMADO

                # Decidimos qué overlay visual mostrar basado en el estado final.
                anim = "NORMAL"
                if nuevo_estado == "Quemado": anim = "FUEGO"
                elif nuevo_estado == "Sangrado": anim = "SANGRE"
                elif nuevo_estado == "Aturdido": anim = "CRITICO"
                
                self.motor.animar_impacto(p1, p2, jefe, mensaje_log, defensor, anim)
        
        return mensaje_log
