from datetime import datetime, timedelta
import database

# ID DOCTORAS (Verifica que coincidan con tu BD)
MAPA_DOCTORAS_ID = {
    "Dra. Raquel Guzmán Reyes (Especialista en Ortodoncia)": 1,
    "Dra. Paola Jazmin Vera Guzmán (Especialista en Endodoncia)": 2,
    "Dra. María Fernanda Cabrera Guzmán (Cirujana Dentista)": 3
}

class CalendarioController:
    def __init__(self):
        pass

    def obtener_citas_del_dia(self, fecha_datetime, filtros_doctoras_activas):
        # 1. Filtros
        if fecha_datetime.date() == datetime.now().date():
            database.sincronizar_estados_bd()

        ids_seleccionados = []
        for nombre_doc_view, variable_tk in filtros_doctoras_activas.items():
            if variable_tk.get() == "on":
                uid = MAPA_DOCTORAS_ID.get(nombre_doc_view)
                if uid: ids_seleccionados.append(uid)
        
        data_vista = {'Pendientes': [], 'En curso': [], 'Completadas': [], 'Canceladas': []}
        if not ids_seleccionados: return data_vista

        # 2. Consulta BD
        fecha_str = fecha_datetime.strftime('%Y-%m-%d')
        # obtener_citas_filtro hace SELECT c.*, así que trae 'tipo'
        resultados = database.obtener_citas_filtro(fecha_str, ids_seleccionados)

        # 3. Procesar
        for fila in resultados:
            # Hora
            hora_obj = fila['hora_inicio'] 
            if isinstance(hora_obj, timedelta):
                seg = int(hora_obj.total_seconds())
                hora_str = f"{seg//3600:02}:{(seg%3600)//60:02}"
            else:
                hora_str = str(hora_obj)[:5]

            # Objeto Visual
            item = {
                'id': fila['id'],
                'hora': f"{hora_str} ({fila.get('duracion_minutos', 30)} min)",
                'paciente': fila['paciente_nombre_completo'],
                'tratamiento': fila.get('descripcion') or fila.get('motivo_cita', 'Sin descripción'),
                'doctora': fila['doctora_nombre_completo'],
                'telefono': fila.get('telefono', 'Sin registro'),
                'tipo': fila.get('tipo', 'Consulta') # <--- AQUÍ RECUPERAMOS EL TIPO
            }

            # Clasificación
            est = fila['estado']
            # Mapeo simple a las 4 categorías visuales
            if est in ['Pendiente', 'Programada']: cat = 'Pendientes'
            elif est in ['En curso', 'En proceso', 'Atendiendo']: cat = 'En curso'
            elif est in ['Completada', 'Finalizada']: cat = 'Completadas'
            elif est in ['Cancelada']: cat = 'Canceladas'
            else: cat = 'Pendientes'
            
            data_vista[cat].append(item)

        return data_vista

    def obtener_dias_ocupados(self, year, month):
        return database.obtener_dias_con_citas_mes(month, year)
    
    def obtener_estado_dias_mes(self, year, month):
        # Reutilizamos la función existente
        dias_ocupados = database.obtener_dias_con_citas_mes(month, year)
        return dias_ocupados
    