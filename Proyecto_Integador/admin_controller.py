import database

class AdminController:
    
    def __init__(self):
        pass

    # --- USUARIOS ---
    def obtener_usuarios(self):
        return database.admin_obtener_usuarios()
    
    def obtener_usuario_por_id(self, uid):
        # Helper para traer datos actuales al editar
        usuarios = database.admin_obtener_usuarios()
        for u in usuarios:
            if u['id'] == uid: return u
        return None

    def crear_usuario(self, nombre, user, pasw, rol):
        if not nombre or not user or not pasw or not rol: return False, "Todos los campos son obligatorios."
        if len(pasw) < 4: return False, "La contraseña es muy corta (mínimo 4 caracteres)."
        if database.admin_existe_usuario(user): return False, "El nombre de usuario ya está en uso."
        return database.admin_guardar_usuario(nombre, user, pasw, rol)
    
    def actualizar_usuario(self, uid, nombre, user, rol, pasw=""):
        if not nombre or not user: return False, "Nombre y Usuario obligatorios."
        return database.admin_actualizar_usuario(uid, nombre, user, rol, pasw if pasw.strip() else None)

    def actualizar_mi_perfil(self, uid, nombre, user, pasw=""):
        # Versión simplificada para "Mi Perfil" (no cambia rol)
        if not nombre or not user: return False, "Nombre y Usuario obligatorios."
        # Reutilizamos la función de base de datos pasando el rol actual (se busca dentro o se ignora)
        # Nota: Para hacerlo perfecto, database.admin_actualizar_usuario requiere rol. 
        # Asumiremos que en "Mi Perfil" no cambiamos rol.
        # Aquí usaremos una lógica directa para no complicar database.py
        import database as db
        conn = db.crear_conexion()
        try:
            cur = conn.cursor()
            if pasw:
                cur.execute("UPDATE usuarios SET nombre_completo=%s, usuario=%s, contrasena=%s WHERE id=%s", (nombre, user, pasw, uid))
            else:
                cur.execute("UPDATE usuarios SET nombre_completo=%s, usuario=%s WHERE id=%s", (nombre, user, uid))
            conn.commit()
            return True, "Perfil actualizado."
        except Exception as e: return False, str(e)
        finally: conn.close()

    def eliminar_usuario(self, uid_a_borrar, uid_sesion_actual, rol_sesion_actual):
        # 1. ANTI-SUICIDIO
        if uid_a_borrar == uid_sesion_actual:
            return False, "⚠️ ACCIÓN DENEGADA\nNo puedes eliminar tu propia cuenta mientras estás conectado."
        
        # 2. PROTECCIÓN DE JERARQUÍA (Doctora no borra Admin)
        target = self.obtener_usuario_por_id(uid_a_borrar)
        if target and target['rol'] == 'Administrador' and rol_sesion_actual != 'Administrador':
             return False, "⚠️ ACCIÓN DENEGADA\nSolo un Administrador puede eliminar a otro Administrador."

        return database.admin_eliminar_usuario(uid_a_borrar)

    # --- SERVICIOS Y SEGURIDAD ---
    def buscar_servicios(self, query=""):
        return database.buscar_servicios_avanzado(query, "Todas", "Todas")
    
    # NUEVO MÉTODO PARA GUARDAR CON OPCIONES
    def crear_servicio_avanzado(self, cat, sub, nom, lista_opciones):
        """
        lista_opciones: Lista de tuplas [('Por diente', '500'), ('Por zona', '200')]
        """
        if not cat or not nom or not lista_opciones: 
            return False, "Faltan datos obligatorios."
        
        dict_final = {}
        for unidad, precio_str in lista_opciones:
            if not unidad.strip(): continue # Saltar vacíos
            try:
                p = float(precio_str)
                if p < 0: return False, "Precios no pueden ser negativos."
                dict_final[unidad] = p
            except:
                return False, f"El precio para '{unidad}' no es válido."
        
        if not dict_final: return False, "Debes agregar al menos una opción válida."
        
        return database.admin_guardar_servicio_complejo(cat, sub, nom, dict_final)
    
    def validar_supervisor(self, user, pwd):
        if not user or not pwd: return False
        return database.validar_credenciales_supervisor(user, pwd)
    
    def crear_servicio(self, cat, sub, nom, pre):
        if not cat or not nom: return False, "Faltan datos."
        try:
            p = float(pre)
            if p < 0: return False, "Precio negativo."
        except: return False, "Precio inválido."
        return database.admin_guardar_servicio_nuevo(cat, sub, nom, p)

    def actualizar_precio(self, sid, precio):
        try: 
            return database.admin_actualizar_precio_servicio(sid, float(precio))
        except: return False, "Error en precio."
    
    def eliminar_servicio(self, sid):
        return database.admin_eliminar_servicio(sid)

    # --- REPORTES ---
    def obtener_kpis(self): return database.reporte_kpis_generales()
    def datos_grafica_pastel(self): 
        d = database.reporte_top_tratamientos()
        return ([x[0] for x in d], [x[1] for x in d])
    def datos_grafica_linea(self):
        d = database.reporte_ingresos_semestral()
        d.reverse()
        return ([x[0] for x in d], [float(x[1]) for x in d])