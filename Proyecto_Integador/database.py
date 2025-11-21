import mysql.connector
from mysql.connector import Error
from datetime import timedelta

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

# --- FUNCIONES PARA CALENDARIO (VISUALIZACIÓN) ---

def obtener_citas_filtro(fecha_str, lista_ids_doctoras):
    """Obtiene citas para mostrar en el calendario principal."""
    conexion = crear_conexion()
    citas = []
    if not lista_ids_doctoras:
        return []

    if conexion and conexion.is_connected():
        try:
            cursor = conexion.cursor(dictionary=True)
            format_strings = ','.join(['%s'] * len(lista_ids_doctoras))
            
            query = f"""
                SELECT 
                    c.hora_inicio, c.duracion_minutos, c.motivo_cita, c.estado,
                    CONCAT(cli.nombre, ' ', cli.apellido) AS paciente_nombre_completo,
                    cli.telefono,
                    CONCAT(doc.nombre, ' ', doc.apellido) AS doctora_nombre_completo
                FROM citas c
                INNER JOIN clientes cli ON c.cliente_id = cli.cliente_id
                INNER JOIN usuarios doc ON c.doctora_id = doc.usuario_id
                WHERE c.fecha_cita = %s 
                AND c.doctora_id IN ({format_strings})
                ORDER BY c.hora_inicio ASC
            """
            params = [fecha_str] + lista_ids_doctoras
            cursor.execute(query, params)
            citas = cursor.fetchall()
        except Error as e:
            print(f"Error al leer citas: {e}")
        finally:
            cursor.close()
            conexion.close()
    return citas

def obtener_dias_con_citas_mes(mes, anio):
    """Para marcar días en negrita en el calendario."""
    conexion = crear_conexion()
    dias = set()
    if conexion and conexion.is_connected():
        try:
            cursor = conexion.cursor()
            query = "SELECT DISTINCT DAY(fecha_cita) FROM citas WHERE MONTH(fecha_cita) = %s AND YEAR(fecha_cita) = %s"
            cursor.execute(query, (mes, anio))
            
            # --- ESTA FUE LA LÍNEA QUE FALTÓ ---
            resultados = cursor.fetchall() 
            # -----------------------------------

            for fila in resultados:
                dias.add(fila[0])
        except Error as e:
            print(f"Error días ocupados: {e}")
        finally:
            cursor.close()
            conexion.close()
    return dias

# --- FUNCIONES PARA AGENDAR Y RESUMEN (NUEVO) ---

def verificar_disponibilidad(doctora_id, fecha, hora_inicio):
    """
    Verifica si ya existe una cita activa en esa fecha y hora para esa doctora.
    Retorna True si está LIBRE, False si está OCUPADO.
    """
    conexion = crear_conexion()
    libre = False
    if conexion and conexion.is_connected():
        try:
            cursor = conexion.cursor()
            # Contamos citas que NO estén canceladas en ese horario exacto
            query = """
                SELECT COUNT(*) FROM citas 
                WHERE doctora_id = %s 
                AND fecha_cita = %s 
                AND hora_inicio = %s 
                AND estado != 'Cancelada'
            """
            cursor.execute(query, (doctora_id, fecha, hora_inicio))
            (count,) = cursor.fetchone()
            libre = (count == 0)
        except Error as e:
            print(f"Error verificando disponibilidad: {e}")
        finally:
            cursor.close()
            conexion.close()
    return libre

def registrar_cita(datos):
    """Guarda la nueva cita en la BD."""
    conexion = crear_conexion()
    exito = False
    if conexion and conexion.is_connected():
        try:
            cursor = conexion.cursor()
            query = """
                INSERT INTO citas 
                (cliente_id, doctora_id, fecha_cita, hora_inicio, duracion_minutos, motivo_cita, estado, notas)
                VALUES (%s, %s, %s, %s, %s, %s, 'Pendiente', %s)
            """
            # NOTA: Usamos cliente_id=1 como genérico. Asegúrate de tener un cliente con ID 1.
            params = (
                1, # ID Cliente Genérico
                datos['doctora_id'],
                datos['fecha'],
                datos['hora'],
                30, # Duración por defecto 30 min
                datos['motivo'],
                datos['notas']
            )
            cursor.execute(query, params)
            conexion.commit()
            exito = True
        except Error as e:
            print(f"Error al guardar cita: {e}")
        finally:
            cursor.close()
            conexion.close()
    return exito

def obtener_conteo_citas_global():
    """
    Obtiene el conteo total de citas por estado para la tabla de resumen.
    """
    conexion = crear_conexion()
    resumen = {'Pendiente': 0, 'En curso': 0, 'Completada': 0, 'Cancelada': 0, 'Total': 0}
    
    if conexion and conexion.is_connected():
        try:
            cursor = conexion.cursor()
            query = "SELECT estado, COUNT(*) FROM citas GROUP BY estado"
            cursor.execute(query)
            resultados = cursor.fetchall()
            
            total = 0
            for estado, cantidad in resultados:
                # Capitalizamos para que coincida con las llaves (ej: 'pendiente' -> 'Pendiente')
                key = estado.capitalize()
                if key in resumen:
                    resumen[key] = cantidad
                # Mapeos adicionales por si en BD se llaman diferente
                elif key in ['Finalizada', 'Terminada']:
                    resumen['Completada'] += cantidad
                elif key in ['Programada']:
                    resumen['Pendiente'] += cantidad
                
                total += cantidad
            
            resumen['Total'] = total
            
        except Error as e:
            print(f"Error obteniendo resumen: {e}")
        finally:
            cursor.close()
            conexion.close()
    return resumen

def buscar_citas_bd(query):
    """Busca citas por nombre del paciente o teléfono."""
    conexion = crear_conexion()
    resultados = []
    if conexion and conexion.is_connected():
        try:
            cursor = conexion.cursor(dictionary=True)
            # Buscamos coincidencias en Nombre, Apellido o Teléfono
            # Unimos tablas para mostrar info legible
            sql = """
                SELECT 
                    c.id AS cita_id,
                    c.fecha_cita,
                    c.hora_inicio,
                    CONCAT(cli.nombre, ' ', cli.apellido) AS paciente,
                    cli.telefono
                FROM citas c
                JOIN clientes cli ON c.cliente_id = cli.cliente_id
                WHERE (cli.nombre LIKE %s OR cli.apellido LIKE %s OR cli.telefono LIKE %s)
                AND c.estado != 'Cancelada'
                ORDER BY c.fecha_cita DESC
            """
            param = f"%{query}%"
            cursor.execute(sql, (param, param, param))
            resultados = cursor.fetchall()
        except Error as e:
            print(f"Error en búsqueda: {e}")
        finally:
            cursor.close()
            conexion.close()
    return resultados

def obtener_cita_por_id(cita_id):
    """Obtiene todos los detalles de una cita específica."""
    conexion = crear_conexion()
    cita = None
    if conexion and conexion.is_connected():
        try:
            cursor = conexion.cursor(dictionary=True)
            sql = """
                SELECT 
                    c.id,
                    c.fecha_cita,
                    c.hora_inicio,
                    c.motivo_cita,
                    c.notas,
                    c.doctora_id,
                    cli.nombre,
                    cli.apellido,
                    CONCAT(doc.nombre, ' ', doc.apellido) as nombre_doctora
                FROM citas c
                JOIN clientes cli ON c.cliente_id = cli.cliente_id
                JOIN usuarios doc ON c.doctora_id = doc.usuario_id
                WHERE c.id = %s
            """
            cursor.execute(sql, (cita_id,))
            cita = cursor.fetchone()
        except Error as e:
            print(f"Error obteniendo cita: {e}")
        finally:
            cursor.close()
            conexion.close()
    return cita

def actualizar_cita_bd(cita_id, datos):
    """Actualiza los datos de una cita."""
    conexion = crear_conexion()
    exito = False
    if conexion and conexion.is_connected():
        try:
            cursor = conexion.cursor()
            sql = """
                UPDATE citas 
                SET doctora_id = %s, fecha_cita = %s, hora_inicio = %s, motivo_cita = %s, notas = %s
                WHERE id = %s
            """
            params = (datos['doctora_id'], datos['fecha'], datos['hora'], datos['motivo'], datos['notas'], cita_id)
            cursor.execute(sql, params)
            conexion.commit()
            exito = True
        except Error as e:
            print(f"Error actualizando cita: {e}")
        finally:
            cursor.close()
            conexion.close()
    return exito

def cancelar_cita_bd(cita_id):
    """Cambia el estado de la cita a 'Cancelada'."""
    conexion = crear_conexion()
    exito = False
    if conexion and conexion.is_connected():
        try:
            cursor = conexion.cursor()
            sql = "UPDATE citas SET estado = 'Cancelada' WHERE id = %s"
            cursor.execute(sql, (cita_id,))
            conexion.commit()
            exito = True
        except Error as e:
            print(f"Error cancelando cita: {e}")
        finally:
            cursor.close()
            conexion.close()
    return exito


