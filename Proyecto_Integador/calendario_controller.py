from datetime import timedelta
import database

# --- CONFIGURACIÓN IMPORTANTE ---
# Aquí relacionamos el TEXTO que aparece en la vista con el ID REAL en la tabla 'usuarios'.
# DEBES VERIFICAR QUE ESTOS IDs (1, 2, 3) SEAN LOS DE TUS DOCTORAS EN TU BD.
MAPA_DOCTORAS_ID = {
    "Dra. Raquel Guzmán Reyes (Especialista en Ortodoncia)": 1,     # ID en tabla usuarios
    "Dra. Paola Jazmin Vera Guzmán (Especialista en Endodoncia)": 2, # ID en tabla usuarios
    "Dra. María Fernanda Cabrera Guzmán (Cirujana Dentista)": 3      # ID en tabla usuarios
}

class CalendarioController:
    def __init__(self):
        pass

    def obtener_citas_del_dia(self, fecha_datetime, filtros_doctoras_activas):
        """
        Recibe la fecha seleccionada y los checkboxes de la vista.
        Devuelve el diccionario organizado por estados.
        """
        # 1. Obtener qué IDs de doctoras (usuarios) se deben consultar
        ids_seleccionados = []
        for nombre_doc_view, variable_tk in filtros_doctoras_activas.items():
            if variable_tk.get() == "on":
                usuario_id = MAPA_DOCTORAS_ID.get(nombre_doc_view)
                if usuario_id:
                    ids_seleccionados.append(usuario_id)
        
        # 2. Estructura base para la vista
        data_vista = {
            'Pendientes': [],
            'En curso': [],
            'Completadas': [],
            'Canceladas': []
        }

        # Si no hay doctores seleccionados, retornamos vacío
        if not ids_seleccionados:
            return data_vista

        # 3. Consultar BD
        fecha_str = fecha_datetime.strftime('%Y-%m-%d')
        resultados = database.obtener_citas_filtro(fecha_str, ids_seleccionados)

        # 4. Transformar datos de BD al formato visual
        for fila in resultados:
            # Formatear hora (quitando segundos si vienen)
            hora_obj = fila['hora_inicio'] 
            if isinstance(hora_obj, timedelta):
                # Si la BD devuelve timedelta
                segundos = int(hora_obj.total_seconds())
                h = segundos // 3600
                m = (segundos % 3600) // 60
                hora_str = f"{h:02}:{m:02}"
            else:
                # Si devuelve objeto time o string
                hora_str = str(hora_obj)[:5]

            duracion = fila['duracion_minutos']
            
            # Construir el objeto para la tarjeta visual
            item = {
                'hora': f"{hora_str} ({duracion} min)",
                'paciente': fila['paciente_nombre_completo'], # Viene del CONCAT en database.py
                'tratamiento': fila['motivo_cita'],
                'doctora': fila['doctora_nombre_completo'],   # Viene del CONCAT en database.py
                'telefono': fila['telefono'] or 'Sin registro',
                'nota': '' # Si quieres agregar notas, deberías añadirlas al SELECT
            }

            # Clasificar según el estado exacto que tengas en la BD
            estado = fila['estado']
            # Ajusta estos strings a como los guardes exactamente en tu BD
            if estado in ['Pendiente', 'Programada']:
                data_vista['Pendientes'].append(item)
            elif estado in ['En curso', 'En proceso', 'Atendiendo']:
                data_vista['En curso'].append(item)
            elif estado in ['Completada', 'Finalizada', 'Terminada']:
                data_vista['Completadas'].append(item)
            elif estado in ['Cancelada', 'No asistió']:
                data_vista['Canceladas'].append(item)
            else:
                # Por defecto a pendientes si no coincide
                data_vista['Pendientes'].append(item)

        return data_vista

    def obtener_dias_ocupados(self, year, month):
        return database.obtener_dias_con_citas_mes(month, year)
    