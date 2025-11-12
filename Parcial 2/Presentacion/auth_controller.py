from database import crear_conexion
from mysql.connector import Error

def validar_credenciales(usuario, password):
    conexion = crear_conexion() 
    if not conexion:
        return False
        
    cursor = None
    try:
        cursor = conexion.cursor()
        consulta = "SELECT * FROM usuarios WHERE usuario = %s AND password = %s"
        cursor.execute(consulta, (usuario, password))
        resultado = cursor.fetchone()

        if cursor:
            cursor.close()
        if conexion and conexion.is_connected():
            conexion.close()
        
        return bool(resultado)

    except Error as e:
        print(f"Error en la validación de credenciales: {e}")
        return False
        
    finally:
        pass 