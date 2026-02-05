import json
import os

"""
SISTEMA DE GUARDADO (PERSISTENCIA DE DATOS JSON)

GUÍA RÁPIDA DE MODIFICACIÓN (SAVEDATA):
-----------------------------------------------------------------------------------------
SECCIÓN / LÓGICA        | MÉTODO / VARIABLE     | ACCIÓN / CÓMO MODIFICAR
-----------------------------------------------------------------------------------------
1. ARCHIVO              | NOMBRE_ARCHIVO        | Define el nombre del fichero en disco.
                        |                       | (Por defecto: "partida_guardada.json").
-----------------------------------------------------------------------------------------
2. ESTRUCTURA GENERAL   | guardar_partida()     | Crea el esqueleto del JSON.
   (El Diccionario)     | - "global": {...}     | - Si agregas variables globales (ej.
                        |                       |   "Nivel 2"), agrégalas aquí.
-----------------------------------------------------------------------------------------
3. SELECCIÓN DE DATOS   | _extraer_datos()      | **CRÍTICO: QUÉ GUARDAR**
   (De Objeto a JSON)   | - datos = {...}       | - Si añades un atributo nuevo al
                        |                       |   Personaje (ej. 'mana'), debes
                        |                       |   escribirlo en este diccionario.
                        | - if hasattr(p, 'st') | - Lógica para guardar datos únicos
                        |                       |   del Boss (Estrés) o Buffs.
-----------------------------------------------------------------------------------------
4. CARGA DE DATOS       | aplicar_datos()       | **CRÍTICO: QUÉ RECUPERAR**
   (De JSON a Objeto)   | - .get("clave", 0)    | - Es el espejo de _extraer_datos.
                        |                       |   Usa .get() para poner un valor
                        |                       |   por defecto si el save es antiguo.
-----------------------------------------------------------------------------------------
5. LIMPIEZA             | borrar_partida()      | Se llama en Game Over / Victoria.
                        | - os.remove()         | Elimina el archivo físico para
                        |                       | impedir reiniciar trampas.
-----------------------------------------------------------------------------------------
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
        # Creo el diccionario base con las estadísticas que comparten tanto los jugadores como el jefe.
        datos = {
            "vida": personaje.vida_actual,
            "energia": personaje.energia_actual,
            "estado": personaje.estado_actual,      
            "turnos_estado": personaje.turnos_quemado, 
            "escudo": personaje.pila_escudo         
        }

        # Aquí verifico si el personaje tiene la mecánica de Estrés (es decir, si es el Jefe).
        # Si es así, lo agrego al archivo para que recuerde qué tan enojado estaba.
        if hasattr(personaje, 'st'):
            datos["st"] = personaje.st

        # para guardar los contadores de los potenciadores (Buffs) 
        if hasattr(personaje, 'turnos_buff_ataque'):
            datos["buff_ataque"] = personaje.turnos_buff_ataque
            datos["buff_defensa"] = personaje.turnos_buff_defensa
            
        return datos

    def aplicar_datos(self, personaje, datos_dict):
        """
        Sobrescribe los atributos del personaje con los datos cargados.
        """
        if not datos_dict: return

        # Restauro los valores estándar usando .get() por seguridad (si no existe la clave, usa un valor por defecto).
        personaje.vida_actual = datos_dict.get("vida", personaje.vida_max)
        personaje.energia_actual = datos_dict.get("energia", 0)
        personaje.estado_actual = datos_dict.get("estado", "Normal")
        personaje.turnos_quemado = datos_dict.get("turnos_estado", 0)
        personaje.pila_escudo = datos_dict.get("escudo", [])

        # Si detecto que este personaje es el Jefe (tiene el atributo st),
        # le restauro su nivel de estrés tal cual estaba.
        if hasattr(personaje, 'st'):
            personaje.st = datos_dict.get("st", 0)

        # De igual forma, si es capaz de tener buffs, recupero los contadores guardados.
        if hasattr(personaje, 'turnos_buff_ataque'):
            personaje.turnos_buff_ataque = datos_dict.get("buff_ataque", 0)
            personaje.turnos_buff_defensa = datos_dict.get("buff_defensa", 0)
    
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