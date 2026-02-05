"""
ENTIDADES DEL JUEGO (LÓGICA DE CLASES)

GUÍA RÁPIDA DE MODIFICACIÓN (MÉTODOS Y LÓGICA):
-----------------------------------------------------------------------------------------
CLASE / SECCIÓN         | MÉTODO / VARIABLE     | ACCIÓN / CÓMO MODIFICAR
-----------------------------------------------------------------------------------------
1. CLASE HABILIDAD      | __init__              | Mapea datos de config.py a objetos.
                        |                       | Cambiar '.get("tipo", "NORMAL")'
                        |                       | para alterar valores por defecto.
-----------------------------------------------------------------------------------------
2. LOGICA DE DAÑO       | recibir_dano()        | En 'if hasattr... * 0.5':
   (Personaje)          |                       | Cambiar 0.5 para ajustar la reducción
                        |                       | de daño del buff defensivo.
                        |-----------------------|----------------------------------------
                        | pila_escudo (Logic)   | Modificar lógica .pop() si quieres
                        |                       | que el escudo no se rompa de 1 golpe.
-----------------------------------------------------------------------------------------
3. ENERGÍA              | recuperar_energia...()| Busca variable 'recuperacion = 10'.
   (Personaje)          |                       | Cambia el 10 para dar más/menos
                        |                       | energía automática al fin del turno.
                        |-----------------------|----------------------------------------
                        | gastar_energia()      | En 'cantidad // 2':
                        |                       | Cambia el divisor para ajustar
                        |                       | el beneficio del estado 'Motivado'.
-----------------------------------------------------------------------------------------
4. JEFE (BOSS)          | __init__ (st_max)     | Cambiar 'self.st_max = 100'
                        |                       | para limitar la barra de estrés (IA).
-----------------------------------------------------------------------------------------
"""

class Habilidad:
    """
    Clase que encapsula la lógica de una acción de combate.
    Se pasa un diccionario que tendrá todas las caracteristicas 
    de los ataques (configurado en config)
    """
    def __init__(self, datos_dict):
        # Extraemos los valores del diccionario de configuración.
        # Esto conecta directamente la lógica del juego con los datos estáticos.
        self.nombre = datos_dict["nombre"]
        self.costo = datos_dict["costo"]
        self.descripcion = datos_dict["desc"]
        
        # Uso el método .get() para propiedades opcionales.
        # si no encuentra asume valores predeterminados
        self.dano = datos_dict.get("dano", 0) 
        self.tipo = datos_dict.get("tipo", "NORMAL")
        self.codigo_efecto = datos_dict["efecto_code"] # Clave para el motor de efectos.


class Personaje:
    """
    Clase base que define el estado y comportamiento de cualquier entidad viva.
    Maneja la salud, la energía y las estructuras de defensa.
    """
    def __init__(self, nombre, vida, ataque, energia, lista_habilidades_data):
        # Inicialización de estadísticas vitales.
        # Mantenemos vida_max para cálculos de porcentaje o curaciones completas.
        self.nombre = nombre
        self.vida_actual = vida
        self.vida_max = vida
        self.ataque_base = ataque
        self.energia_actual = energia
        self.energia_max = energia
        
        # Usamos una lista como pila para manejar los escudos.
        # Lógica LIFO (Last In, First Out): El último escudo puesto es el primero en romperse.
        self.pila_escudo = [] 

        # Contador de estado alterado. Si es mayor a 0, el personaje sufre daño por turno.
        self.turnos_quemado = 0
        self.turnos_motivado = 0
        # Máquina de estados simple.
        # Controla si el personaje está en reposo, atacando o recibiendo daño
        # para coordinar las animaciones en el módulo de gráficos.
        self.estado_actual = "Normal" 
        
        # Aquí convertimos la lista de diccionarios (JSON-like) en una lista
        # de objetos reales de tipo Habilidad usando una "list comprehension".
        self.habilidades = [Habilidad(data) for data in lista_habilidades_data]
        
        # Placeholder para el sprite. Se asigna externamente para no acoplar
        # la lógica del juego con la librería gráfica (Pygame) aquí mismo.
        self.sprite_idle = None

    def recibir_dano(self, cantidad):
        """
        Calcula el daño final recibido por la entidad.
        Aquí es donde la estructura de PILA cobra sentido para la mecánica de juego.
        """
        # Inicializo el daño real con el valor original que llega del ataque.
        dano_final = cantidad
        
        # Antes de nada, compruebo si el personaje tiene activa alguna mejora defensiva (como la 'Táctica' del Jefe).
        # Si es así, corto el daño a la mitad para que se sienta el impacto de la estrategia defensiva y consumo un turno del efecto.
        if hasattr(self, 'turnos_buff_defensa') and self.turnos_buff_defensa > 0:
            dano_final = int(cantidad * 0.5)
            self.turnos_buff_defensa -= 1

        # Verificación de la PILA de escudos.
        if len(self.pila_escudo) > 0:
            # Operación POP: Eliminamos el elemento superior de la pila.
            # Mecánicamente, esto significa que una capa de escudo absorbe
            # TODO el daño del ataque, sin importar cuánto sea (incluso si venía reducido).
            self.pila_escudo.pop() 
            return f"¡{self.nombre} bloqueó el daño con su escudo!"
        
        # Si la pila está vacía, el daño calculado afecta directamente al atributo de vida.
        self.vida_actual -= dano_final
        
        # Clamp (restricción) para evitar valores negativos en la interfaz de usuario.
        if self.vida_actual < 0:
            self.vida_actual = 0
        
        # Devuelvo el mensaje confirmando cuánto daño entró realmente al final.
        return f"{self.nombre} recibió {dano_final} de daño."

    def agregar_capa_escudo(self, cantidad=1):
        """
        Operación PUSH en la pila de escudos.
        Agrega capas de protección que deben ser destruidas antes de tocar la vida.
        """
        for _ in range(cantidad):
            self.pila_escudo.append("Capa de Energía")

    def curar(self, cantidad):
        """
        Aumenta la vida actual respetando el límite superior (vida_max).
        """
        self.vida_actual += cantidad
        if self.vida_actual > self.vida_max:
            self.vida_actual = self.vida_max

    def gastar_energia(self, cantidad):
        costo_real = cantidad
        
        # Si está motivado, el costo baja a la mitad (división entera)
        if self.turnos_motivado > 0:
            costo_real = cantidad // 2
            
        if self.energia_actual >= costo_real:
            self.energia_actual -= costo_real
            return True
        return False
    
    def recuperar_energia_turno(self):
        """
        Mecánica de ciclo de juego: Al finalizar el turno, las entidades
        recuperan recursos pasivamente para mantener el ritmo del combate.
        """
        recuperacion = 10 
        self.energia_actual += recuperacion
        if self.energia_actual > self.energia_max:
            self.energia_actual = self.energia_max

    def esta_vivo(self):
        """
        Helper booleano para verificar rápidamente el estado de derrota
        en el bucle principal del juego.
        """
        return self.vida_actual > 0

class Boss(Personaje):
    def __init__(self, nombre, vida, ataque, energia, habilidades):
        super().__init__(nombre, vida, ataque, energia, habilidades)
        # Variable requerida por el Grafo de Comportamiento
        self.st = 0      # Nivel Inicial: 0
        self.st_max = 100 
        self.turnos_buff_ataque = 0  # Para cuando usa Molotov+
        self.turnos_buff_defensa = 0 # Para cuando usa Táctica
    
    def aumentar_estres(self, cantidad):
        self.st += cantidad
        if self.st > self.st_max:
            self.st = self.st_max
            
    def reducir_estres(self, cantidad):
        self.st -= cantidad
        if self.st < 0:
            self.st = 0
        
