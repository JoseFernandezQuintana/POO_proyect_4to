import database
from datetime import datetime, timedelta

# Mapeo de UI -> ID Base de Datos
# Asegúrate de que estos IDs (1, 2, 3) existan en tu tabla 'usuarios' con rol de doctora
MAPA_DOCTORAS_ID = {
    "Dra. Raquel Guzmán Reyes (Ortodoncia)": 1,
    "Dra. Paola Jazmin Vera Guzmán (Endodoncia)": 2,
    "Dra. María Fernanda Cabrera (Cirugía General)": 3
}

class AgendarCitaController:
    
    def obtener_doctoras(self):
        """Devuelve la lista de nombres para el Dropdown."""
        return list(MAPA_DOCTORAS_ID.keys())

    def obtener_datos_resumen(self):
        """Obtiene los datos numéricos reales para la tabla de resumen."""
        return database.obtener_conteo_citas_global()

    def generar_horarios_disponibles(self, fecha_datetime):
        """
        Genera la lista de horas disponibles basado en reglas:
        - Lunes a Viernes: 11:00 - 20:00
        - Sábados: 11:00 - 16:00
        - Domingos: Cerrado
        Intervalos de 15 minutos.
        """
        dia_semana = fecha_datetime.weekday() # 0=Lun, 6=Dom
        
        if dia_semana == 6: # Domingo
            return [] 

        hora_inicio = 11
        hora_fin = 16 if dia_semana == 5 else 20 # Sábado cierra a las 16, resto a las 20

        horarios = []
        current_time = datetime(fecha_datetime.year, fecha_datetime.month, fecha_datetime.day, hora_inicio, 0)
        end_time = datetime(fecha_datetime.year, fecha_datetime.month, fecha_datetime.day, hora_fin, 0)

        while current_time < end_time:
            horarios.append(current_time.strftime("%H:%M"))
            current_time += timedelta(minutes=15)
            
        return horarios

    def guardar_cita(self, datos_form):
        """
        Valida y guarda la cita.
        Retorna: (Bool Exito, String Mensaje)
        """
        # 1. Validaciones Básicas
        if not datos_form['nombre']:
            return False, "El nombre del paciente es obligatorio."
        
        if datos_form['doctora'] == "Selecciona una doctora":
            return False, "Debes seleccionar una doctora."
            
        if not datos_form['fecha'] or not datos_form['hora'] or datos_form['hora'] == "--:--":
            return False, "Selecciona una fecha y hora válida."

        # 2. Obtener ID de Doctora
        doctora_id = MAPA_DOCTORAS_ID.get(datos_form['doctora'])
        if not doctora_id:
            return False, "Error interno: Doctora no identificada."

        # 3. Verificar Disponibilidad en BD
        # Convertimos fecha objeto a string SQL 'YYYY-MM-DD'
        fecha_sql = datos_form['fecha_obj'].strftime('%Y-%m-%d')
        
        esta_libre = database.verificar_disponibilidad(doctora_id, fecha_sql, datos_form['hora'])
        
        if not esta_libre:
            return False, f"La {datos_form['doctora'].split('(')[0]} ya tiene una cita a las {datos_form['hora']}."

        # 4. Preparar datos para insertar
        datos_bd = {
            'doctora_id': doctora_id,
            'fecha': fecha_sql,
            'hora': datos_form['hora'],
            'motivo': datos_form['motivo'] if datos_form['motivo'] else "Consulta General",
            'notas': datos_form['notas']
        }

        # 5. Guardar
        if database.registrar_cita(datos_bd):
            return True, "Cita agendada correctamente."
        else:
            return False, "Error al guardar en la base de datos."
        