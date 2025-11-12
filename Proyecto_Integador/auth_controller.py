from database import crear_conexion
from mysql.connector import Error

# Valida usuario y contraseña contra la base de datos
def validar_credenciales(usuario, password):
    conexion = crear_conexion()
    if not conexion:
        return False

    cursor = None
    try:
        cursor = conexion.cursor()
        # Consulta SQL para verificar las credenciales
        consulta = "SELECT * FROM usuarios WHERE usuario = %s AND password = %s"
        cursor.execute(consulta, (usuario, password))
        resultado = cursor.fetchone()
        # Devuelve True si se encuentra el usuario, False si no
        return bool(resultado)
    except Error as e:
        print(f"Error en la validación de credenciales: {e}")
        return False
    finally:
        # Cierra el cursor y la conexión de forma segura
        if cursor:
            cursor.close()
        if conexion and conexion.is_connected():
            conexion.close()
            