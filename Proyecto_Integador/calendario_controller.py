import database
from datetime import datetime

class CalendarioController:
    def __init__(self):
        self.lista_doctoras = database.obtener_lista_doctoras()
        
    def obtener_doctoras_activas(self):
        return self.lista_doctoras

    def buscar_pacientes_lista(self, query):
        # Wrapper para la función de base de datos
        return database.buscar_clientes_rapido(query)

    def buscar_paciente_id(self, nombre):
        if not nombre: return None
        res = database.buscar_clientes_rapido(nombre)
        return res[0]['id'] if res else None

    def obtener_estilos_dias(self, year, month, id_paciente=None, ids_doctoras=None):
        bold_days = set()
        blue_days = set()
        
        # Calcular rangos
        inicio = f"{year}-{month:02d}-01"
        if month == 12: fin = f"{year+1}-01-01"
        else: fin = f"{year}-{month+1:02d}-01"

        # 1. Días con citas de las doctoras seleccionadas (Negritas/Indicador)
        if ids_doctoras:
            # Nota: database.py devuelve 'fecha_cita'
            citas = database.obtener_citas_rango_doctoras(inicio, fin, ids_doctoras)
            for c in citas:
                try: 
                    # Aseguramos que sea datetime
                    fecha = c['fecha_cita']
                    if isinstance(fecha, str):
                        fecha = datetime.strptime(fecha, "%Y-%m-%d")
                    bold_days.add(fecha.day)
                except: pass

        # 2. Días del paciente seleccionado (Azules)
        if id_paciente:
            citas_p = database.obtener_citas_rango_paciente(inicio, fin, id_paciente)
            for c in citas_p:
                try: 
                    fecha = c['fecha_cita']
                    if isinstance(fecha, str):
                        fecha = datetime.strptime(fecha, "%Y-%m-%d")
                    blue_days.add(fecha.day)
                except: pass
                
        return bold_days, blue_days

    def obtener_citas_dia(self, fecha_dt, ids_doctoras):
        fecha_str = fecha_dt.strftime("%Y-%m-%d")
        return database.obtener_citas_filtro(fecha_str, ids_doctoras)
    