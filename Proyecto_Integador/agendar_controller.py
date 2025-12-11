import database
from datetime import datetime, timedelta
import os

class AgendarCitaController:
    
    def __init__(self):
        # Cargar lista de la BD al iniciar
        self.lista_doctoras = database.obtener_lista_doctoras()
        # Mapa para buscar rápido ID por Nombre
        self.mapa_ids = {d['nombre']: d['id'] for d in self.lista_doctoras}
        # Mapa inverso para buscar Nombre por ID (usado para sugerir doctora)
        self.mapa_nombres = {d['id']: d['nombre'] for d in self.lista_doctoras}
        
    def obtener_info_doctoras_visual(self):
        """
        Prepara los datos para la UI.
        Prioridad: 
        1. Foto definida en BD (campo 'foto_perfil').
        2. Emoji según género (fallback).
        """
        resultado = {}
        
        for d in self.lista_doctoras:
            doc_id = d['id']
            nombre = d['nombre']
            especialidad = d['especialidad']
            ruta_bd = d.get('foto_perfil') 
            
            foto_final = None
            tipo_visual = "emoji"

            # 1. Verificar si hay ruta en BD y si el archivo existe
            if ruta_bd and os.path.exists(ruta_bd):
                foto_final = ruta_bd
                tipo_visual = "archivo"
            else:
                # 2. Fallback a Emoji
                if "dra" in nombre.lower():
                    foto_final = "👩‍⚕️"
                else:
                    foto_final = "👨‍⚕️"
            
            resultado[nombre] = {
                "id": doc_id,
                "especialidad": especialidad,
                "foto": foto_final,
                "tipo": tipo_visual
            }
            
        return resultado

    def obtener_lista_nombres_doctoras(self):
        return [d['nombre'] for d in self.lista_doctoras]
    
    # --- SUGERENCIA DE DOCTORA ---
    def obtener_doctor_sugerido(self, cliente_id):
        """Busca la última doctora con la que se atendió el paciente."""
        try:
            # Buscamos en un rango amplio hacia atrás (ej. 2 años)
            hoy = datetime.now()
            inicio = (hoy - timedelta(days=730)).strftime("%Y-%m-%d")
            fin = hoy.strftime("%Y-%m-%d")
            
            # Reutilizamos la función de base de datos que ya existe para rangos
            # Nota: Asumimos que database tiene esta función (usada en calendario)
            citas = database.obtener_citas_rango_paciente(inicio, fin, cliente_id)
            
            if citas:
                # Ordenamos por fecha descendente (la más reciente primero)
                # Asegúrate que 'fecha_cita' sea datetime o string comparable
                citas.sort(key=lambda x: x['fecha_cita'], reverse=True)
                ultimo_doc_id = citas[0]['doctora_id']
                return self.mapa_nombres.get(ultimo_doc_id)
        except:
            pass
        return None

    # --- LÓGICA DE TIEMPO (5 minutos) ---
    def obtener_horas_inicio_disponibles(self, fecha_dt, nombre_doctora):
        doc_id = self.mapa_ids.get(nombre_doctora)
        if not doc_id: return []

        dia_sem = fecha_dt.weekday() 
        if dia_sem == 6: return [] # Domingo cerrado

        # Horarios (Configurable)
        if dia_sem == 5: # Sábado
            hora_apertura, hora_cierre = 11, 16 
        else: # Lunes-Viernes
            hora_apertura, hora_cierre = 11, 20

        fecha_sql = fecha_dt.strftime("%Y-%m-%d")
        ocupadas = database.obtener_citas_dia_doctora(doc_id, fecha_sql)
        
        actual = datetime(fecha_dt.year, fecha_dt.month, fecha_dt.day, hora_apertura, 0)
        limite = datetime(fecha_dt.year, fecha_dt.month, fecha_dt.day, hora_cierre, 0)
        ahora_mismo = datetime.now()
        
        validas = []
        while actual < limite:
            if actual.date() == ahora_mismo.date() and actual < (ahora_mismo - timedelta(minutes=10)):
                actual += timedelta(minutes=5)
                continue
            
            choca = False
            for (ini, fin) in ocupadas:
                if isinstance(ini, timedelta): 
                    t_i = (datetime.min + ini).time()
                    t_f = (datetime.min + fin).time()
                else: 
                    t_i, t_f = ini, fin
                
                dt_i = datetime.combine(fecha_dt.date(), t_i)
                dt_f = datetime.combine(fecha_dt.date(), t_f)

                if actual >= dt_i and actual < dt_f:
                    choca = True; break
            
            if not choca: 
                validas.append(actual.strftime("%I:%M %p"))
            
            actual += timedelta(minutes=5)
            
        return validas

    # --- GUARDAR CITA ---
    def guardar_cita_completa(self, datos, servicios, usuario_responsable_id):
        doc_id = self.mapa_ids.get(datos['doctora'])
        if not doc_id: return False, "Doctora no seleccionada."
        
        try:
            h_ini = datetime.strptime(datos['hora_inicio'], "%I:%M %p")
            
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
            
            esta_libre = database.verificar_disponibilidad_sp(
                doc_id, 
                datos['fecha'], 
                h_ini.strftime("%H:%M:%S"), 
                h_fin.strftime("%H:%M:%S")
            )
            
            if not esta_libre:
                return False, "⚠️ Error: El horario seleccionado acaba de ser ocupado."

            d_cli = {
                'cliente_id_existente': datos.get('cliente_id_existente'), 
                'nombre': datos['nombre'],
                'telefono': datos['telefono'], 
                'email': datos['email'],
                'edad': datos['edad'], 
                'genero': datos['genero'],
                'notificar': datos['notificar'], 
                'previo_desc': datos.get('previo_desc')
            }
            
            desc = datos['descripcion']
            if datos['tipo_cita'] == "Tratamiento" and not desc and servicios:
                desc = servicios[0]['nombre']
                if len(servicios) > 1: desc += f" (+{len(servicios)-1})"
            if not desc: desc = "Consulta General"

            d_cita = {
                'doctora_id': doc_id, 
                'fecha': datos['fecha'],
                'hora_inicio': h_ini.strftime("%H:%M:%S"), 
                'hora_final': h_fin.strftime("%H:%M:%S"),
                'descripcion': desc, 
                'estado': 'Pendiente', 
                'tipo': datos['tipo_cita']
            }
            
            return database.guardar_cita_transaccional_bd(d_cli, d_cita, servicios, usuario_responsable_id)

        except Exception as e: 
            return False, f"Error interno: {e}"

    # --- HELPERS ---
    def buscar_pacientes_existentes(self, query):
        return database.buscar_clientes_rapido(query)
    
    def obtener_resumen_citas(self): 
        database.sincronizar_estados_bd()
        return database.obtener_resumen_dia_bd(datetime.now().strftime('%Y-%m-%d'))
    
    def obtener_categorias_unicas(self):
        return database.obtener_columnas_unicas("categoria")

    def obtener_subcategorias_por_cat(self, c):
        return database.obtener_subcategorias_filtro(c)

    def buscar_servicios_filtros(self, n, c, s):
        return database.buscar_servicios_avanzado(n, c, s)
    