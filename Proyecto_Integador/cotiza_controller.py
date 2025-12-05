# conf_service_controller.py
# Controlador de Servicios: CRUD y Búsqueda avanzada con múltiples filtros
from mysql.connector import Error
from database import crear_conexion

# Listas de validación para la UI y el backend
# Usamos los mismos roles que en usuarios
VALID_ROLES = ["Administrador", "Doctora", "Recepcionista"]

# Categorías extraídas de tu lista
VALID_CATEGORIES = [
    "ODONTOLOGÍA GENERAL",
    "ORTODONCIA",
    "ENDODONCIA",
    "CIRUGÍA ORAL Y MAXILOFACIAL",
    "REHABILITACIÓN Y PRÓTESIS",
    "PERIODONCIA",
    "ODONTOPEDIATRÍA",
    "OTROS SERVICIOS"
]

# Tipos de unidad comunes extraídos de tu lista (para el combobox del formulario)
VALID_UNIT_TYPES = [
    "por diente",
    "por boca completa",
    "por zona",
    "por caso",
    "por arcada",
    "por cuadrante",
    "por persona/caso",
    "por zona o caso",
    "por diente o por zona"
]

# ------------------ CRUD y Búsqueda Avanzada -------------------

def get_all_services():
    """Obtiene todos los servicios ordenados por categoría y nombre."""
    conn = crear_conexion()
    if not conn: return []
    try:
        cur = conn.cursor(dictionary=True)
        # Seleccionamos todos los campos necesarios para la tabla y la edición
        query = """
            SELECT servicio_id, categoria, nombre, tipo_unidad, rol_responsable, precio_base 
            FROM servicios 
            ORDER BY categoria ASC, nombre ASC
        """
        cur.execute(query)
        return cur.fetchall()
    except Error as e:
        print("Error get_all_services:", e)
        return []
    finally:
        if 'cur' in locals() and cur: cur.close()
        if 'conn' in locals() and conn: conn.close()

def get_service_by_id(service_id: int):
    """Obtiene un servicio específico para llenar el formulario de edición."""
    conn = crear_conexion()
    if not conn: return None
    try:
        cur = conn.cursor(dictionary=True)
        cur.execute("SELECT * FROM servicios WHERE servicio_id = %s", (service_id,))
        return cur.fetchone()
    except Error as e:
        print("Error get_service_by_id:", e)
        return None
    finally:
        if 'cur' in locals() and cur: cur.close()
        if 'conn' in locals() and conn: conn.close()

def find_services_advanced(term: str = "", category_filter: str = "", role_filter: str = ""):
    """
    Búsqueda avanzada dinámica. Construye la consulta SQL basándose en qué filtros
    están activos (texto, categoría y/o rol).
    """
    conn = crear_conexion()
    if not conn: return []
    try:
        cur = conn.cursor(dictionary=True)
        
        # Consulta base: 'WHERE 1=1' es un truco para facilitar añadir 'AND' dinámicamente
        query = "SELECT servicio_id, categoria, nombre, tipo_unidad, rol_responsable, precio_base FROM servicios WHERE 1=1"
        params = []

        # 1. Filtro de texto (Busca en nombre O categoría)
        if term:
            query += " AND (nombre LIKE %s OR categoria LIKE %s)"
            like_term = f"%{term}%"
            params.extend([like_term, like_term])
        
        # 2. Filtro estricto por categoría (si no es la opción por defecto)
        if category_filter and category_filter != "Todas las Categorías":
            query += " AND categoria = %s"
            params.append(category_filter)

        # 3. Filtro estricto por rol (si no es la opción por defecto)
        if role_filter and role_filter != "Todos los Roles":
            query += " AND rol_responsable = %s"
            params.append(role_filter)
            
        # Siempre ordenar los resultados
        query += " ORDER BY categoria ASC, nombre ASC"

        # Ejecutar la consulta construida
        cur.execute(query, tuple(params))
        return cur.fetchall()
    except Error as e:
        print("Error find_services_advanced:", e)
        return []
    finally:
        if 'cur' in locals() and cur: cur.close()
        if 'conn' in locals() and conn: conn.close()

def add_service(nombre: str, categoria: str, unidad: str, rol: str, precio: float):
    """Añade un nuevo servicio al catálogo."""
    if not all([nombre, categoria, unidad, rol]):
         return False, "Nombre, categoría, unidad y rol son obligatorios."

    conn = crear_conexion()
    if not conn: return False, "No se pudo conectar a la BD."

    try:
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO servicios (nombre, categoria, tipo_unidad, rol_responsable, precio_base)
            VALUES (%s, %s, %s, %s, %s)
        """, (nombre, categoria, unidad, rol, precio))
        conn.commit()
        return True, "Servicio creado correctamente."
    except Error as e:
        return False, f"Error al crear servicio: {e}"
    finally:
        if 'cur' in locals() and cur: cur.close()
        if 'conn' in locals() and conn: conn.close()

def update_service(service_id: int, nombre: str, categoria: str, unidad: str, rol: str, precio: float):
    """Actualiza un servicio existente, incluyendo su precio base."""
    if not all([service_id, nombre, categoria, unidad, rol]):
         return False, "Faltan datos obligatorios para actualizar."

    conn = crear_conexion()
    if not conn: return False, "No se pudo conectar a la BD."

    try:
        cur = conn.cursor()
        cur.execute("""
            UPDATE servicios
            SET nombre=%s, categoria=%s, tipo_unidad=%s, rol_responsable=%s, precio_base=%s
            WHERE servicio_id=%s
        """, (nombre, categoria, unidad, rol, precio, service_id))
        conn.commit()
        return True, "Servicio actualizado correctamente."
    except Error as e:
        return False, f"Error al actualizar: {e}"
    finally:
        if 'cur' in locals() and cur: cur.close()
        if 'conn' in locals() and conn: conn.close()

def delete_service(service_id: int):
    """Elimina un servicio del catálogo."""
    conn = crear_conexion()
    if not conn: return False, "No se pudo conectar a la BD."
    try:
        cur = conn.cursor()
        cur.execute("DELETE FROM servicios WHERE servicio_id = %s", (service_id,))
        conn.commit()
        return True, "Servicio eliminado."
    except Error as e:
        # Importante: Si este servicio ya se usó en una cotización futura,
        # la base de datos podría impedir la eliminación (foreign key constraint).
        return False, f"Error al eliminar (¿El servicio está en uso?): {e}"
    finally:
        if 'cur' in locals() and cur: cur.close()
        if 'conn' in locals() and conn: conn.close()