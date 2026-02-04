import json
import os

"""
SISTEMA DE GUARDADO
-------------------
Guarda y carga el estado del juego usando un archivo JSON.
Variables y claves en español.
"""

NOMBRE_ARCHIVO = "partida_guardada.json"

class SistemaGuardado:
    def __init__(self):
        pass

    def guardar_partida(self, p1, p2, jefe, es_turno_jugador, indice_personaje_actual):
        """
        Guarda las estadísticas vitales y el turno actual.
        """
        # Creamos el diccionario con todos los datos
        datos_a_guardar = {
            "global": {
                "es_turno_jugador": es_turno_jugador,  # Booleano (True/False)
                "indice_actual": indice_personaje_actual # 0 o 1
            },
            "jugador1": self._extraer_datos(p1),
            "jugador2": self._extraer_datos(p2),
            "jefe": self._extraer_datos(jefe)
        }

        try:
            with open(NOMBRE_ARCHIVO, "w") as archivo:
                json.dump(datos_a_guardar, archivo, indent=4)
            print("Partida guardada exitosamente.")
            return True
        except Exception as e:
            print(f"Error al guardar: {e}")
            return False

    def cargar_partida(self):
        """
        Lee el archivo JSON y devuelve el diccionario de datos.
        """
        if not os.path.exists(NOMBRE_ARCHIVO):
            return None
        
        try:
            with open(NOMBRE_ARCHIVO, "r") as archivo:
                return json.load(archivo)
        except Exception as e:
            print(f"Error al cargar: {e}")
            return None

    def _extraer_datos(self, personaje):
        """
        Extrae solo los datos necesarios de un objeto Personaje.
        """
        return {
            "vida": personaje.vida_actual,
            "energia": personaje.energia_actual,
            "estado": personaje.estado_actual,      # "Normal", "Quemado", etc.
            "turnos_estado": personaje.turnos_quemado, # Cuánto le falta al efecto
            "escudo": personaje.pila_escudo         # Lista de escudos
        }

    def aplicar_datos(self, personaje, datos_dict):
        """
        Sobrescribe los atributos del personaje con los datos cargados.
        """
        if not datos_dict: return

        # Usamos .get() por seguridad, si no existe usa el valor por defecto
        personaje.vida_actual = datos_dict.get("vida", personaje.vida_max)
        personaje.energia_actual = datos_dict.get("energia", 0)
        personaje.estado_actual = datos_dict.get("estado", "Normal")
        personaje.turnos_quemado = datos_dict.get("turnos_estado", 0)
        personaje.pila_escudo = datos_dict.get("escudo", [])
    def borrar_partida(self):
        """
        Elimina el archivo de guardado si existe (para Game Over o Victoria).
        """
        if os.path.exists(NOMBRE_ARCHIVO):
            try:
                os.remove(NOMBRE_ARCHIVO)
                print("Archivo de guardado eliminado.")
            except Exception as e:
                print(f"No se pudo borrar el archivo: {e}")