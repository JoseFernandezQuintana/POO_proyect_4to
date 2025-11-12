from database import crear_conexion
from mysql.connector import Error 

def ver_usuario():
    conexion = crear_conexion()
    if not conexion:
        return [] 
        
    cursor = None
    try:
        cursor = conexion.cursor()
        # Cambiado: 'username' → 'usuario'
        cursor.execute("SELECT id, usuario FROM usuarios")
        resultado = cursor.fetchall()
        return resultado
        
    except Error as e:
        print(f"Error al obtener usuarios: {e}")
        return []
        
    finally:
        if cursor:
            cursor.close()
        if conexion and conexion.is_connected():
            conexion.close()


def crear_usuarios(usuario, password):
    conexion = crear_conexion()
    if not conexion:
        return False
    
    try:
        cursor = conexion.cursor()
        # Cambiado: 'username' → 'usuario'
        cursor.execute("INSERT INTO usuarios (usuario, password) VALUES (%s, %s)", (usuario, password))
        conexion.commit()
        return True
    except Exception as e:
        print(f"Error al crear usuario: {e}")
        return False
    finally:
        if conexion and conexion.is_connected():
            conexion.close()


def actualizar_usuarios(id_usuario, nuevo_usuario, nueva_password):
    conexion = crear_conexion()
    if not conexion:
        return False
    
    try:
        cursor = conexion.cursor()
        cursor.execute(
            "UPDATE usuarios SET usuario = %s, password = %s WHERE id = %s",
            (nuevo_usuario, nueva_password, id_usuario)
        )
        conexion.commit()
        return True
    except Exception as e:
        print(f"Error al actualizar usuario: {e}")
        return False
    finally:
        if conexion and conexion.is_connected():
            conexion.close()


def eliminar_usuario(id_usuario):
    conexion = crear_conexion()
    if not conexion:
        return False
    
    try:
        cursor = conexion.cursor()
        cursor.execute("DELETE FROM usuarios WHERE id = %s", (id_usuario,))
        conexion.commit()
        return True
    except Exception as e:
        print(f"Error al eliminar usuario: {e}")
        return False
    finally:
        if conexion and conexion.is_connected():
            conexion.close()
