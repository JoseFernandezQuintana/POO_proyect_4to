import database
from datetime import datetime, timedelta

MAPA_DOCTORAS = {
    "Dra. Raquel Guzmán Reyes": {"id": 1, "especialidad": "Ortodoncia", "foto": "doctora_1.jpg"},
    "Dra. Paola Jazmin Vera Guzmán": {"id": 2, "especialidad": "Endodoncia", "foto": "doctora_2.jpg"},
    "Dra. María Fernanda Cabrera": {"id": 3, "especialidad": "Cirugía General", "foto": "doctora_3.jpg"}
}

class ModificarCitaController:
    
    def obtener_lista_nombres_doctoras(self): return list(MAPA_DOCTORAS.keys())
    def obtener_info_doctoras(self): return MAPA_DOCTORAS
    
    def calcular_estado_tiempo_real(self, fecha_bd, hora_ini, hora_fin):
        try:
            ahora = datetime.now()
            fecha_str = fecha_bd.strftime("%Y-%m-%d") if isinstance(fecha_bd, (datetime, object)) else str(fecha_bd)
            dt_inicio = datetime.strptime(f"{fecha_str} {str(hora_ini)}", "%Y-%m-%d %H:%M:%S")
            dt_fin = datetime.strptime(f"{fecha_str} {str(hora_fin)}", "%Y-%m-%d %H:%M:%S")
            
            if ahora < dt_inicio: return "Pendiente"
            elif dt_inicio <= ahora <= dt_fin: return "En curso"
            else: return "Completada"
        except: return "Pendiente"

    def buscar_citas(self, query):
        database.sincronizar_estados_bd()
        if not query.strip(): citas = database.obtener_citas_en_curso_bd()
        else: citas = database.buscar_citas_por_paciente_bd(query)
        for c in citas:
            c['estado_calc'] = c['estado']
        return citas

    def obtener_cita_completa(self, cita_id): return database.obtener_detalle_completo_cita(cita_id)

    def actualizar_cita(self, cita_id, datos):
        info_doc = MAPA_DOCTORAS.get(datos['doctora'])
        if not info_doc: return False, "Doctora inválida"
        try:
            h_ini = datetime.strptime(datos['hora_inicio'], "%I:%M %p")
            import re
            nums = re.findall(r'\d+', datos['duracion'])
            mins = 30
            if "h" in datos['duracion'] and "min" in datos['duracion']: mins = int(nums[0])*60 + int(nums[1])
            elif "h" in datos['duracion']: mins = int(nums[0])*60
            elif nums: mins = int(nums[0])
            h_fin = h_ini + timedelta(minutes=mins)
            
            nuevo_estado = self.calcular_estado_tiempo_real(datos['fecha'], h_ini.strftime("%H:%M:%S"), h_fin.strftime("%H:%M:%S"))

            d_cli = {'id': datos['cliente_id'], 'nombre': datos['nombre'], 'telefono': datos['telefono'], 'email': datos['email'], 'edad': datos['edad'], 'genero': datos['genero']}
            d_cita = {'doctora_id': info_doc['id'], 'fecha': datos['fecha'], 'hora_inicio': h_ini.strftime("%H:%M:%S"), 'hora_final': h_fin.strftime("%H:%M:%S"), 'tipo': datos['tipo_cita'], 'descripcion': datos['descripcion'], 'estado': nuevo_estado}
            
            return database.actualizar_cita_completa_bd(cita_id, d_cli, d_cita), "Cita actualizada."
        except Exception as e: return False, str(e)

    def cambiar_estado_cancelada(self, cita_id):
        import database
        conn = database.crear_conexion()
        if not conn: return False
        try:
            c = conn.cursor(); c.execute("UPDATE citas SET estado='Cancelada' WHERE id=%s", (cita_id,)); conn.commit(); return True
        except: return False
        finally: conn.close()

    def borrar_cita_definitiva(self, cita_id): return database.borrar_cita_definitiva_bd(cita_id)
        
    def obtener_horas_inicio_disponibles(self, *args): 
        from agendar_controller import AgendarCitaController
        return AgendarCitaController().obtener_horas_inicio_disponibles(*args)
        
    def obtener_duraciones_disponibles(self, *args):
        from agendar_controller import AgendarCitaController
        return AgendarCitaController().obtener_duraciones_disponibles(*args)
    
    def buscar_servicios_filtros(self, nombre, cat, sub): return database.buscar_servicios_avanzado(nombre, cat, sub)
    def obtener_categorias_unicas(self): return database.obtener_columnas_unicas("categoria")
    def obtener_subcategorias_por_cat(self, c): return database.obtener_subcategorias_filtro(c)