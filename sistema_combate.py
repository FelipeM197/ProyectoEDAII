import pygame
from estructuras import ArbolAtaque
import config 

"""
SISTEMA DE COMBATE (CORREGIDO)
------------------------------
- Se arregló el bug visual donde salía el sprite de Trump cuando se quemaba el jugador.
- Se eliminó código duplicado en ejecutar_habilidad.
"""

class ControladorCombate:
    def __init__(self, grafo_estados, motor_grafico):
        self.grafo = grafo_estados
        self.motor = motor_grafico 

    # [CORRECCIÓN 1] Añadimos 'jefe' como argumento obligatorio
    def procesar_efectos_pasivos(self, p1, p2, jefe, personaje_activo):
        """
        Aplica daño por quemadura/sangrado al inicio del turno.
        """
        estado = personaje_activo.estado_actual
        mensaje = ""
        efecto_aplicado = False
        pierde_turno = False

        if estado == "Quemado":
            dano = 15
            personaje_activo.recibir_dano(dano)
            mensaje = f"¡{personaje_activo.nombre} se quema!\nPierde {dano} HP."
            
            # [CORRECCIÓN 2] Pasamos 'jefe' como 3er argumento (el Boss de la escena)
            # y 'personaje_activo' como 5to argumento (el que recibe el fuego)
            self.motor.animar_impacto(p1, p2, jefe, mensaje, personaje_activo, "FUEGO")
            efecto_aplicado = True
            
            if personaje_activo.turnos_quemado > 0:
                personaje_activo.turnos_quemado -= 1
            
            if personaje_activo.turnos_quemado <= 0:
                personaje_activo.estado_actual = "Normal"
                mensaje += "\nEl fuego se ha extinguido."

        elif estado == "Sangrado":
            dano = 10
            personaje_activo.recibir_dano(dano)
            mensaje = f"¡{personaje_activo.nombre} sangra!\nPierde {dano} HP."
            
            # [CORRECCIÓN 2] Aquí también pasamos 'jefe' correctamente
            self.motor.animar_impacto(p1, p2, jefe, mensaje, personaje_activo, "SANGRE")
            efecto_aplicado = True

        elif estado == "Aturdido":
            mensaje = f"¡{personaje_activo.nombre} está ATURDIDO!\nPierde su turno."
            personaje_activo.estado_actual = "Normal"
            pierde_turno = True
            
            # Visualización rápida
            self.motor.dibujar_interfaz(p1, p2, jefe, mensaje) # Aquí pasamos jefe correctamente
            pygame.display.flip()
            pygame.time.delay(2000)

        if efecto_aplicado:
            pygame.time.delay(1000)
            
        return pierde_turno, mensaje

    def ejecutar_habilidad(self, atacante, defensor, habilidad, p1, p2, jefe):
        mensaje_log = f"{atacante.nombre} usa {habilidad.nombre}!"
        
        # 1. POSICIONES
        origen = (100, 230) if atacante == p1 else (350, 230)
        destino = (850, 230) 
        
        # 2. PROYECTILES
        img_proyectil = None
        if "Molotov" in habilidad.nombre: img_proyectil = 'proy_molotov'
        elif "Disparo" in habilidad.nombre: img_proyectil = 'proy_disparo'
        elif "Cuchillada" in habilidad.nombre: img_proyectil = 'proy_cuchillo'
        elif "Intimidación" in habilidad.nombre: img_proyectil = 'proy_calavera'
        elif "Discurso" in habilidad.nombre: img_proyectil = 'proy_grito'

        if img_proyectil:
             self.motor.animar_proyectil(p1, p2, jefe, mensaje_log, origen, destino, img_proyectil)

        # 3. EFECTOS
        if habilidad.tipo == "CURACION":
            objetivo = p1 if p1.vida_actual < p2.vida_actual else p2
            cantidad = abs(habilidad.dano)
            objetivo.curar(cantidad)
            mensaje_log += f"\nRecupera {cantidad} HP a {objetivo.nombre}"
            self.motor.animar_impacto(p1, p2, jefe, mensaje_log, objetivo, "CURACION")
        
        elif habilidad.tipo == "LIMPIEZA":
            nuevo_estado = self.grafo.transicion(atacante.estado_actual, habilidad.codigo_efecto)
            if nuevo_estado != atacante.estado_actual:
                atacante.estado_actual = nuevo_estado
                mensaje_log += "\n¡Efectos eliminados! Estado: Normal."
                self.motor.animar_impacto(p1, p2, jefe, mensaje_log, atacante, "CURACION")
            else:
                mensaje_log += "\nEl botiquín no era necesario."
                self.motor.animar_impacto(p1, p2, jefe, mensaje_log, atacante, "NORMAL")

        elif habilidad.tipo == "BUFF":
            mensaje_log += f"\n¡{atacante.nombre} se siente motivado!"
            self.motor.animar_impacto(p1, p2, jefe, mensaje_log, atacante, "MOTIVACION")
            
        elif habilidad.tipo == "DEFENSA":
            atacante.agregar_capa_escudo(1)
            mensaje_log += f"\n¡{atacante.nombre} levanta un Muro!"
            self.motor.animar_impacto(p1, p2, jefe, mensaje_log, atacante, "ESCUDO")

        else: # ATAQUE OFENSIVO
            resultado = ArbolAtaque.ejecutar_ataque(habilidad.dano)
            
            if resultado.tipo == "TROPIEZO":
                atacante.recibir_dano(resultado.dano)
                mensaje_log += f"\n¡Tropiezo! Se hiere a sí mismo ({resultado.dano})"
                self.motor.animar_impacto(p1, p2, jefe, mensaje_log, atacante, "SANGRE")
            
            elif resultado.tipo == "FALLO":
                mensaje_log += f"\n{resultado.mensaje}"
                self.motor.animar_impacto(p1, p2, jefe, mensaje_log, defensor, "NORMAL")

            else: # ÉXITO O CRÍTICO
                msg_escudo = defensor.recibir_dano(resultado.dano)
                mensaje_log += f"\n{resultado.mensaje} Daño: {resultado.dano}"
                if isinstance(msg_escudo, str): mensaje_log += f"\n{msg_escudo}"

                # SOLO SI ACIERTA, TRANSICIÓN DEL GRAFO
                evento = habilidad.codigo_efecto 
                nuevo_estado = self.grafo.transicion(defensor.estado_actual, evento)
                
                # [CORRECCIÓN 3] Bloque único y limpio de actualización de estado
                if nuevo_estado != defensor.estado_actual:
                    defensor.estado_actual = nuevo_estado
                    mensaje_log += f"\n[EFECTO] ¡{defensor.nombre} pasa a {nuevo_estado}!"
                    
                    if nuevo_estado == "Quemado":
                        defensor.turnos_quemado = config.DURACION_QUEMADO

                anim = "NORMAL"
                if nuevo_estado == "Quemado": anim = "FUEGO"
                elif nuevo_estado == "Sangrado": anim = "SANGRE"
                elif nuevo_estado == "Aturdido": anim = "CRITICO"
                
                self.motor.animar_impacto(p1, p2, jefe, mensaje_log, defensor, anim)
        
        return mensaje_log