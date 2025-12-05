import database
from datetime import datetime, timedelta
import os

class AgendarCitaController:
    
    def __init__(self):
        self.lista_doctoras_bd = database.obtener_lista_doctoras()
        self.mapa_ids = {d['nombre']: d['id'] for d in self.lista_doctoras_bd}
        
    def obtener_info_doctoras(self):
        res = {}
        for d in self.lista_doctoras_bd:
            # 1. Asignación de imágenes
            foto = "default_doctor.png"
            if d['id'] == 1: foto = "doctora_1.jpg"
            elif d['id'] == 2: foto = "doctora_2.jpg"
            elif d['id'] == 3: foto = "doctora_3.jpg"
            
            # 2. Formato de Especialidad
            # "Cirujana Dentista - (Especialidad)" para las primeras dos
            especialidad_txt = d['especialidad']
            if d['id'] in [1, 2]:
                especialidad_txt = f"Cirujana Dentista - {d['especialidad']}"
            
            res[d['nombre']] = {
                "id": d['id'],
                "especialidad": especialidad_txt,
                "foto": foto 
            }
        return res

    def obtener_lista_nombres_doctoras(self):
        return [d['nombre'] for d in self.lista_doctoras_bd]
    
    def obtener_resumen_citas(self):
        database.sincronizar_estados_bd()
        hoy = datetime.now().strftime('%Y-%m-%d')
        return database.obtener_resumen_dia_bd(hoy)

    def buscar_pacientes_existentes(self, query):
        return database.buscar_clientes_rapido(query)
    
    # --- MENÚ DE SERVICIOS ---
    def buscar_servicios_filtros(self, nombre, cat, sub):
        return database.buscar_servicios_avanzado(nombre, cat, sub)
    
    def obtener_categorias_unicas(self):
        return database.obtener_columnas_unicas("categoria")

    def obtener_subcategorias_por_cat(self, categoria):
        return database.obtener_subcategorias_filtro(categoria)

    # --- HORARIOS (Lógica 5 minutos) ---
    def obtener_horas_inicio_disponibles(self, fecha_dt, nombre_doctora):
        doc_id = self.mapa_ids.get(nombre_doctora)
        if not doc_id: return []

        dia_sem = fecha_dt.weekday() 
        if dia_sem == 6: return [] 

        if dia_sem == 5: hora_apertura, hora_cierre = 11, 16
        else: hora_apertura, hora_cierre = 11, 20

        fecha_sql = fecha_dt.strftime("%Y-%m-%d")
        ocupadas = database.obtener_citas_dia_doctora(doc_id, fecha_sql)
        
        actual = datetime(fecha_dt.year, fecha_dt.month, fecha_dt.day, hora_apertura, 0)
        limite = datetime(fecha_dt.year, fecha_dt.month, fecha_dt.day, hora_cierre, 0)
        ahora_mismo = datetime.now()
        
        validas = []
        while actual < limite:
            # Filtro: Si es hoy, permitir hasta 10 min "atrasados" para dar margen
            if actual.date() == ahora_mismo.date() and actual < (ahora_mismo - timedelta(minutes=10)):
                actual += timedelta(minutes=5)
                continue
            
            choca = False
            for (ini, fin) in ocupadas:
                if isinstance(ini, timedelta): t_i, t_f = (datetime.min + ini).time(), (datetime.min + fin).time()
                else: t_i, t_f = ini, fin
                
                dt_i = datetime.combine(fecha_dt.date(), t_i)
                dt_f = datetime.combine(fecha_dt.date(), t_f)

                if actual >= dt_i and actual < dt_f:
                    choca = True; break
            
            if not choca: validas.append(actual.strftime("%I:%M %p"))
            
            # --- INTERVALO DE 5 MINUTOS ---
            actual += timedelta(minutes=5)
            
        return validas

    def obtener_duraciones_disponibles(self, fecha_dt, hora_str, nombre_doctora):
        # Legacy (ya no se usa visualmente, pero se mantiene por compatibilidad)
        return ["30 min"]

    def guardar_cita_completa(self, datos, servicios):
        doc_id = self.mapa_ids.get(datos['doctora'])
        if not doc_id: return False, "Doctora no válida"
        
        try:
            h_ini = datetime.strptime(datos['hora_inicio'], "%I:%M %p")
            
            # Procesar duración (viene del slider o texto)
            import re
            val_dur = str(datos['duracion'])
            nums = re.findall(r'\d+', val_dur)
            mins = 30
            
            if "h" in val_dur and "min" in val_dur and len(nums) >= 2: 
                mins = int(nums[0])*60 + int(nums[1])
            elif "h" in val_dur and len(nums) >= 1: 
                mins = int(nums[0])*60
            elif nums: 
                mins = int(nums[0])
            
            h_fin = h_ini + timedelta(minutes=mins)
            
            d_cli = {
                'id': datos['cliente_id_existente'], 'nombre': datos['nombre'],
                'telefono': datos['telefono'], 'email': datos['email'],
                'edad': datos['edad'], 'genero': datos['genero'],
                'notificar': datos['notificar'], 'previo_desc': datos.get('previo_desc')
            }
            
            desc = datos['descripcion']
            if datos['tipo_cita'] == "Tratamiento" and not desc and servicios:
                desc = servicios[0]['nombre']
                if len(servicios) > 1: desc += "..."
            if not desc: desc = "Consulta General"

            d_cita = {
                'doctora_id': doc_id, 'fecha': datos['fecha'],
                'hora_inicio': h_ini.strftime("%H:%M:%S"), 'hora_final': h_fin.strftime("%H:%M:%S"),
                'descripcion': desc, 'estado': 'Pendiente', 'tipo': datos['tipo_cita']
            }
            return database.guardar_cita_transaccional_bd(d_cli, d_cita, servicios)
        except Exception as e: return False, f"Error Controller: {e}"