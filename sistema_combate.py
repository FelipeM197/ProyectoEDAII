import pygame
from estructuras import ArbolAtaque
import config # Importamos config para saber coordenadas si es necesario

"""
SISTEMA DE COMBATE (CEREBRO LÓGICO)
-----------------------------------
Este módulo encapsula las reglas del juego para mantener el main.py limpio.
Responsabilidades:
1. Procesar los efectos pasivos al inicio del turno (Grafo).
2. Ejecutar las habilidades seleccionadas (Árbol).
"""

class ControladorCombate:
    def __init__(self, grafo_estados, motor_grafico):
        self.grafo = grafo_estados
        self.motor = motor_grafico # Referencia para poder invocar animaciones

    def procesar_efectos_pasivos(self, p1, p2, personaje_activo):
        """
        FASE DE GRAFOS: Revisa el NODO actual del personaje en el grafo
        y aplica las consecuencias (restar vida, perder turno).
        Retorna: (pierde_turno: bool, mensaje: str)
        """
        estado = personaje_activo.estado_actual
        mensaje = ""
        efecto_aplicado = False
        pierde_turno = False

        # --- RECORRIDO DEL ESTADO ACTUAL ---
        if estado == "Quemado":
            dano = 15
            personaje_activo.recibir_dano(dano)
            mensaje = f"¡{personaje_activo.nombre} se quema!\nPierde {dano} HP."
            
            # [CORRECCIÓN 1]: Pasamos 'personaje_activo' (que es el jefe) en vez de None
            # para que dibujar_barras_vida no falle.
            self.motor.animar_impacto(p1, p2, personaje_activo, mensaje, personaje_activo, "FUEGO")
            efecto_aplicado = True

        elif estado == "Sangrado":
            dano = 10
            personaje_activo.recibir_dano(dano)
            mensaje = f"¡{personaje_activo.nombre} sangra!\nPierde {dano} HP."
            
            # [CORRECCIÓN 1]: Pasamos 'personaje_activo' aquí también.
            self.motor.animar_impacto(p1, p2, personaje_activo, mensaje, personaje_activo, "SANGRE")
            efecto_aplicado = True

        elif estado == "Aturdido":
            mensaje = f"¡{personaje_activo.nombre} está ATURDIDO!\nPierde su turno."
            # Lógica de salida del nodo Aturdido
            personaje_activo.estado_actual = "Normal"
            pierde_turno = True
            
            # Visualización rápida
            self.motor.dibujar_interfaz(p1, p2, personaje_activo, mensaje) 
            pygame.display.flip()
            pygame.time.delay(2000)

        # Pausa dramática si hubo algún efecto visual
        if efecto_aplicado:
            pygame.time.delay(1000)
            
        return pierde_turno, mensaje

    def ejecutar_habilidad(self, atacante, defensor, habilidad, p1, p2, jefe):
        """
        FASE DE ACCIÓN: Ejecuta la habilidad seleccionada (1, 2, 3 o 4).
        Usa el Árbol Binario para calcular el éxito y el Grafo para transiciones.
        """
        mensaje_log = f"{atacante.nombre} usa {habilidad.nombre}!"
        
        # [CORRECCIÓN 2]: LÓGICA DE PROYECTILES
        # Determinamos posiciones y sprite según quién ataca y qué usa
        origen = (100, 230) if atacante == p1 else (350, 230)
        destino = (850, 230) # Posición del Jefe
        
        img_proyectil = None
        # Asignamos imagen según habilidad
        if "Molotov" in habilidad.nombre:
            img_proyectil = 'proy_molotov'
        elif "Disparo" in habilidad.nombre:
            img_proyectil = 'proy_disparo'
        elif "Cuchillada" in habilidad.nombre:
            img_proyectil = 'proy_cuchillo'
            
        # Si es un ataque ofensivo y tenemos imagen, lanzamos la animación antes del impacto
        if img_proyectil and habilidad.tipo == "ATAQUE":
             self.motor.animar_proyectil(p1, p2, jefe, mensaje_log, origen, destino, img_proyectil)

        # --- AHORA SI, EL CÁLCULO DEL EFECTO ---
        
        # CASO A: CURACIÓN
        if habilidad.tipo == "CURACION":
            objetivo = p1 if p1.vida_actual < p2.vida_actual else p2
            cantidad = abs(habilidad.dano)
            objetivo.curar(cantidad)
            mensaje_log += f"\nRecupera {cantidad} HP a {objetivo.nombre}"
            self.motor.animar_impacto(p1, p2, jefe, mensaje_log, objetivo, "CURACION")
        
        # CASO B: BUFF (Motivación)
        elif habilidad.tipo == "BUFF":
            mensaje_log += f"\n¡{atacante.nombre} se siente motivado!"
            self.motor.animar_impacto(p1, p2, jefe, mensaje_log, atacante, "NORMAL")
            
        # CASO C: DEFENSA (Escudo)
        elif habilidad.tipo == "DEFENSA":
            atacante.agregar_capa_escudo(1)
            mensaje_log += f"\n¡{atacante.nombre} levanta un Muro!"
            self.motor.animar_impacto(p1, p2, jefe, mensaje_log, atacante, "NORMAL")

        # CASO D: ATAQUE OFENSIVO (Usa Árbol y Grafo)
        else:
            # 1. Usar ÁRBOL BINARIO
            resultado = ArbolAtaque.ejecutar_ataque(habilidad.dano)
            
            if resultado.tipo == "TROPIEZO":
                atacante.recibir_dano(resultado.dano)
                mensaje_log += f"\n¡Tropiezo! Se hiere a sí mismo ({resultado.dano})"
                self.motor.animar_impacto(p1, p2, jefe, mensaje_log, atacante, "SANGRE")
            else:
                # 2. Aplicar Daño
                msg_escudo = defensor.recibir_dano(resultado.dano)
                mensaje_log += f"\n{resultado.mensaje} Daño: {resultado.dano}"
                if isinstance(msg_escudo, str): mensaje_log += f"\n{msg_escudo}"

                # 3. TRANSICIÓN DE GRAFO
                evento = habilidad.codigo_efecto 
                nuevo_estado = self.grafo.transicion(defensor.estado_actual, evento)
                
                if nuevo_estado != defensor.estado_actual:
                    defensor.estado_actual = nuevo_estado
                    mensaje_log += f"\n[EFECTO] ¡{defensor.nombre} pasa a {nuevo_estado}!"

                anim = "NORMAL"
                if nuevo_estado == "Quemado": anim = "FUEGO"
                elif nuevo_estado == "Sangrado": anim = "SANGRE"
                elif nuevo_estado == "Aturdido": anim = "CRITICO"
                
                # Animación de impacto final
                self.motor.animar_impacto(p1, p2, jefe, mensaje_log, defensor, anim)
        
        return mensaje_log