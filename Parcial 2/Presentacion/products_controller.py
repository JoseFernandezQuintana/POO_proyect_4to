from database import crear_conexion
from mysql.connector import Error 
def ver_productos():
    """Obtiene todos los productos de la base de datos."""
    conexion = crear_conexion()
    if not conexion:
        return []
    
    cursor = None
    try:
        cursor = conexion.cursor()
        cursor.execute("""
            SELECT id_producto, nombre_producto, stock, precio, status, marca, proveedor, descripcion 
            FROM productos
        """)
        resultado = cursor.fetchall()
        return resultado
        
    except Error as e:
        print(f"Error al obtener productos: {e}")
        return []
        
    finally:
        if cursor:
            cursor.close()
        if conexion and conexion.is_connected():
            conexion.close()


def crear_producto(nombre, stock, precio, status, marca=None, proveedor=None, descripcion=None):
    """Crea un nuevo producto en la base de datos."""
    conexion = crear_conexion()
    if not conexion:
        return False
    
    try:
        cursor = conexion.cursor()
        cursor.execute("""
            INSERT INTO productos (nombre_producto, stock, precio, status, marca, proveedor, descripcion)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (nombre, stock, precio, status, marca, proveedor, descripcion))
        conexion.commit()
        return True
    except Exception as e:
        print(f"Error al crear producto: {e}")
        return False
    finally:
        if conexion and conexion.is_connected():
            conexion.close()


def actualizar_producto(id_producto, nombre, stock, precio, status, marca=None, proveedor=None, descripcion=None):
    """Actualiza un producto existente por su ID."""
    conexion = crear_conexion()
    if not conexion:
        return False
    
    try:
        cursor = conexion.cursor()
        cursor.execute("""
            UPDATE productos 
            SET nombre_producto = %s, stock = %s, precio = %s, status = %s, marca = %s, proveedor = %s, descripcion = %s
            WHERE id_producto = %s
        """, (nombre, stock, precio, status, marca, proveedor, descripcion, id_producto))
        conexion.commit()
        return True
    except Exception as e:
        print(f"Error al actualizar producto: {e}")
        return False
    finally:
        if conexion and conexion.is_connected():
            conexion.close()


def eliminar_producto(id_producto):
    """Elimina un producto por su ID."""
    conexion = crear_conexion()
    if not conexion:
        return False
    
    try:
        cursor = conexion.cursor()
        cursor.execute("DELETE FROM productos WHERE id_producto = %s", (id_producto,))
        conexion.commit()
        return True
    except Exception as e:
        print(f"Error al eliminar producto: {e}")
        return False
    finally:
        if conexion and conexion.is_connected():
            conexion.close()