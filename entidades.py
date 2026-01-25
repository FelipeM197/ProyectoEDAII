

"""
---------------------------------------------
En este archivo se definieron todos los objetos que le darán vida tanto a bosses como
personajes jugables

GUÍA DE MODIFICACIÓN:
1. Para cambiar la lógica de recibir daño (Vida) ....... Línea 63
2. Para cambiar el consumo de energía ..................  Línea 95
3. Para ver la estructura de una Habilidad ............. Línea 20
4. Para la logica de curarse ........................... Linea 88
5. Para cambiar la recuperacion de energía..............  Línea 108
"""

class Habilidad:
    """
    Objeto de datos que representa una acción de ataque o defensa.
    Se carga con los datos definidos en config.py.
    """
    def __init__(self, datos_dict):
        self.nombre = datos_dict["nombre"]
        self.costo = datos_dict["costo"]
        self.descripcion = datos_dict["desc"]
        self.id_efecto = datos_dict["id"]
        self.codigo_efecto = datos_dict["efecto_code"] 

class Personaje:
    """
    Clase principal que define al jugador y al jefe.
    Implementa las estadísticas definidas por el Integrante A:
    - Vida 
    - Daño Base 
    - Energía 
    """
    def __init__(self, nombre, vida, ataque, energia, lista_habilidades_data):
        self.nombre = nombre
        
        self.vida_actual = vida
        self.vida_max = vida
        self.energia_actual = energia
        self.energia_max = energia
        
        self.ataque_base = ataque
        
        # Diccionario para guardar efectos como {"quemado": True, "escudo": 30}
        self.estados = {} 
        
        # Cargar habilidades
        #Obtiene los datos del diccionario y los usa para llenar la lista de habilidades
        # NOTA: se le pasará una lista de diccionarios
        self.habilidades = [Habilidad(data) for data in lista_habilidades_data]
        
        """ Ejemplo de uso: 
            soldado = Personaje("Rambo", 100, 20, 100, lista_datos)
            mi_habilidad = soldado.habilidades[0] (hace referencia a la primera habilidad)
            mi_habiliad.nombre = nombre de la habilidad
            mi_habilidad.dano = daño del ataque ...
        """
        # Placeholder para gráficos (Se llenará en graficos.py)
        self.sprite_idle = None
        self.sprite_atacando = None
        self.sprite_dano = None

    def recibir_dano(self, cantidad):
        """
        Reduce la vida del personaje según el daño recibido.
        Incluye la lógica de 'Escudo' (Muro de Contención) si está activo.
        """
        # 1. Verificar si hay estados defensivos 
        if "escudo" in self.estados:
            escudo_val = self.estados["escudo"]
            # El escudo absorbe el daño
            absorcion = min(escudo_val, cantidad)
            self.estados["escudo"] -= absorcion
            cantidad -= absorcion
            
            # Si el escudo se rompe, se elimina del estado
            if self.estados["escudo"] <= 0:
                del self.estados["escudo"]
        
        # Aplicar daño directo a la Vida 
        self.vida_actual -= cantidad
        
        # Evitar vida negativa
        if self.vida_actual < 0:
            self.vida_actual = 0

    def curar(self, cantidad):
        
        #Recupera vida sin superar el máximo.
        
        self.vida_actual += cantidad
        if self.vida_actual > self.vida_max:
            self.vida_actual = self.vida_max

    def gastar_energia(self, cantidad):
        """
        Intenta gastar energía para una habilidad.
        Retorna True si tuvo suficiente energía, False si no.
        Fuente: 
        """
        if self.energia_actual >= cantidad:
            self.energia_actual -= cantidad
            return True
        return False
    
    def recuperar_energia_turno(self):
        """
        Pequeña regeneración de energía por turno (Opcional de diseño).
        """
        recuperacion = 10 
        self.energia_actual += recuperacion
        if self.energia_actual > self.energia_max:
            self.energia_actual = self.energia_max

    def esta_vivo(self):

        """
        Retorna True si la vida es mayor a 0.
        """
        return self.vida_actual > 0
    
class Trump: 
    print("te toca jordy")