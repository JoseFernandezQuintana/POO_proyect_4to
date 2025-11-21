import database
from datetime import datetime, timedelta

# Mapeo Inverso (Nombre -> ID) para guardar
MAPA_DOCTORAS_ID = {
    "Dra. Raquel Guzmán Reyes (Ortodoncia)": 1,
    "Dra. Paola Jazmin Vera Guzmán (Endodoncia)": 2,
    "Dra. María Fernanda Cabrera (Cirugía General)": 3
}

# Mapeo Directo (ID -> Nombre) para cargar datos
MAPA_ID_DOCTORAS = {v: k for k, v in MAPA_DOCTORAS_ID.items()}

class ModificarCitaController:
    
    def buscar_citas_flexibles(self, query):
        """Busca en la BD usando SQL LIKE."""
        if not query or len(query) < 2:
            return []
        
        raw_results = database.buscar_citas_bd(query)
        processed = []
        
        for r in raw_results:
            # Formatear para el dropdown
            fecha = r['fecha_cita'] # Puede ser objeto date o string
            hora = str(r['hora_inicio'])
            display_text = f"ID {r['cita_id']} | {r['paciente']} | {fecha} {hora}"
            
            processed.append({
                'display': display_text,
                'id': r['cita_id']
            })
        return processed

    def obtener_datos_cita(self, cita_id):
        """Obtiene detalle y formatea para la vista."""
        raw = database.obtener_cita_por_id(cita_id)
        if not raw:
            return None
            
        # Recuperar nombre completo de doctora basado en ID
        nombre_doc = MAPA_ID_DOCTORAS.get(raw['doctora_id'], "Desconocido")
        
        # Formatear hora (quitar segundos)
        hora_str = str(raw['hora_inicio'])
        if len(hora_str) > 5: hora_str = hora_str[:5]

        return {
            'id': raw['id'],
            'nombre_completo': f"{raw['nombre']} {raw['apellido']}",
            'doctora': nombre_doc,
            'fecha_obj': raw['fecha_cita'], # Objeto date
            'fecha_str': raw['fecha_cita'].strftime('%d/%m/%Y'),
            'hora': hora_str,
            'motivo': raw['motivo_cita'],
            'notas': raw['notas']
        }

    def obtener_doctoras(self):
        return list(MAPA_DOCTORAS_ID.keys())

    def generar_horarios_disponibles(self, fecha_datetime):
        """Misma lógica que en Agendar."""
        dia_semana = fecha_datetime.weekday() 
        if dia_semana == 6: return [] # Domingo cerrado

        hora_inicio = 11
        hora_fin = 16 if dia_semana == 5 else 20 

        horarios = []
        current = datetime(fecha_datetime.year, fecha_datetime.month, fecha_datetime.day, hora_inicio, 0)
        end = datetime(fecha_datetime.year, fecha_datetime.month, fecha_datetime.day, hora_fin, 0)

        while current < end:
            horarios.append(current.strftime("%H:%M"))
            current += timedelta(minutes=15)
        return horarios

    def guardar_modificacion(self, cita_id, datos_form):
        # 1. Validar
        doc_id = MAPA_DOCTORAS_ID.get(datos_form['doctora'])
        if not doc_id: return False, "Doctora no válida."
        
        if datos_form['hora'] == "--:--": return False, "Hora no válida."

        # 2. Verificar disponibilidad (Opcional: permitir misma hora si es la misma cita)
        # Por simplicidad, asumimos que el recepcionista sabe lo que hace al modificar,
        # o podrías reutilizar database.verificar_disponibilidad excluyendo el ID actual.

        datos_bd = {
            'doctora_id': doc_id,
            'fecha': datos_form['fecha_obj'].strftime('%Y-%m-%d'),
            'hora': datos_form['hora'],
            'motivo': datos_form['motivo'],
            'notas': datos_form['notas']
        }
        
        if database.actualizar_cita_bd(cita_id, datos_bd):
            return True, "Cita modificada correctamente."
        return False, "Error al actualizar en BD."

    def cancelar_cita(self, cita_id):
        if database.cancelar_cita_bd(cita_id):
            return True, "Cita cancelada correctamente."
        return False, "Error al cancelar."
    