import mysql.connector
from mysql.connector import Error
from datetime import datetime, timedelta
import json

# --- CONEXIÓN ---
def crear_conexion():
    try:
        conexion = mysql.connector.connect(
            host="localhost", 
            user="root", 
            password="", 
            database="futuras_sonrisas"
        )
        return conexion
    except Error as e:
        print(f"Error al conectar con la BD: {e}")
        return None

# =========================================================
# 1. AUTENTICACIÓN Y USUARIOS
# =========================================================
def validar_login(usuario, password):
    """Retorna (id, nombre_completo, rol, id_rol)"""
    conexion = crear_conexion()
    if not conexion: return None
    try:
        cursor = conexion.cursor(dictionary=True)
        sql = """SELECT u.id, u.nombre_completo, r.nombre as rol, u.rol_id 
                 FROM usuarios u JOIN roles r ON u.rol_id = r.id
                 WHERE BINARY u.usuario = %s AND BINARY u.contrasena = %s AND u.activo = 1"""
        cursor.execute(sql, (usuario, password))
        return cursor.fetchone()
    except: return None
    finally: conexion.close()

def obtener_lista_doctoras():
    conexion = crear_conexion()
    if not conexion: return []
    try:
        cursor = conexion.cursor(dictionary=True)
        cursor.execute("SELECT id, nombre_completo as nombre, especialidad, foto_perfil FROM usuarios WHERE rol_id = 2 AND activo = 1")
        return cursor.fetchall()
    except: return []
    finally: conexion.close()

# =========================================================
# 2. AGENDA Y CITAS
# =========================================================
def verificar_disponibilidad_sp(doctora_id, fecha, hora_inicio, hora_final, ignorar_cita_id=0):
    conexion = crear_conexion()
    if not conexion: return False 
    try:
        cursor = conexion.cursor()
        args = (doctora_id, fecha, hora_inicio, hora_final, ignorar_cita_id)
        cursor.callproc('sp_check_disponibilidad', args)
        
        for result in cursor.stored_results():
            fila = result.fetchone()
            if fila and fila[0] > 0:
                return False # Ocupado
        return True # Libre
    except Error as e:
        print(f"Error SP Disponibilidad: {e}")
        return False
    finally: conexion.close()

def guardar_cita_transaccional_bd(datos_cliente, datos_cita, servicios_detalle, usuario_responsable_id=None):
    conexion = crear_conexion()
    if not conexion: return False, "Sin conexión BD."
    try:
        conexion.start_transaction()
        cursor = conexion.cursor()
        
        # A. Cliente
        cliente_id = datos_cliente.get('cliente_id_existente')
        notif_val = 1 if datos_cliente['notificar'] else 0
        
        # Calcular bandera de tratamiento previo (Si hay descripción, asumimos True, o lógica específica)
        desc_tx = datos_cliente.get('previo_desc', '')
        tp = 1 if ("Externa" in desc_tx or "Ambas" in desc_tx or len(desc_tx) > 20) else 0 
        
        if cliente_id:
            cursor.execute("""
                UPDATE clientes 
                SET telefono=%s, email=%s, notificacion=%s, rango_edad=%s, 
                    tratamiento_previo=%s, descripcion_tratamiento=%s 
                WHERE id=%s
            """, (datos_cliente['telefono'], datos_cliente['email'], notif_val, datos_cliente['edad'], tp, desc_tx, cliente_id))
        else:
            sql_cli = "INSERT INTO clientes (nombre_completo, rango_edad, genero, telefono, email, notificacion, tratamiento_previo, descripcion_tratamiento) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
            cursor.execute(sql_cli, (datos_cliente['nombre'], datos_cliente['edad'], datos_cliente['genero'], datos_cliente['telefono'], datos_cliente['email'], notif_val, tp, desc_tx))
            cliente_id = cursor.lastrowid

        # B. Cita
        sql_cita = "INSERT INTO citas (cliente_id, doctora_id, fecha_cita, hora_inicio, hora_final, tipo, estado, descripcion) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
        cursor.execute(sql_cita, (cliente_id, datos_cita['doctora_id'], datos_cita['fecha'], datos_cita['hora_inicio'], datos_cita['hora_final'], datos_cita['tipo'], datos_cita['estado'], datos_cita['descripcion']))
        cita_id = cursor.lastrowid
        
        # C. Detalles
        if datos_cita['tipo'] == 'Tratamiento' and servicios_detalle:
            sql_det = "INSERT INTO cita_detalle (cita_id, servicio_id, cantidad, detalle_unidad, precio_unitario, subtotal) VALUES (%s, %s, %s, %s, %s, %s)"
            for s in servicios_detalle:
                cursor.execute(sql_det, (cita_id, s['id'], s['cantidad'], s['unidad'], s['precio_unitario'], s['precio_total']))

        # D. Auditoría
        if usuario_responsable_id:
            cursor.execute("INSERT INTO bitacora_acciones (usuario_id, accion, tabla, detalle_nuevo) VALUES (%s, 'NUEVA_CITA', 'citas', %s)", 
                           (usuario_responsable_id, f"Cita ID: {cita_id} para Cliente: {cliente_id}"))

        conexion.commit()
        return True, "Cita agendada correctamente."
    except Error as e:
        conexion.rollback()
        return False, f"Error BD: {e}"
    finally: conexion.close()

# =========================================================
# 3. PAGOS Y DEUDAS 
# =========================================================
def buscar_citas_con_deuda(query=""):
    conexion = crear_conexion()
    if not conexion: return []
    try:
        cursor = conexion.cursor(dictionary=True)
        
        # SQL base
        sql = """SELECT c.id, c.fecha_cita, c.hora_inicio, cl.nombre_completo, cl.telefono,
                   c.monto_total, c.monto_pagado, c.estado_pago, c.descripcion as tratamiento,
                   (c.monto_total - c.monto_pagado) as saldo_pendiente
            FROM citas c JOIN clientes cl ON c.cliente_id = cl.id
            WHERE c.estado != 'Cancelada'
              AND (c.monto_total > c.monto_pagado) """
        
        params = []
        if query:
            # Filtro dinámico
            sql += " AND (cl.nombre_completo LIKE %s OR cl.telefono LIKE %s)"
            term = f"%{query}%"
            params.extend([term, term])
            
        sql += " ORDER BY c.fecha_cita DESC LIMIT 30"
        
        cursor.execute(sql, tuple(params))
        return cursor.fetchall()
    except: return []
    finally: conexion.close()

def registrar_pago_bd(cita_id, monto, metodo, nota, usuario_id):
    conexion = crear_conexion()
    if not conexion: return False, "Sin conexión"
    try:
        cursor = conexion.cursor()
        cursor.execute("INSERT INTO pagos (cita_id, monto, metodo, nota, registrado_por) VALUES (%s, %s, %s, %s, %s)", 
                       (cita_id, monto, metodo, nota, usuario_id))
        
        cursor.execute("INSERT INTO bitacora_acciones (usuario_id, accion, tabla, detalle_nuevo) VALUES (%s, 'COBRO', 'pagos', %s)",
                       (usuario_id, f"Cobro de ${monto} a Cita {cita_id}"))
                       
        conexion.commit()
        return True, "Pago registrado."
    except Error as e: return False, str(e)
    finally: conexion.close()

def obtener_detalle_deuda(cita_id):
    conexion = crear_conexion()
    if not conexion: return []
    try:
        cursor = conexion.cursor(dictionary=True)
        sql = "SELECT s.nombre, cd.detalle_unidad, cd.cantidad, cd.subtotal FROM cita_detalle cd JOIN servicios s ON cd.servicio_id = s.id WHERE cd.cita_id = %s"
        cursor.execute(sql, (cita_id,))
        return cursor.fetchall()
    except: return []
    finally: conexion.close()

# =========================================================
# 4. UTILS Y FILTROS
# =========================================================
def buscar_clientes_rapido(query):
    conexion = crear_conexion()
    if not conexion: return []
    try:
        cursor = conexion.cursor(dictionary=True)
        # Agregamos % % para búsqueda parcial (LIKE)
        t = f"%{query}%"
        # Busca por Nombre O Teléfono
        sql = """SELECT id, nombre_completo, telefono, email, rango_edad, genero, 
                        tratamiento_previo, descripcion_tratamiento
                 FROM clientes 
                 WHERE nombre_completo LIKE %s OR telefono LIKE %s 
                 LIMIT 5"""
        cursor.execute(sql, (t, t))
        return cursor.fetchall()
    except Exception as e: 
        print(f"Error buscar cliente: {e}")
        return []
    finally: conexion.close()

def obtener_citas_rango_doctoras(fecha_inicio, fecha_fin, ids_doctoras):
    if not ids_doctoras: return []
    
    conn = crear_conexion()
    if not conn: return []
    
    try:
        cursor = conn.cursor(dictionary=True)
        format_strings = ','.join(['%s'] * len(ids_doctoras))
        query = f"SELECT `fecha_cita`, `hora_inicio` FROM `citas` WHERE `fecha_cita` BETWEEN %s AND %s AND `doctora_id` IN ({format_strings}) AND `estado` != 'Cancelada'"
        
        params = [fecha_inicio, fecha_fin] + ids_doctoras
        cursor.execute(query, tuple(params))
        return cursor.fetchall()
    except Exception as e:
        print(f"Error rango docs: {e}")
        return []
    finally:
        if conn: conn.close()

def obtener_citas_rango_paciente(fecha_inicio, fecha_fin, paciente_id):
    conn = crear_conexion()
    if not conn: return []
    
    try:
        cursor = conn.cursor(dictionary=True)
        query = "SELECT `fecha_cita` FROM `citas` WHERE `fecha_cita` BETWEEN %s AND %s AND `cliente_id` = %s AND `estado` != 'Cancelada'"
        cursor.execute(query, (fecha_inicio, fecha_fin, paciente_id))
        return cursor.fetchall()
    except Exception as e:
        print(f"Error rango paciente: {e}")
        return []
    finally:
        if conn: conn.close()

def buscar_servicios_avanzado(nombre, categoria="Todas", subcategoria="Todas"):
    conexion = crear_conexion()
    if not conexion: return []
    try:
        cursor = conexion.cursor(dictionary=True)
        sql = "SELECT * FROM servicios WHERE activo = 1"
        params = []
        if nombre:
            sql += " AND (nombre LIKE %s OR categoria LIKE %s OR subcategoria LIKE %s)"
            term = f"%{nombre}%"
            params.extend([term, term, term])
        if categoria and categoria != "Todas":
            sql += " AND categoria = %s"
            params.append(categoria)
        if subcategoria and subcategoria != "Todas":
            sql += " AND subcategoria = %s"
            params.append(subcategoria)
        sql += " LIMIT 50"
        cursor.execute(sql, tuple(params))
        return cursor.fetchall()
    except: return []
    finally: conexion.close()

def obtener_columnas_unicas(columna):
    conexion = crear_conexion()
    if not conexion: return []
    try:
        cursor = conexion.cursor()
        if columna in ['categoria', 'subcategoria']:
            cursor.execute(f"SELECT DISTINCT {columna} FROM servicios ORDER BY {columna}")
            return [row[0] for row in cursor.fetchall() if row[0]]
    except: pass
    finally: conexion.close()
    return []

def obtener_subcategorias_filtro(categoria):
    conexion = crear_conexion()
    if not conexion: return []
    try:
        cursor = conexion.cursor()
        cursor.execute("SELECT DISTINCT subcategoria FROM servicios WHERE categoria = %s ORDER BY subcategoria", (categoria,))
        return [row[0] for row in cursor.fetchall() if row[0]]
    except: return []
    finally: conexion.close()

# --- APOYO VISUAL ---
def obtener_resumen_dia_bd(fecha_sql):
    conexion = crear_conexion()
    res = {'Pendiente':0, 'Confirmada':0, 'Completada':0, 'Cancelada':0, 'En curso':0}
    if not conexion: return res
    try:
        cursor = conexion.cursor()
        cursor.execute("SELECT estado, COUNT(*) FROM citas WHERE fecha_cita = %s GROUP BY estado", (fecha_sql,))
        for est, cant in cursor.fetchall(): res[est] = cant
    except: pass
    finally: conexion.close()
    return res

def obtener_citas_dia_doctora(doc_id, fecha_sql):
    conexion = crear_conexion()
    if not conexion: return []
    try:
        cursor = conexion.cursor()
        cursor.execute("SELECT hora_inicio, hora_final FROM citas WHERE doctora_id=%s AND fecha_cita=%s AND estado!='Cancelada'", (doc_id, fecha_sql))
        return cursor.fetchall()
    except: return []
    finally: conexion.close()

def obtener_citas_filtro(fecha_str, ids_doctoras):
    conexion = crear_conexion()
    if not conexion or not ids_doctoras: return []
    try:
        cursor = conexion.cursor(dictionary=True)
        fmt = ','.join(['%s'] * len(ids_doctoras))
        sql = f"""SELECT c.*, cl.nombre_completo as paciente_nombre_completo, cl.telefono, cl.email, u.nombre_completo as doctora_nombre_completo, TIMESTAMPDIFF(MINUTE, c.hora_inicio, c.hora_final) as duracion_minutos
                  FROM citas c JOIN clientes cl ON c.cliente_id=cl.id JOIN usuarios u ON c.doctora_id=u.id
                  WHERE c.fecha_cita=%s AND c.doctora_id IN ({fmt}) ORDER BY c.hora_inicio ASC"""
        cursor.execute(sql, [fecha_str] + ids_doctoras)
        return cursor.fetchall()
    except: return []
    finally: conexion.close()

def obtener_dias_con_citas_mes(mes, anio):
    conexion = crear_conexion()
    if not conexion: return []
    try:
        cursor = conexion.cursor()
        cursor.execute("SELECT DISTINCT DAY(fecha_cita) FROM citas WHERE MONTH(fecha_cita)=%s AND YEAR(fecha_cita)=%s AND estado!='Cancelada'", (mes, anio))
        return [r[0] for r in cursor.fetchall()]
    except: return []
    finally: conexion.close()
    
def obtener_dias_paciente_mes(mes, anio, cliente_id):
    conexion = crear_conexion()
    if not conexion: return []
    try:
        cursor = conexion.cursor()
        cursor.execute("SELECT DISTINCT DAY(fecha_cita) FROM citas WHERE MONTH(fecha_cita)=%s AND YEAR(fecha_cita)=%s AND cliente_id=%s AND estado!='Cancelada'", (mes, anio, cliente_id))
        return [r[0] for r in cursor.fetchall()]
    except: return []
    finally: conexion.close()

def obtener_detalle_completo_cita(cita_id):
    conexion = crear_conexion()
    if not conexion: return None
    try:
        cursor = conexion.cursor(dictionary=True)
        cursor.execute("SELECT c.*, cl.id as cliente_id_real, cl.nombre_completo, cl.telefono, cl.email, cl.rango_edad, cl.genero, cl.notificacion, cl.tratamiento_previo, cl.descripcion_tratamiento as desc_previo, u.nombre_completo as doctora_nombre FROM citas c JOIN clientes cl ON c.cliente_id = cl.id JOIN usuarios u ON c.doctora_id = u.id WHERE c.id = %s", (cita_id,))
        datos = cursor.fetchone()
        servicios = []
        if datos:
            cursor.execute("SELECT s.id, s.nombre, cd.precio_unitario, cd.detalle_unidad as unidad, cd.cantidad, cd.subtotal as precio_total FROM cita_detalle cd JOIN servicios s ON cd.servicio_id = s.id WHERE cd.cita_id = %s", (cita_id,))
            servicios = cursor.fetchall()
        return {'cita': datos, 'servicios': servicios}
    except: return None
    finally: conexion.close()

def actualizar_cita_completa_bd(cita_id, datos_cli, datos_cita, usuario_id=None):
    conexion = crear_conexion()
    if not conexion: return False
    try:
        cursor = conexion.cursor()
        
        cursor.execute("""
            UPDATE clientes 
            SET nombre_completo=%s, telefono=%s, email=%s, 
                tratamiento_previo=%s, descripcion_tratamiento=%s 
            WHERE id=%s
        """, (datos_cli['nombre'], datos_cli['telefono'], datos_cli['email'], datos_cli['tp'], datos_cli['desc'], datos_cli['id']))
        
        cursor.execute("UPDATE citas SET doctora_id=%s, fecha_cita=%s, hora_inicio=%s, hora_final=%s, descripcion=%s, estado=%s WHERE id=%s", (datos_cita['doctora_id'], datos_cita['fecha'], datos_cita['hora_inicio'], datos_cita['hora_final'], datos_cita['descripcion'], datos_cita['estado'], cita_id))
        
        if usuario_id:
             cursor.execute("INSERT INTO bitacora_acciones (usuario_id, accion, tabla, detalle_nuevo) VALUES (%s, 'MODIFICA_CITA', 'citas', %s)", (usuario_id, f"Modificó cita {cita_id}"))

        conexion.commit()
        return True
    except Exception as e: 
        print(f"Error update: {e}")
        return False
    finally: conexion.close()

def cambiar_estado_cita_cancelada_bd(cita_id, usuario_id=None):
    conexion = crear_conexion()
    if not conexion: return False
    try:
        cursor = conexion.cursor()
        cursor.execute("UPDATE citas SET estado='Cancelada' WHERE id=%s", (cita_id,))
        if usuario_id:
             cursor.execute("INSERT INTO bitacora_acciones (usuario_id, accion, tabla, detalle_nuevo) VALUES (%s, 'CANCELAR', 'citas', %s)", (usuario_id, f"Canceló cita {cita_id}"))
        conexion.commit()
        return True
    except: return False
    finally: conexion.close()

def sincronizar_estados_bd():
    conexion = crear_conexion()
    if not conexion: return
    try:
        cursor = conexion.cursor()
        sql = """UPDATE citas SET estado = CASE 
                WHEN fecha_cita < CURDATE() AND estado != 'Completada' THEN 'Completada'
                WHEN fecha_cita = CURDATE() AND CURTIME() > hora_final THEN 'Completada'
                WHEN fecha_cita = CURDATE() AND CURTIME() >= hora_inicio AND CURTIME() <= hora_final THEN 'En curso'
                ELSE estado END 
                WHERE estado NOT IN ('Cancelada', 'Completada')"""
        cursor.execute(sql)
        conexion.commit()
    except: pass
    finally: conexion.close()

def ejecutar_sp_fetch_one(sp_name, args):
    """Ejecuta un Procedimiento Almacenado y devuelve el primer resultado."""
    conexion = crear_conexion()
    if not conexion: return None
    try:
        cursor = conexion.cursor()
        cursor.callproc(sp_name, args)
        
        # Iterar sobre los resultados almacenados
        for result in cursor.stored_results():
            return result.fetchone() # Retorna la primera fila encontrada
            
        return None
    except Exception as e:
        print(f"Error SP {sp_name}: {e}")
        return None
    finally: conexion.close()

def ejecutar_sp(sp_name, args):
    """Ejecuta un Procedimiento Almacenado sin devolver datos (para updates)."""
    conexion = crear_conexion()
    if not conexion: return False
    try:
        cursor = conexion.cursor()
        cursor.callproc(sp_name, args)
        conexion.commit()
        return True
    except Exception as e:
        print(f"Error SP {sp_name}: {e}")
        return False
    finally: conexion.close()

# =========================================================
# 5. ADMINISTRACIÓN Y REPORTES
# =========================================================

# --- GESTIÓN DE USUARIOS Y SERVICIOS ---
def admin_obtener_usuarios():
    conn = crear_conexion()
    if not conn: return []
    try:
        cur = conn.cursor(dictionary=True)
        cur.execute("SELECT u.id, u.nombre_completo, u.usuario, u.rol_id, r.nombre as rol, u.especialidad, u.activo FROM usuarios u JOIN roles r ON u.rol_id = r.id WHERE u.activo = 1 ORDER BY u.nombre_completo")
        return cur.fetchall()
    except: return []
    finally: conn.close()

def admin_existe_usuario(usuario):
    conn = crear_conexion()
    try:
        cur = conn.cursor()
        cur.execute("SELECT id FROM usuarios WHERE usuario = %s AND activo = 1", (usuario,))
        return cur.fetchone() is not None
    finally: conn.close()

def admin_guardar_usuario(nombre, usuario, contra, rol_nombre, especialidad="General"):
    conn = crear_conexion()
    if not conn: return False, "Sin conexión"
    try:
        cur = conn.cursor()
        cur.execute("SELECT id FROM roles WHERE nombre = %s", (rol_nombre,))
        res = cur.fetchone()
        if not res: return False, "Rol inválido"
        cur.execute("INSERT INTO usuarios (nombre_completo, usuario, contrasena, rol_id, especialidad, activo) VALUES (%s, %s, %s, %s, %s, 1)", (nombre, usuario, contra, res[0], especialidad))
        conn.commit()
        return True, "Creado."
    except Exception as e: return False, str(e)
    finally: conn.close()

def admin_actualizar_usuario(uid, nombre, usuario, rol_nombre, nueva_contra=None, especialidad="General"):
    conn = crear_conexion()
    try:
        cur = conn.cursor()
        cur.execute("SELECT id FROM roles WHERE nombre = %s", (rol_nombre,))
        rid = cur.fetchone()[0]
        if nueva_contra:
            cur.execute("UPDATE usuarios SET nombre_completo=%s, usuario=%s, rol_id=%s, contrasena=%s, especialidad=%s WHERE id=%s", (nombre, usuario, rid, nueva_contra, especialidad, uid))
        else:
            cur.execute("UPDATE usuarios SET nombre_completo=%s, usuario=%s, rol_id=%s, especialidad=%s WHERE id=%s", (nombre, usuario, rid, especialidad, uid))
        conn.commit()
        return True, "Actualizado."
    except Exception as e: return False, str(e)
    finally: conn.close()

def admin_eliminar_usuario(user_id):
    conn = crear_conexion()
    try:
        cur = conn.cursor()
        cur.execute("UPDATE usuarios SET activo = 0 WHERE id = %s", (user_id,))
        conn.commit(); return True, "Eliminado."
    except Exception as e: return False, str(e)
    finally: conn.close()

def admin_guardar_servicio_complejo(cat, sub, nom, opciones_dict):
    conexion = crear_conexion()
    if not conexion: return False, "Sin conexión"
    try:
        cursor = conexion.cursor()
        cursor.execute("SELECT id FROM servicios WHERE nombre = %s AND activo = 1", (nom,))
        if cursor.fetchone(): return False, "Ya existe este servicio."
        
        unidades = list(opciones_dict.keys())
        tipo_unidad_str = " o ".join(unidades)
        precios = list(opciones_dict.values())
        precio_ref = min(precios) if precios else 0
        json_str = json.dumps(opciones_dict)

        sql = """INSERT INTO servicios (categoria, subcategoria, nombre, tipo_unidad, precio_base, opciones_json, activo) 
                 VALUES (%s, %s, %s, %s, %s, %s, 1)"""
        cursor.execute(sql, (cat, sub, nom, tipo_unidad_str, precio_ref, json_str))
        conexion.commit()
        return True, "Servicio creado con múltiples opciones."
    except Exception as e: return False, str(e)
    finally: conexion.close()

def admin_actualizar_precio_servicio(sid, precio):
    conn = crear_conexion()
    try:
        cur = conn.cursor()
        cur.execute("UPDATE servicios SET precio_base = %s WHERE id = %s", (precio, sid))
        conn.commit(); return True, "Actualizado."
    except Exception as e: return False, str(e)
    finally: conn.close()

def admin_actualizar_precio_variante_json(sid, nombre_variante, nuevo_precio):
    conn = crear_conexion()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT opciones_json FROM servicios WHERE id=%s", (sid,))
        res = cursor.fetchone()
        if not res or not res[0]: return False, "No tiene variantes"
        
        datos = json.loads(res[0])
        if nombre_variante in datos:
            datos[nombre_variante] = float(nuevo_precio)
            nuevo_json = json.dumps(datos)
            cursor.execute("UPDATE servicios SET opciones_json=%s WHERE id=%s", (nuevo_json, sid))
            conn.commit()
            return True, "Precio actualizado"
        return False, "Variante no encontrada"
    except Exception as e: return False, str(e)
    finally: conn.close()

def admin_eliminar_servicio(sid):
    conn = crear_conexion()
    try:
        cur = conn.cursor()
        cur.execute("UPDATE servicios SET activo = 0 WHERE id = %s", (sid,))
        conn.commit(); return True, "Eliminado."
    except Exception as e: return False, str(e)
    finally: conn.close()

def validar_credenciales_supervisor(usuario, password):
    conn = crear_conexion()
    if not conn: return False
    try:
        cur = conn.cursor()
        sql = "SELECT id FROM usuarios WHERE usuario=%s AND contrasena=%s AND activo=1 AND rol_id IN (1, 2)"
        cur.execute(sql, (usuario, password))
        return cur.fetchone() is not None
    except: return False
    finally: conn.close()

# --- KPIS Y REPORTES (USANDO VISTAS SQL) ---

def reporte_kpis_generales():
    """Consulta directa a tablas para KPIs de tiempo real"""
    conn = crear_conexion()
    try:
        cur = conn.cursor()
        cur.execute("SELECT IFNULL(SUM(monto),0) FROM pagos WHERE MONTH(fecha_pago) = MONTH(CURRENT_DATE()) AND YEAR(fecha_pago) = YEAR(CURRENT_DATE())")
        mes = cur.fetchone()[0]
        cur.execute("SELECT IFNULL(SUM(monto),0) FROM pagos")
        total = cur.fetchone()[0]
        cur.execute("SELECT COUNT(*) FROM clientes WHERE MONTH(creado_en) = MONTH(CURRENT_DATE()) AND YEAR(creado_en) = YEAR(CURRENT_DATE())")
        nuevos = cur.fetchone()[0]
        return mes, total, nuevos
    except: return 0, 0, 0
    finally: conn.close()

def reporte_top_tratamientos():
    """Consulta la Vista SQL 'reporte_tratamientos_top'"""
    conn = crear_conexion()
    try:
        cur = conn.cursor()
        cur.execute("SELECT nombre, veces_realizado FROM reporte_tratamientos_top")
        return cur.fetchall()
    except: return []
    finally: conn.close()

def reporte_ingresos_semestral():
    """Consulta la Vista SQL 'reporte_ingresos_mensuales'"""
    conn = crear_conexion()
    try:
        cur = conn.cursor()
        cur.execute("SELECT mes, total_ingreso FROM reporte_ingresos_mensuales")
        return cur.fetchall()
    except: return []
    finally: conn.close()

def reporte_demografia_edad():
    """Consulta la Vista SQL 'reporte_demografia_edad'"""
    conn = crear_conexion()
    try:
        cur = conn.cursor()
        cur.execute("SELECT rango_edad, total FROM reporte_demografia_edad")
        return cur.fetchall()
    except: return []
    finally: conn.close()

def reporte_demografia_genero():
    """Consulta la Vista SQL 'reporte_demografia_genero'"""
    conn = crear_conexion()
    try:
        cur = conn.cursor()
        cur.execute("SELECT genero, total FROM reporte_demografia_genero")
        return cur.fetchall()
    except: return []
    finally: conn.close()

def reporte_pagos_metodo():
    """Consulta la Vista SQL 'reporte_metodos_pago'"""
    conn = crear_conexion()
    try:
        cur = conn.cursor()
        cur.execute("SELECT metodo, total FROM reporte_metodos_pago")
        return cur.fetchall()
    except: return []
    finally: conn.close()

# --- FUNCIONES DE SOPORTE PARA ADMIN CONTROLLER ---

def reporte_kpis_comparativos():
    conn = crear_conexion()
    res = (0, 0, 0, 0)
    if not conn: return res
    try:
        cur = conn.cursor()
        sql_ingresos = """
            SELECT 
                SUM(CASE WHEN MONTH(fecha_pago) = MONTH(CURRENT_DATE()) AND YEAR(fecha_pago) = YEAR(CURRENT_DATE()) THEN monto ELSE 0 END) as actual,
                SUM(CASE WHEN MONTH(fecha_pago) = MONTH(DATE_SUB(CURRENT_DATE(), INTERVAL 1 MONTH)) AND YEAR(fecha_pago) = YEAR(DATE_SUB(CURRENT_DATE(), INTERVAL 1 MONTH)) THEN monto ELSE 0 END) as anterior
            FROM pagos
        """
        cur.execute(sql_ingresos)
        ingresos = cur.fetchone()
        
        sql_pacientes = """
            SELECT 
                COUNT(CASE WHEN MONTH(creado_en) = MONTH(CURRENT_DATE()) AND YEAR(creado_en) = YEAR(CURRENT_DATE()) THEN 1 END),
                COUNT(CASE WHEN MONTH(creado_en) = MONTH(DATE_SUB(CURRENT_DATE(), INTERVAL 1 MONTH)) AND YEAR(creado_en) = YEAR(DATE_SUB(CURRENT_DATE(), INTERVAL 1 MONTH)) THEN 1 END)
            FROM clientes
        """
        cur.execute(sql_pacientes)
        pacs = cur.fetchone()
        res = (ingresos[0] or 0, ingresos[1] or 0, pacs[0] or 0, pacs[1] or 0)
    except: pass
    finally: conn.close()
    return res

def reporte_info_pacientes_completa():
    conn = crear_conexion()
    try:
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM clientes")
        total = cur.fetchone()[0]
        cur.execute("SELECT rango_edad FROM clientes GROUP BY rango_edad ORDER BY COUNT(*) DESC LIMIT 1")
        moda = cur.fetchone()
        edad_top = moda[0] if moda else "N/A"
        return total, edad_top
    except: return 0, "N/A"
    finally: conn.close()

def reporte_estado_citas(anio=None):
    conn = crear_conexion()
    try:
        cur = conn.cursor()
        sql = "SELECT estado, COUNT(*) FROM citas WHERE estado != 'Cancelada' GROUP BY estado"
        cur.execute(sql)
        return cur.fetchall()
    except: return []
    finally: conn.close()

def reporte_citas_tipo():
    conn = crear_conexion()
    try:
        cur = conn.cursor()
        sql = "SELECT tipo, COUNT(*) FROM citas WHERE estado != 'Cancelada' GROUP BY tipo"
        cur.execute(sql)
        return cur.fetchall()
    except: return []
    finally: conn.close()

def reporte_top_doctores():
    conn = crear_conexion()
    try:
        cur = conn.cursor()
        sql = """SELECT u.nombre_completo, COUNT(c.id) as total 
                 FROM citas c JOIN usuarios u ON c.doctora_id = u.id 
                 WHERE c.estado = 'Completada' 
                 GROUP BY u.id 
                 ORDER BY total DESC"""
        cur.execute(sql)
        return cur.fetchall()
    except: return []
    finally: conn.close()

def reporte_comparativo_semanal():
    conn = crear_conexion()
    try:
        cur = conn.cursor()
        sql = """
            SELECT WEEK(fecha_cita, 1) as semana, COUNT(*) 
            FROM citas 
            WHERE fecha_cita >= DATE_SUB(NOW(), INTERVAL 8 WEEK) 
            GROUP BY semana ORDER BY semana ASC
        """
        cur.execute(sql)
        return cur.fetchall()
    except: return []
    finally: conn.close()
