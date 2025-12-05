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

# --- LOGIN ---
def validar_login(usuario, password):
    conexion = crear_conexion()
    if not conexion: return None
    try:
        cursor = conexion.cursor(dictionary=True)
        sql = """SELECT u.id, u.nombre_completo, r.nombre as rol 
                 FROM usuarios u JOIN roles r ON u.rol_id = r.id
                 WHERE u.usuario = %s AND u.contrasena = %s AND u.activo = 1"""
        cursor.execute(sql, (usuario, password))
        return cursor.fetchone()
    except: return None
    finally: conexion.close()

# --- SEGURIDAD EXTRA ---
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

# --- DOCTORAS ---
def obtener_lista_doctoras():
    conexion = crear_conexion()
    if not conexion: return []
    try:
        cursor = conexion.cursor(dictionary=True)
        cursor.execute("SELECT id, nombre_completo as nombre, especialidad FROM usuarios WHERE rol_id = 2 AND activo = 1")
        return cursor.fetchall()
    except: return []
    finally: conexion.close()

# --- AGENDAR CITA (Transacciones) ---
def guardar_cita_transaccional_bd(datos_cliente, datos_cita, servicios_detalle):
    conexion = crear_conexion()
    if not conexion: return False, "Sin conexión BD."
    try:
        conexion.start_transaction()
        cursor = conexion.cursor()
        
        # 1. Cliente
        cliente_id = datos_cliente.get('id')
        notif_val = 1 if datos_cliente['notificar'] else 0
        
        if cliente_id:
            cursor.execute("UPDATE clientes SET telefono=%s, email=%s, notificacion=%s WHERE id=%s", 
                          (datos_cliente['telefono'], datos_cliente['email'], notif_val, cliente_id))
        else:
            tp = 1 if datos_cliente.get('previo_desc') else 0
            sql_cli = "INSERT INTO clientes (nombre_completo, rango_edad, genero, telefono, email, notificacion, tratamiento_previo, descripcion_tratamiento) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
            cursor.execute(sql_cli, (datos_cliente['nombre'], datos_cliente['edad'], datos_cliente['genero'], datos_cliente['telefono'], datos_cliente['email'], notif_val, tp, datos_cliente.get('previo_desc','')))
            cliente_id = cursor.lastrowid

        # 2. Cita
        sql_cita = "INSERT INTO citas (cliente_id, doctora_id, fecha_cita, hora_inicio, hora_final, tipo, estado, descripcion) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
        cursor.execute(sql_cita, (cliente_id, datos_cita['doctora_id'], datos_cita['fecha'], datos_cita['hora_inicio'], datos_cita['hora_final'], datos_cita['tipo'], datos_cita['estado'], datos_cita['descripcion']))
        cita_id = cursor.lastrowid
        
        # 3. Detalles (Genera Deuda)
        if datos_cita['tipo'] == 'Tratamiento' and servicios_detalle:
            sql_det = "INSERT INTO cita_detalle (cita_id, servicio_id, cantidad, detalle_unidad, precio_unitario, subtotal) VALUES (%s, %s, %s, %s, %s, %s)"
            for s in servicios_detalle:
                cursor.execute(sql_det, (cita_id, s['id'], s['cantidad'], s['unidad'], s['precio_unitario'], s['precio_total']))

        conexion.commit()
        return True, "Cita agendada."
    except Error as e:
        conexion.rollback()
        return False, f"Error BD: {e}"
    finally: conexion.close()

# --- PAGOS ---
def buscar_citas_con_deuda(query):
    conexion = crear_conexion()
    if not conexion: return []
    try:
        cursor = conexion.cursor(dictionary=True)
        term = f"%{query}%"
        sql = """SELECT c.id, c.fecha_cita, c.hora_inicio, cl.nombre_completo, cl.telefono,
                   c.monto_total, c.monto_pagado, c.estado_pago, (c.monto_total - c.monto_pagado) as saldo_pendiente
            FROM citas c JOIN clientes cl ON c.cliente_id = cl.id
            WHERE (cl.nombre_completo LIKE %s OR cl.telefono LIKE %s) AND c.estado != 'Cancelada'
              AND (c.estado_pago = 'Pendiente' OR c.estado_pago = 'Parcial') AND c.monto_total > 0
            ORDER BY c.fecha_cita DESC LIMIT 20"""
        cursor.execute(sql, (term, term))
        return cursor.fetchall()
    except: return []
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

def registrar_pago_bd(cita_id, monto, metodo, nota, usuario_id=None):
    conexion = crear_conexion()
    if not conexion: return False, "Sin conexión"
    try:
        cursor = conexion.cursor()
        cursor.execute("INSERT INTO pagos (cita_id, monto, metodo, nota, registrado_por) VALUES (%s, %s, %s, %s, %s)", (cita_id, monto, metodo, nota, usuario_id))
        conexion.commit()
        return True, "Pago registrado."
    except Error as e: return False, str(e)
    finally: conexion.close()

# --- BUSCADORES Y UTILS ---
def buscar_clientes_rapido(query):
    conexion = crear_conexion()
    if not conexion: return []
    try:
        cursor = conexion.cursor(dictionary=True)
        t = f"%{query}%"
        cursor.execute("SELECT id, nombre_completo, telefono, email, rango_edad, genero FROM clientes WHERE nombre_completo LIKE %s OR telefono LIKE %s LIMIT 10", (t, t))
        return cursor.fetchall()
    except: return []
    finally: conexion.close()

# [MODIFICADO] BUSCADOR MEJORADO (Nombre OR Categoría OR Subcategoría)
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

def admin_guardar_servicio_complejo(cat, sub, nom, opciones_dict):
    """
    opciones_dict: Diccionario ej {'Por diente': 500, 'Boca completa': 2000}
    Se guarda el precio menor como 'precio_base' para referencia y el resto en JSON.
    """
    conexion = crear_conexion()
    if not conexion: return False, "Sin conexión"
    try:
        cursor = conexion.cursor()
        
        # Validar duplicado
        cursor.execute("SELECT id FROM servicios WHERE nombre = %s AND activo = 1", (nom,))
        if cursor.fetchone(): return False, "Ya existe este servicio."

        # Procesar datos
        # 1. Construir string "Por x o y"
        unidades = list(opciones_dict.keys())
        tipo_unidad_str = " o ".join(unidades)
        
        # 2. Precio base (Tomamos el primero o el menor, solo para referencia)
        precios = list(opciones_dict.values())
        precio_ref = min(precios) if precios else 0
        
        # 3. JSON
        json_str = json.dumps(opciones_dict)

        sql = """INSERT INTO servicios (categoria, subcategoria, nombre, tipo_unidad, precio_base, opciones_json, activo) 
                 VALUES (%s, %s, %s, %s, %s, %s, 1)"""
        
        cursor.execute(sql, (cat, sub, nom, tipo_unidad_str, precio_ref, json_str))
        conexion.commit()
        return True, "Servicio creado con múltiples opciones."
    except Exception as e: return False, str(e)
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

def sincronizar_estados_bd():
    conexion = crear_conexion()
    if not conexion: return
    try:
        cursor = conexion.cursor()
        sql = """UPDATE citas SET estado = CASE 
                WHEN fecha_cita < CURDATE() THEN 'Completada'
                WHEN fecha_cita = CURDATE() AND CURTIME() > hora_final THEN 'Completada'
                WHEN fecha_cita = CURDATE() AND CURTIME() >= hora_inicio AND CURTIME() <= hora_final THEN 'En curso'
                WHEN fecha_cita = CURDATE() AND CURTIME() < hora_inicio THEN 'Pendiente'
                ELSE estado END WHERE estado != 'Cancelada'"""
        cursor.execute(sql)
        conexion.commit()
    except: pass
    finally: conexion.close()

# --- FUNCIONES DE CALENDARIO/MODIFICAR (Soporte) ---
def obtener_citas_filtro(fecha_str, ids_doctoras):
    conexion = crear_conexion()
    if not conexion or not ids_doctoras: return []
    try:
        cursor = conexion.cursor(dictionary=True)
        fmt = ','.join(['%s'] * len(ids_doctoras))
        sql = f"""SELECT c.*, cl.nombre_completo as paciente_nombre_completo, cl.telefono, u.nombre_completo as doctora_nombre_completo, TIMESTAMPDIFF(MINUTE, c.hora_inicio, c.hora_final) as duracion_minutos
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

def buscar_citas_por_paciente_bd(query):
    conexion = crear_conexion()
    if not conexion: return []
    try:
        cursor = conexion.cursor(dictionary=True)
        term = f"%{query}%"
        sql = """SELECT c.*, cl.nombre_completo, cl.telefono, cl.email, cl.rango_edad, cl.genero
            FROM citas c JOIN clientes cl ON c.cliente_id = cl.id 
            WHERE cl.nombre_completo LIKE %s OR cl.telefono LIKE %s ORDER BY c.fecha_cita DESC LIMIT 20"""
        cursor.execute(sql, (term, term))
        return cursor.fetchall()
    except: return []
    finally: conexion.close()

def obtener_detalle_completo_cita(cita_id):
    conexion = crear_conexion()
    if not conexion: return None
    try:
        cursor = conexion.cursor(dictionary=True)
        cursor.execute("SELECT c.*, cl.id as cliente_id_real, cl.nombre_completo, cl.telefono, cl.email, cl.rango_edad, cl.genero, cl.notificacion, cl.tratamiento_previo, cl.descripcion_tratamiento as desc_previo FROM citas c JOIN clientes cl ON c.cliente_id = cl.id WHERE c.id = %s", (cita_id,))
        datos = cursor.fetchone()
        servicios = []
        if datos:
            cursor.execute("SELECT s.id, s.nombre, cd.precio_unitario, cd.detalle_unidad as unidad, cd.cantidad, cd.subtotal as precio_total FROM cita_detalle cd JOIN servicios s ON cd.servicio_id = s.id WHERE cd.cita_id = %s", (cita_id,))
            servicios = cursor.fetchall()
        return {'cita': datos, 'servicios': servicios}
    except: return None
    finally: conexion.close()

def actualizar_cita_completa_bd(cita_id, datos_cli, datos_cita):
    conexion = crear_conexion()
    if not conexion: return False
    try:
        cursor = conexion.cursor()
        cursor.execute("UPDATE clientes SET nombre_completo=%s, telefono=%s, email=%s WHERE id=%s", (datos_cli['nombre'], datos_cli['telefono'], datos_cli['email'], datos_cli['id']))
        cursor.execute("UPDATE citas SET doctora_id=%s, fecha_cita=%s, hora_inicio=%s, hora_final=%s, descripcion=%s, estado=%s WHERE id=%s", (datos_cita['doctora_id'], datos_cita['fecha'], datos_cita['hora_inicio'], datos_cita['hora_final'], datos_cita['descripcion'], datos_cita['estado'], cita_id))
        conexion.commit()
        return True
    except: return False
    finally: conexion.close()

def borrar_cita_definitiva_bd(cita_id):
    conexion = crear_conexion()
    if not conexion: return False
    try:
        cursor = conexion.cursor()
        cursor.execute("DELETE FROM citas WHERE id=%s", (cita_id,))
        conexion.commit()
        return True
    except: return False
    finally: conexion.close()

def obtener_citas_en_curso_bd():
    conexion = crear_conexion()
    if not conexion: return []
    try:
        cursor = conexion.cursor(dictionary=True)
        cursor.execute("SELECT c.*, cl.nombre_completo, cl.telefono FROM citas c JOIN clientes cl ON c.cliente_id = cl.id WHERE c.fecha_cita = CURDATE() AND CURTIME() BETWEEN c.hora_inicio AND c.hora_final AND c.estado != 'Cancelada'")
        return cursor.fetchall()
    except: return []
    finally: conexion.close()

# =========================================================
# SECCIÓN ADMINISTRACIÓN (CRUDs y REPORTES) -- ¡LO QUE FALTABA!
# =========================================================

# 1. USUARIOS (CRUD)
def admin_obtener_usuarios():
    conn = crear_conexion()
    if not conn: return []
    try:
        cur = conn.cursor(dictionary=True)
        cur.execute("SELECT u.id, u.nombre_completo, u.usuario, u.rol_id, r.nombre as rol, u.activo FROM usuarios u JOIN roles r ON u.rol_id = r.id WHERE u.activo = 1 ORDER BY u.nombre_completo")
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

def admin_guardar_usuario(nombre, usuario, contra, rol_nombre):
    conn = crear_conexion()
    if not conn: return False, "Sin conexión"
    try:
        cur = conn.cursor()
        cur.execute("SELECT id FROM roles WHERE nombre = %s", (rol_nombre,))
        res = cur.fetchone()
        if not res: return False, "Rol inválido"
        cur.execute("INSERT INTO usuarios (nombre_completo, usuario, contrasena, rol_id, especialidad, activo) VALUES (%s, %s, %s, %s, 'General', 1)", (nombre, usuario, contra, res[0]))
        conn.commit()
        return True, "Creado."
    except Exception as e: return False, str(e)
    finally: conn.close()

def admin_actualizar_usuario(uid, nombre, usuario, rol_nombre, nueva_contra=None):
    conn = crear_conexion()
    try:
        cur = conn.cursor()
        cur.execute("SELECT id FROM roles WHERE nombre = %s", (rol_nombre,))
        rid = cur.fetchone()[0]
        if nueva_contra:
            cur.execute("UPDATE usuarios SET nombre_completo=%s, usuario=%s, rol_id=%s, contrasena=%s WHERE id=%s", (nombre, usuario, rid, nueva_contra, uid))
        else:
            cur.execute("UPDATE usuarios SET nombre_completo=%s, usuario=%s, rol_id=%s WHERE id=%s", (nombre, usuario, rid, uid))
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

# 2. SERVICIOS (ADMIN)
def admin_guardar_servicio_nuevo(cat, sub, nom, precio):
    conn = crear_conexion()
    try:
        cur = conn.cursor()
        cur.execute("SELECT id FROM servicios WHERE nombre = %s AND activo = 1", (nom,))
        if cur.fetchone(): return False, "Ya existe."
        cur.execute("INSERT INTO servicios (categoria, subcategoria, nombre, tipo_unidad, precio_base, activo) VALUES (%s, %s, %s, 'por caso', %s, 1)", (cat, sub, nom, precio))
        conn.commit(); return True, "Creado."
    except Exception as e: return False, str(e)
    finally: conn.close()

def admin_actualizar_precio_servicio(sid, precio):
    conn = crear_conexion()
    try:
        cur = conn.cursor()
        cur.execute("UPDATE servicios SET precio_base = %s WHERE id = %s", (precio, sid))
        conn.commit(); return True, "Actualizado."
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

# 3. REPORTES
def reporte_kpis_generales():
    conn = crear_conexion()
    try:
        cur = conn.cursor()
        cur.execute("SELECT IFNULL(SUM(monto),0) FROM pagos WHERE MONTH(fecha_pago) = MONTH(CURRENT_DATE())")
        mes = cur.fetchone()[0]
        cur.execute("SELECT IFNULL(SUM(monto),0) FROM pagos")
        total = cur.fetchone()[0]
        cur.execute("SELECT COUNT(*) FROM clientes WHERE MONTH(creado_en) = MONTH(CURRENT_DATE())")
        nuevos = cur.fetchone()[0]
        return mes, total, nuevos
    except: return 0, 0, 0
    finally: conn.close()

def reporte_top_tratamientos():
    conn = crear_conexion()
    try:
        cur = conn.cursor()
        sql = "SELECT s.nombre, COUNT(cd.id) as cant FROM cita_detalle cd JOIN servicios s ON cd.servicio_id = s.id GROUP BY s.id ORDER BY cant DESC LIMIT 5"
        cur.execute(sql)
        return cur.fetchall()
    except: return []
    finally: conn.close()

def reporte_ingresos_semestral():
    conn = crear_conexion()
    try:
        cur = conn.cursor()
        sql = "SELECT DATE_FORMAT(fecha_pago, '%Y-%m') as mes, SUM(monto) FROM pagos GROUP BY mes ORDER BY mes DESC LIMIT 6"
        cur.execute(sql)
        return cur.fetchall()
    except: return []
    finally: conn.close()