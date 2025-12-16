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
        # Generamos slots cada 5 minutos para mayor precisión
        start = datetime.strptime("11:00", "%H:%M")
        end = datetime.strptime("20:00", "%H:%M")
        while start < end:
            slots.append(start.strftime("%H:%M:%S"))
            start += timedelta(minutes=5)
        return slots

    def obtener_horas_disponibles_edicion(self, fecha_dt, nombre_doc, cita_id):
        doc_id = self.mapa_ids.get(nombre_doc)
        if not doc_id: return []

        # Obtener citas del día para ese doctor
        citas_dia = database.obtener_citas_filtro(fecha_dt.date(), [str(doc_id)])
        slots_base = self._generar_slots_base()
        disponibles = []

        for slot in slots_base:
            slot_start = datetime.strptime(slot, "%H:%M:%S").time()
            slot_end_dt = datetime.combine(date.min, slot_start) + timedelta(minutes=30)
            slot_end = slot_end_dt.time()
            
            ocupado = False
            for c in citas_dia:
                if str(c['id']) == str(cita_id): continue # Ignorar la propia cita
                
                raw_ini = c['hora_inicio']
                raw_fin = c['hora_final']
                c_ini = (datetime.min + raw_ini).time() if isinstance(raw_ini, timedelta) else raw_ini
                c_fin = (datetime.min + raw_fin).time() if isinstance(raw_fin, timedelta) else raw_fin

                if (c_ini < slot_end and c_fin > slot_start):
                    ocupado = True
                    break
            
            if not ocupado:
                dt_obj = datetime.strptime(slot, "%H:%M:%S")
                hora_12 = dt_obj.strftime("%I:%M %p").lstrip("0")
                disponibles.append(hora_12)

        # Asegurar que la hora ACTUAL de la cita esté en la lista
        data_actual = self.obtener_cita_data(cita_id)
        if data_actual and 'cita' in data_actual:
            f_actual = data_actual['cita']['fecha_cita']
            if f_actual == fecha_dt.date():
                raw_time = data_actual['cita']['hora_inicio']
                t = (datetime.min + raw_time).time() if isinstance(raw_time, timedelta) else raw_time
                h_str = t.strftime("%I:%M %p").lstrip("0")
                if h_str not in disponibles:
                    disponibles.append(h_str)
                    disponibles.sort(key=lambda x: datetime.strptime(x, "%I:%M %p"))

        return disponibles

    def guardar_cambios(self, cita_id, datos_nuevos, usuario_responsable_id, forzar_horario=False):
        """
        Guarda cambios. Si detecta conflicto > 8pm y no se fuerza, retorna status especial.
        """
        doc_id = self.mapa_ids.get(datos_nuevos['doctora'])
        if not doc_id: return "error", "Doctora no válida.", []

        afectados_notif = [] 

        try:
            # 1. Preparar horas SQL
            h_str = datos_nuevos['hora_inicio'] 
            try: 
                h_dt = datetime.strptime(h_str, "%I:%M %p")
                h_sql = h_dt.strftime("%H:%M:%S") 
            except: 
                h_sql = h_str 

            dur_mins = int(datos_nuevos['duracion_minutos'])
            h_ini_dt = datetime.strptime(h_sql, "%H:%M:%S")
            h_fin_dt = h_ini_dt + timedelta(minutes=dur_mins)
            h_fin_sql = h_fin_dt.strftime("%H:%M:%S")
            
            # 2. DETECCIÓN DE CONFLICTO
            conflicto = database.ejecutar_sp_fetch_one("sp_obtener_conflicto_futuro", (doc_id, datos_nuevos['fecha'], h_sql, h_fin_sql, cita_id))

            if conflicto:
                id_conflictivo = conflicto[0]
                hora_inicio_estorbo = conflicto[1]
                
                # Calcular cuánto se empalma
                if isinstance(hora_inicio_estorbo, timedelta): t_estorbo = (datetime.min + hora_inicio_estorbo).time()
                else: t_estorbo = hora_inicio_estorbo
                
                dt_estorbo = datetime.combine(date.min, t_estorbo)
                
                if h_fin_dt > dt_estorbo:
                    diff = h_fin_dt - dt_estorbo
                    minutos_a_mover = int(diff.total_seconds() / 60)
                    
                    if minutos_a_mover > 0:
                        # --- LÓGICA DE CIERRE ---
                        hora_cierre = datetime.strptime("20:00:00", "%H:%M:%S").time()
                        
                        # Estimamos dónde terminaría la ÚLTIMA cita si empujamos todo
                        nueva_hora_fin_conflictiva = (dt_estorbo + timedelta(minutes=minutos_a_mover) + timedelta(minutes=30)).time()
                        
                        # SI NO ESTAMOS FORZANDO y se pasa de las 8pm
                        if not forzar_horario and nueva_hora_fin_conflictiva > hora_cierre:
                            
                            datos_afectado = self.obtener_datos_paciente_id(id_conflictivo)
                            nombre_afectado = datos_afectado['nombre'] if datos_afectado else "Siguiente Paciente"
                            
                            fin_12h = nueva_hora_fin_conflictiva.strftime("%I:%M %p")
                            
                            msg = (f"Al extender la duración, la cita de {nombre_afectado} se recorrería "
                                   f"terminando a las {fin_12h}.\n\n"
                                   f"El consultorio cierra a las 08:00 PM.\n\n"
                                   "¿Qué deseas hacer?")
                            
                            return "conflicto_cierre", msg, {'id_conflicto': id_conflictivo, 'minutos': minutos_a_mover}

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

                        # Ejecutar SP para mover agenda en cascada
                        h_corte_sql = t_estorbo.strftime("%H:%M:%S")
                        database.ejecutar_sp("sp_recorrer_agenda", (doc_id, datos_nuevos['fecha'], h_corte_sql, minutos_a_mover, usuario_responsable_id))
            
            # 3. Guardar Cita Principal
            desc_tx = datos_nuevos.get('previo_desc', '')
            es_previo = ("Externa" in desc_tx) or ("Interno" in desc_tx) or ("Clínica" in desc_tx) or ("Ambas" in desc_tx)
            tp_val = 1 if es_previo else 0

            d_cli = {
                'id': datos_nuevos['cliente_id'], 
                'nombre': datos_nuevos['nombre'], 
                'telefono': datos_nuevos['telefono'], 
                'email': datos_nuevos['email'],
                'tp': tp_val,       
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

    def buscar_sugerencia_siguiente_dia(self, cita_id_conflictiva, fecha_origen, minutos_duracion):
        """
        Busca hueco al día siguiente.
        Prioridad 1: Misma hora.
        Prioridad 2: +/- 30 minutos.
        Prioridad 3: Primer hueco libre.
        """
        data_cita = database.obtener_detalle_completo_cita(cita_id_conflictiva)
        if not data_cita: return None
        
        cita = data_cita['cita']
        nombre_doc = cita['doctora_nombre']
        
        # Calcular fecha siguiente (saltando domingos)
        siguiente_dia = fecha_origen + timedelta(days=1)
        if siguiente_dia.weekday() == 6: # Si es domingo
            siguiente_dia += timedelta(days=1) # Lunes
            
        # Hora original (objeto time)
        raw_time = cita['hora_inicio']
        hora_original = (datetime.min + raw_time).time() if isinstance(raw_time, timedelta) else raw_time
        
        # Consultar disponibilidad del día siguiente
        dt_siguiente = datetime.combine(siguiente_dia, datetime.min.time())
        horas_libres_str = self.obtener_horas_disponibles_edicion(dt_siguiente, nombre_doc, 0)
        
        horas_libres_obj = []
        for h_str in horas_libres_str:
            try: horas_libres_obj.append(datetime.strptime(h_str, "%I:%M %p").time())
            except: pass
            
        if not horas_libres_obj:
            return {"status": "lleno", "fecha": siguiente_dia}

        # 1. Misma hora exacta
        if hora_original in horas_libres_obj:
            return {
                "status": "encontrado",
                "tipo": "Misma hora",
                "fecha": siguiente_dia,
                "hora": hora_original.strftime("%I:%M %p").lstrip("0"),
                "paciente": cita['nombre_completo']
            }
            
        # 2. Cercano (+/- 30 mins)
        min_start = (datetime.combine(date.min, hora_original) - timedelta(minutes=30)).time()
        max_start = (datetime.combine(date.min, hora_original) + timedelta(minutes=30)).time()
        
        for h in horas_libres_obj:
            if min_start <= h <= max_start:
                return {
                    "status": "encontrado",
                    "tipo": "Horario cercano",
                    "fecha": siguiente_dia,
                    "hora": h.strftime("%I:%M %p").lstrip("0"),
                    "paciente": cita['nombre_completo']
                }

        # 3. Primer hueco disponible
        primera = horas_libres_obj[0]
        return {
            "status": "encontrado",
            "tipo": "Primer hueco disponible",
            "fecha": siguiente_dia,
            "hora": primera.strftime("%I:%M %p").lstrip("0"),
            "paciente": cita['nombre_completo']
        }

    def mover_cita_a_fecha(self, cita_id, nueva_fecha, nueva_hora_str, usuario_id):
        """Mueve una cita específica a otra fecha/hora"""
        try:
            # Convertir hora
            h_dt = datetime.strptime(nueva_hora_str, "%I:%M %p")
            h_sql = h_dt.strftime("%H:%M:%S")
            
            # Necesitamos recalcular la hora final basada en la duración original
            data = database.obtener_detalle_completo_cita(cita_id)
            if not data: return False
            
            # Calcular duración original
            raw_ini = data['cita']['hora_inicio']
            raw_fin = data['cita']['hora_final']
            
            # Normalizar a timedelta
            td_ini = raw_ini if isinstance(raw_ini, timedelta) else timedelta(hours=raw_ini.hour, minutes=raw_ini.minute)
            td_fin = raw_fin if isinstance(raw_fin, timedelta) else timedelta(hours=raw_fin.hour, minutes=raw_fin.minute)
            duracion = td_fin - td_ini
            
            # Nuevos tiempos
            nuevo_inicio_dt = datetime.combine(nueva_fecha, h_dt.time())
            nuevo_fin_dt = nuevo_inicio_dt + duracion
            h_fin_sql = nuevo_fin_dt.strftime("%H:%M:%S")
            
            # Actualizar BD
            conn = database.crear_conexion()
            cursor = conn.cursor()
            sql = "UPDATE citas SET fecha_cita=%s, hora_inicio=%s, hora_final=%s, estado='Pendiente' WHERE id=%s"
            cursor.execute(sql, (nueva_fecha, h_sql, h_fin_sql, cita_id))
            
            # Bitácora
            cursor.execute("INSERT INTO bitacora_acciones (usuario_id, accion, tabla, detalle_nuevo) VALUES (%s, 'MOVER_DIA', 'citas', %s)", 
                           (usuario_id, f"Mueve Cita {cita_id} a {nueva_fecha} {h_sql}"))
            
            conn.commit()
            conn.close()
            return True
            
        except Exception as e:
            print(f"Error moviendo cita: {e}")
            return False

    def obtener_datos_paciente_id(self, cita_id):
        """Helper para recuperar datos contacto"""
        data = database.obtener_detalle_completo_cita(cita_id)
        if data and 'cita' in data:
            c = data['cita']
            return {'nombre': c['nombre_completo'], 'telefono': c['telefono'], 'email': c['email'], 'notif': c['notificacion']}
        return None

    def cancelar_cita(self, cita_id, usuario_id):
        return database.cambiar_estado_cita_cancelada_bd(cita_id, usuario_id)
