import database
from datetime import datetime, timedelta, date

class ModificarCitaController:
    def __init__(self):
        self.lista_doctoras = database.obtener_lista_doctoras()
        self.mapa_ids = {d['nombre']: d['id'] for d in self.lista_doctoras}

    def obtener_cita_data(self, cita_id):
        return database.obtener_detalle_completo_cita(cita_id)

    def _generar_slots_base(self):
        slots = []
        start = datetime.strptime("11:00", "%H:%M")
        end = datetime.strptime("20:00", "%H:%M")
        while start < end:
            slots.append(start.strftime("%H:%M:%S"))
            # CAMBIO AQUI: Intervalos de 5 minutos en lugar de 30
            start += timedelta(minutes=5)
        return slots

    def obtener_horas_disponibles_edicion(self, fecha_dt, nombre_doc, cita_id):
        doc_id = self.mapa_ids.get(nombre_doc)
        if not doc_id: return []

        # CORRECCIÓN: Usamos 'obtener_citas_filtro' que SÍ existe en tu database.py
        # Pasamos el ID del doctor como una lista porque así lo pide esa función
        citas_dia = database.obtener_citas_filtro(fecha_dt.date(), [str(doc_id)])

        slots_base = self._generar_slots_base()
        disponibles = []

        for slot in slots_base:
            slot_start = datetime.strptime(slot, "%H:%M:%S").time()
            slot_end_dt = datetime.combine(date.min, slot_start) + timedelta(minutes=30) # Duración "visual" del slot para checar colisión
            slot_end = slot_end_dt.time()
            
            ocupado = False
            for c in citas_dia:
                # Ignorar la cita actual que estamos editando
                if str(c['id']) == str(cita_id):
                    continue
                
                # Manejo seguro de horas (por si vienen como timedelta o time)
                raw_ini = c['hora_inicio']
                raw_fin = c['hora_final']
                c_ini = (datetime.min + raw_ini).time() if isinstance(raw_ini, timedelta) else raw_ini
                c_fin = (datetime.min + raw_fin).time() if isinstance(raw_fin, timedelta) else raw_fin

                # Checar colisión
                if (c_ini < slot_end and c_fin > slot_start):
                    ocupado = True
                    break
            
            if not ocupado:
                # Convertir a formato amigable "09:00 AM"
                dt_obj = datetime.strptime(slot, "%H:%M:%S")
                disponibles.append(dt_obj.strftime("%I:%M %p"))

        # Asegurar que la hora ACTUAL de la cita esté en la lista
        data_actual = self.obtener_cita_data(cita_id)
        if data_actual and 'cita' in data_actual:
            f_actual = data_actual['cita']['fecha_cita']
            if f_actual == fecha_dt.date():
                raw_time = data_actual['cita']['hora_inicio']
                t = (datetime.min + raw_time).time() if isinstance(raw_time, timedelta) else raw_time
                h_str = t.strftime("%I:%M %p")
                if h_str not in disponibles:
                    disponibles.append(h_str)
                    disponibles.sort(key=lambda x: datetime.strptime(x, "%I:%M %p"))

        return disponibles

    def obtener_datos_paciente_id(self, cita_id):
        """Helper para recuperar telefono/email de una cita específica"""
        data = database.obtener_detalle_completo_cita(cita_id)
        if data and 'cita' in data:
            c = data['cita']
            return {'nombre': c['nombre_completo'], 'telefono': c['telefono'], 'email': c['email'], 'notif': c['notificacion']}
        return None

    def guardar_cambios(self, cita_id, datos_nuevos, usuario_responsable_id):
        doc_id = self.mapa_ids.get(datos_nuevos['doctora'])
        if not doc_id: return "error", "Doctora no válida.", []

        afectados_notif = [] 

        try:
            # Preparar horas SQL
            h_str = datos_nuevos['hora_inicio']
            try: h_dt = datetime.strptime(h_str, "%I:%M %p"); h_sql = h_dt.strftime("%H:%M:%S")
            except: h_sql = h_str 

            dur_mins = int(datos_nuevos['duracion_minutos'])
            h_ini_dt = datetime.strptime(h_sql, "%H:%M:%S")
            h_fin_dt = h_ini_dt + timedelta(minutes=dur_mins)
            h_fin_sql = h_fin_dt.strftime("%H:%M:%S")
            
            # 1. DETECCIÓN DE CONFLICTO
            conflicto = database.ejecutar_sp_fetch_one("sp_obtener_conflicto_futuro", (doc_id, datos_nuevos['fecha'], h_sql, h_fin_sql, cita_id))

            if conflicto:
                id_conflictivo = conflicto[0]
                hora_inicio_estorbo = conflicto[1]
                
                # Calcular movimiento
                if isinstance(hora_inicio_estorbo, timedelta): t_estorbo = (datetime.min + hora_inicio_estorbo).time()
                else: t_estorbo = hora_inicio_estorbo
                
                dt_estorbo = datetime.combine(date.min, t_estorbo)
                if h_fin_dt > dt_estorbo:
                    diff = h_fin_dt - dt_estorbo
                    minutos_a_mover = int(diff.total_seconds() / 60)
                    
                    if minutos_a_mover > 0:
                        # --- VALIDACIÓN DE HORARIO LÍMITE ---
                        hora_limite = datetime.strptime("20:00:00", "%H:%M:%S").time()
                        if datos_nuevos['fecha'].weekday() == 5: 
                             hora_limite = datetime.strptime("16:00:00", "%H:%M:%S").time()

                        nueva_hora_fin_estimada = (dt_estorbo + timedelta(minutes=minutos_a_mover) + timedelta(minutes=30)).time()
                        
                        if nueva_hora_fin_estimada > hora_limite:
                            return "pregunta_dia", f"El ajuste recorre citas más allá de las {hora_limite}. ¿Deseas mover la cita conflictiva al día siguiente?", None

                        datos_afectado = self.obtener_datos_paciente_id(id_conflictivo)
                        if datos_afectado:
                            nueva_h_afectado = (dt_estorbo + timedelta(minutes=minutos_a_mover)).time().strftime("%I:%M %p")
                            afectados_notif.append({
                                'nombre': datos_afectado['nombre'],
                                'telefono': datos_afectado['telefono'],
                                'email': datos_afectado['email'],
                                'fecha': datos_nuevos['fecha'],
                                'hora': nueva_h_afectado,
                                'notif': datos_afectado['notif']
                            })

                        h_corte_sql = t_estorbo.strftime("%H:%M:%S")
                        database.ejecutar_sp("sp_recorrer_agenda", (doc_id, datos_nuevos['fecha'], h_corte_sql, minutos_a_mover, usuario_responsable_id))
            
            # 2. Guardar Cita Principal (CON LA CORRECCIÓN DE TRATAMIENTO PREVIO)
            desc_tx = datos_nuevos.get('previo_desc', '')
            
            # LÓGICA CORREGIDA: Detecta cualquiera de las palabras clave
            es_previo = ("Externa" in desc_tx) or ("Interno" in desc_tx) or ("Clínica" in desc_tx) or ("Ambas" in desc_tx)
            tp_val = 1 if es_previo else 0

            d_cli = {
                'id': datos_nuevos['cliente_id'], 
                'nombre': datos_nuevos['nombre'], 
                'telefono': datos_nuevos['telefono'], 
                'email': datos_nuevos['email'],
                'tp': tp_val,       # Se envía el valor calculado correctamente
                'desc': desc_tx     
            }
            
            d_cita = {
                'doctora_id': doc_id, 
                'fecha': datos_nuevos['fecha'], 
                'hora_inicio': h_sql, 
                'hora_final': h_fin_sql, 
                'descripcion': datos_nuevos['descripcion'], 
                'estado': datos_nuevos['estado']
            }

            ok = database.actualizar_cita_completa_bd(cita_id, d_cli, d_cita, usuario_responsable_id)
            if ok:
                return "ok", "Guardado correctamente.", afectados_notif
            else:
                return "error", "Error al actualizar BD.", []

        except Exception as e:
            return "error", f"Error técnico: {e}", []
    
    def mover_conflicto_siguiente_dia(self, cita_id_origen, fecha_origen, doctora_id, usuario_id):
        pass

    def cancelar_cita(self, cita_id, usuario_id):
        return database.cambiar_estado_cita_cancelada_bd(cita_id, usuario_id)
    
    
    