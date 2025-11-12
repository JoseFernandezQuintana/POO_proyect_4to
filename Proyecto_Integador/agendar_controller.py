# agendar_controller.py
from database import crear_conexion
from mysql.connector import Error

class AgendarCitaController:
    """Clase para manejar la lógica de agendamiento y datos de doctoras."""
    
    def obtener_doctoras(self):
        """Simula la obtención de la lista de doctoras desde la BD."""
        
        # Se ajusta el formato para que el view pueda separar el nombre de la especialidad
        lista_doctoras = [
            "Dra. Raquel Guzmán Reyes (Ortodoncia)",
            "Dra. Paola Jazmin Vera Guzmán (Endodoncia)",
            "Dra. María Fernanda Cabrera (Cirugía General)"
        ]
        return lista_doctoras

    def agendar_cita(self, datos_cita):
        """Intenta agendar una cita en la base de datos."""
        
        # Aquí va la implementación de la lógica de guardado en BD
        print("Datos de la cita recibidos:", datos_cita)
        # Lógica de guardar en BD:
        # try:
        #     conexion = crear_conexion()
        #     cursor = conexion.cursor()
        #     ... (código de inserción)
        #     conexion.commit()
        #     return True
        # except Error as e:
        #     print(f"Error al agendar cita: {e}")
        #     return False
        
        return True # Simulación de éxito
    
