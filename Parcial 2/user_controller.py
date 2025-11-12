
from database import crear_conexion

def ver_usuarios():
    conexion = crear_conexion()
    if not conexion:
        return[]
    
    cursor = conexion.cursor()
    cursor.execute("SELECT id, usuario FROM usuarios")
    resultado = cursor.fetchall()
    conexion.close()
    return resultado

def agregar_usuarios(username, password):
    conexion = crear_conexion()
    if not conexion:
        return False
    
    try:
        cursor = conexion.cursor()
        cursor.execute("INSERT INTO usuarios (usuario, password) VALUES (%s, %s)", (username, password))
        conexion.commit()
        conexion.close()
        return True
    except Exception as e:
        print(f"Error al crear un usuario. Tipo de error {e}")
        return False
    
def actualizar_usuarios(id_usuario, new_usuario, new_password ):
 conexion = crear_conexion()
 if not conexion:
    return False
 try:
    cursor = conexion.cursor()
    cursor.execute("UPDATE usuarios SET usuario = %s, password = %s WHERE id_usuario = %s", (new_password, new_usuario, id_usuario))
    conexion.commit()
    conexion.close()
    return True
 except Exception as e:
  print(f"Error al actualizar usuario. Tipo de error: {e}")
  return False
       
def eliminar_usuarios(id_usuario):
 conexion = crear_conexion()
 if not conexion:
    return False
 try:
    cursor = conexion.cursor()
    cursor.execute("DELETE from usuarios WHERE id = %s", (id_usuario))
    conexion.commit()
    conexion.close()
    return True
 except Exception as e:
  print(f"Error al eliminar usuario. Tipo de error: {e}")
  return False
#TAREA HACER EL DEF DE UPDATE Y DELETE (Actualizar y eliminar.) Y añadirlos al userview
