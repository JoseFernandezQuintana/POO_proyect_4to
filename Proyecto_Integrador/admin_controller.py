import database

class AdminController:
    
    def __init__(self):
        pass

    # --- GESTIÓN DE USUARIOS ---
    def obtener_usuarios(self):
        return database.admin_obtener_usuarios()
    
    def obtener_usuario_por_id(self, uid):
        users = self.obtener_usuarios()
        for u in users:
            if u['id'] == uid: return u
        return None

    def crear_usuario(self, nombre, user, pasw, rol, especialidad="General"):
        if not nombre or not user or not pasw or not rol: 
            return False, "Todos los campos son obligatorios."
        if len(pasw) < 4: 
            return False, "La contraseña es muy corta (mínimo 4)."
        if database.admin_existe_usuario(user): 
            return False, "El usuario ya existe."
        return database.admin_guardar_usuario(nombre, user, pasw, rol, especialidad)
    
    def actualizar_usuario(self, uid, nombre, user, rol, pasw="", especialidad="General"):
        if not nombre or not user: return False, "Nombre y Usuario obligatorios."
        return database.admin_actualizar_usuario(uid, nombre, user, rol, pasw if pasw.strip() else None, especialidad)

    def eliminar_usuario(self, uid_a_borrar, uid_sesion_actual, rol_sesion_actual):
        if uid_a_borrar == uid_sesion_actual:
            return False, "⚠️ ACCIÓN DENEGADA\nNo puedes eliminar tu propia cuenta mientras estás conectado."
        target = self.obtener_usuario_por_id(uid_a_borrar)
        if target and target['rol'] == 'Administrador' and rol_sesion_actual != 'Administrador':
             return False, "⚠️ ACCIÓN DENEGADA\nSolo un Administrador puede eliminar a otro Administrador."
        return database.admin_eliminar_usuario(uid_a_borrar)

    # --- SERVICIOS Y CATÁLOGO ---
    def validar_supervisor(self, user, pwd):
        if not user or not pwd: return False
        return database.validar_credenciales_supervisor(user, pwd)

    def obtener_categorias(self):
        """Wrapper para obtener categorías únicas"""
        return database.obtener_columnas_unicas("categoria")

    def obtener_subcategorias(self, categoria):
        return database.obtener_subcategorias_filtro(categoria)

    def buscar_servicios(self, query, categoria, subcategoria):
        """Wrapper para búsqueda avanzada de servicios"""
        return database.buscar_servicios_avanzado(query, categoria, subcategoria)

    def crear_servicio_avanzado(self, cat, sub, nom, lista_tuplas):
        if not cat or not nom or not lista_tuplas: 
            return False, "Faltan datos obligatorios."
        
        dict_final = {}
        for unidad, precio_str in lista_tuplas:
            if not unidad.strip(): continue
            try:
                p = float(precio_str)
                if p < 0: return False, "No se admiten precios negativos."
                dict_final[unidad] = p
            except:
                return False, f"El precio para '{unidad}' no es válido."
        
        if not dict_final: return False, "Debes definir al menos un precio."
        return database.admin_guardar_servicio_complejo(cat, sub, nom, dict_final)

    def actualizar_precio(self, sid, precio):
        try: 
            p = float(precio)
            if p < 0: return False, "Precio negativo."
            return database.admin_actualizar_precio_servicio(sid, p)
        except: return False, "Precio inválido."

    def actualizar_precio_variante(self, servicio_id, nombre_variante, precio_nuevo):
        return database.admin_actualizar_precio_variante_json(servicio_id, nombre_variante, precio_nuevo)
    
    def eliminar_servicio(self, sid):
        return database.admin_eliminar_servicio(sid)

    # --- REPORTES Y GRÁFICAS ---
    def obtener_kpis(self): return database.reporte_kpis_generales()

    def datos_grafica_pastel(self): 
        d = database.reporte_top_tratamientos()
        if not d: return [], []
        return ([x[0] for x in d], [x[1] for x in d])

    def datos_grafica_linea(self):
        d = database.reporte_ingresos_semestral()
        d.reverse()
        return ([x[0] for x in d], [float(x[1]) for x in d])
    
    def datos_grafica_metodos_pago(self):
        data = database.reporte_pagos_metodo()
        return ([x[0] for x in data], [float(x[1]) for x in data])

    def datos_grafica_estados_cita(self):
        data = database.reporte_estado_citas()
        return ([x[0] for x in data], [x[1] for x in data])

    def datos_grafica_tipos_cita(self):
        data = database.reporte_citas_tipo()
        return ([x[0] for x in data], [x[1] for x in data])

    def datos_demografia(self):
        edades = database.reporte_demografia_edad()
        generos = database.reporte_demografia_genero()
        gen_labels = []
        gen_vals = []
        for g, cant in generos:
            lbl = "Mujer" if g == 'f' else "Hombre"
            gen_labels.append(lbl)
            gen_vals.append(cant)
        return (([x[0] for x in edades], [x[1] for x in edades]), (gen_labels, gen_vals))

    def datos_rendimiento_doctores(self):
        data = database.reporte_top_doctores()
        names = []
        for row in data:
            full_name = row[0]
            short_name = full_name.split(' ')[0] 
            if "Dra." in full_name: short_name = "Dra. " + full_name.split(' ')[1]
            names.append(short_name)
        return (names, [x[1] for x in data])
    
    def obtener_datos_comparativos(self):
        ia, i_ant, pa, p_ant = database.reporte_kpis_comparativos()
        def calc_perc(act, ant):
            if ant == 0: return 100 if act > 0 else 0
            return ((act - ant) / ant) * 100
        return {
            "ingreso_actual": ia, "ingreso_anterior": i_ant, "ingreso_perc": calc_perc(ia, i_ant),
            "pac_actual": pa, "pac_anterior": p_ant, "pac_perc": calc_perc(pa, p_ant)
        }

    def obtener_info_pacientes_header(self):
        return database.reporte_info_pacientes_completa()

    def datos_grafica_semanal(self):
        raw = database.reporte_comparativo_semanal()
        semanas = [f"Sem {x[0]}" for x in raw]
        cantidades = [x[1] for x in raw]
        return semanas, cantidades
    