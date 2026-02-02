"""
ENTIDADES DEL JUEGO
-------------------
Define el comportamiento de los personajes y el Boss (Trump).
GUÍA DE MODIFICACIÓN:
1. CAMBIA ESTO: En 'recibir_dano' se define la lógica de la PILA de escudo.
2. CAMBIA ESTO: En 'recuperar_energia_turno' ajustas la velocidad de recarga.
"""

class Habilidad:
    """
    Objeto que representa un ataque o poder.
    Se carga con los diccionarios definidos en config.py[cite: 64, 66].
    """
    def __init__(self, datos_dict):
        self.nombre = datos_dict["nombre"]
        self.costo = datos_dict["costo"]
        self.descripcion = datos_dict["desc"]
        # Asegúrate de tener estos dos:
        self.dano = datos_dict.get("dano", 0) # Si no tiene daño, asume 0
        self.tipo = datos_dict.get("tipo", "NORMAL")
        self.codigo_efecto = datos_dict["efecto_code"]


class Personaje:
    """
    Clase principal para Soldados y Bosses[cite: 67, 68].
    MUEVES ESTO: Para que los personajes empiecen con más vida o energía.
    """
    def __init__(self, nombre, vida, ataque, energia, lista_habilidades_data):
        # Estadísticas Básicas del personaje [cite: 68, 70]
        self.nombre = nombre
        self.vida_actual = vida
        self.vida_max = vida
        self.ataque_base = ataque
        self.energia_actual = energia
        self.energia_max = energia
        
        # PILA (Stack): Para el escudo por capas
        self.pila_escudo = [] 

        self.turnos_quemado = 0
        
        # Guardamos el estado actual para transiciones en estructuras.py[cite: 17, 18, 19].
        self.estado_actual = "Normal" 
        
        # Carga de habilidades desde el diccionario de configuración[cite: 66, 70].
        self.habilidades = [Habilidad(data) for data in lista_habilidades_data]
        
        # Atributos para imágenes que se asignan en graficos.py[cite: 26, 71].
        self.sprite_idle = None

    def recibir_dano(self, cantidad):
        """
        LÓGICA DE IMPACTO: Primero revisa la PILA de escudo[cite: 73, 75, 78].
        MUEVES ESTO: Si quieres que el escudo sea más resistente.
        """
        # Si la pila tiene elementos, se elimina una capa (POP) y se anula el daño[cite: 75, 78].
        if len(self.pila_escudo) > 0:
            self.pila_escudo.pop() 
            return f"¡{self.nombre} bloqueó el daño con su escudo!"
        
        # Si no hay escudo en la pila, resta vida[cite: 75].
        self.vida_actual -= cantidad
        
        # Evitamos que la vida baje de cero
        if self.vida_actual < 0:
            self.vida_actual = 0
        
        return f"{self.nombre} recibió {cantidad} de daño."

    def agregar_capa_escudo(self, cantidad=1):
        """Añade elementos a la PILA de escudo (PUSH)[cite: 75, 78]."""
        for _ in range(cantidad):
            self.pila_escudo.append("Capa de Energía")

    def curar(self, cantidad):
        """Recupera salud sin exceder el máximo[cite: 78]."""
        self.vida_actual += cantidad
        if self.vida_actual > self.vida_max:
            self.vida_actual = self.vida_max

    def gastar_energia(self, cantidad):
        """Verifica si hay energía suficiente para ejecutar un ataque[cite: 79, 80]."""
        if self.energia_actual >= cantidad:
            self.energia_actual -= cantidad
            return True
        return False
    
    def recuperar_energia_turno(self):
        """Regeneración automática de energía al final del turno[cite: 81, 82]."""
        recuperacion = 10 
        self.energia_actual += recuperacion
        if self.energia_actual > self.energia_max:
            self.energia_actual = self.energia_max

    def esta_vivo(self):
        """Retorna True si el personaje sigue en pie[cite: 83]."""
        return self.vida_actual > 0

# Clase para el jefe final, hereda de Personaje
class Boss(Personaje):
    def __init__(self, nombre, vida, ataque, energia, habilidades):
        super().__init__(nombre, vida, ataque, energia, habilidades)