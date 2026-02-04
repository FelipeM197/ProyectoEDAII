"""
ENTIDADES DEL JUEGO
-------------------
Este módulo contiene la lógica orientada a objetos para los actores del juego.
Aquí definimos cómo se comportan los datos que configuramos en config.py.

INDICE RÁPIDO PARA MODIFICACIONES:
-------------------------------------------------
Línea 23  -> Clase Habilidad (Manejo de diccionarios de datos)
Línea 42  -> Clase Personaje (Estado y atributos)
Línea 75  -> Lógica de Escudos (Estructura de datos PILA/Stack)
Línea 95  -> Sistema de Salud y Energía
Línea 126 -> Clase Boss (Herencia)
-------------------------------------------------
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
        # Verificación de la PILA de escudos.
        if len(self.pila_escudo) > 0:
            # Operación POP: Eliminamos el elemento superior de la pila.
            # Mecánicamente, esto significa que una capa de escudo absorbe
            # TODO el daño del ataque, sin importar cuánto sea.
            self.pila_escudo.pop() 
            return f"¡{self.nombre} bloqueó el daño con su escudo!"
        
        # Si la pila está vacía, el daño afecta directamente al atributo de vida.
        self.vida_actual -= cantidad
        
        # Clamp (restricción) para evitar valores negativos en la interfaz de usuario.
        if self.vida_actual < 0:
            self.vida_actual = 0
        
        return f"{self.nombre} recibió {cantidad} de daño."

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
        """
        Gestión de recursos. Valida si la operación es posible antes de restar.
        Retorna un booleano para que la interfaz sepa si el ataque procedió o falló.
        """
        if self.energia_actual >= cantidad:
            self.energia_actual -= cantidad
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
        # Uso de super() para invocar el constructor de la clase padre (Personaje).
        # Esto garantiza que el Boss tenga todos los atributos base (vida, pila de escudos, etc.)
        # sin tener que duplicar el código de inicialización.
        super().__init__(nombre, vida, ataque, energia, habilidades)

        
