import pygame
import sys
import config
from graficos import GestorGrafico
from entidades import Personaje
from estructuras import ArbolAtaque

"""
MAIN (PUNTO DE ENTRADA)
-----------------------
Controla el bucle principal del juego y los estados (Menú -> Juego).
"""

def main():
    pygame.init()
    reloj = pygame.time.Clock()
    
    # 1. Iniciar Motor Gráfico
    motor = GestorGrafico()
    
    # 2. Crear Entidades (Cargar Nivel 1)
    datos_nivel = config.NIVELES[0]
    
    # Jugador (Usamos P1 por defecto)
    jugador = Personaje(config.P1_NOMBRE, config.P1_VIDA_MAX, config.P1_ATAQUE, config.P1_ENERGIA_MAX, config.HABILIDADES_P1)
    
    # Jefe
    jefe = Personaje(datos_nivel["boss_nombre"], datos_nivel["boss_vida"], datos_nivel["boss_ataque"], 100, [])
    
    # Estado del juego
    estado = "MENU" # Puede ser "MENU" o "JUEGO"
    mensaje_log = "¡Batalla iniciada! Tu turno."

    # --- BUCLE PRINCIPAL ---
    while True:
        # A. Manejo de Eventos
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            if evento.type == pygame.KEYDOWN:
                if estado == "MENU":
                    if evento.key == pygame.K_RETURN:
                        estado = "JUEGO"
                        print("Cambiando a nivel 1...")
                
                elif estado == "JUEGO":
                    # PRUEBA RÁPIDA DE ATAQUE (Tecla ESPACIO)
                    if evento.key == pygame.K_SPACE:
                        resultado = ArbolAtaque.ejecutar_ataque(jugador.ataque_base)
                        mensaje_log = f"{resultado.mensaje} Daño: {resultado.dano}"
                        
                        # Aplicar daño
                        if resultado.tipo == "TROPIEZO":
                            jugador.recibir_dano(resultado.dano)
                        else:
                            jefe.recibir_dano(resultado.dano)

        # B. Dibujado (Render)
        if estado == "MENU":
            motor.dibujar_menu()
        
        elif estado == "JUEGO":
            motor.dibujar_batalla(jugador, jefe, mensaje_log)

        # Actualizar pantalla
        pygame.display.flip()
        reloj.tick(config.FPS)

if __name__ == "__main__":
    main()