# auth_controller.py
from database import crear_conexion
from mysql.connector import Error

def login_user(usuario_input, password_input):
    """
    Verifica las credenciales contra la base de datos MariaDB 'futuras_sonrisas'.
    Usa comparación de texto plano (sin encriptación) y recupera el nombre del rol.
    """
    conexion = crear_conexion()
    if not conexion:
        return None

    cursor = None
    datos_usuario = None # Variable para guardar el resultado final

    try:
        cursor = conexion.cursor()

        # CORRECCIÓN: Usamos los nombres exactos de tu MariaDB:
        # u.usuario, u.contrasena, y hacemos JOIN con roles para obtener el nombre del rol (ej. 'Doctora')
        consulta = """
            SELECT u.id, u.nombre_completo, r.nombre AS rol_nombre, u.contrasena
            FROM usuarios u
            JOIN roles r ON u.rol_id = r.id
            WHERE u.usuario = %s
        """
        
        cursor.execute(consulta, (usuario_input,))
        resultado = cursor.fetchone()

        if resultado:
            # Desempaquetamos los datos que vienen de la BD
            # user_id, nombre, rol, password_en_bd
            uid, nombre, rol, pass_db = resultado

            # VERIFICACIÓN EN TEXTO PLANO (Como solicitaste)
            # Compara exactamente lo que escribió el usuario con lo que hay en la BD
            if password_input == pass_db:
                # Si coincide, preparamos la tupla para devolver
                datos_usuario = (uid, nombre, rol)
            else:
                # Contraseña incorrecta
                print(f"Intento fallido para usuario {usuario_input}: Contraseña incorrecta.")
        else:
            print(f"Intento fallido: Usuario '{usuario_input}' no encontrado.")

    except Error as e:
        print(f"Error crítico en base de datos durante login: {e}")
    
    finally:
        if cursor:
            cursor.close()
        if conexion and conexion.is_connected():
            conexion.close()

    # Retorna la tupla (id, nombre, rol) si fue exitoso, o None si falló
    return datos_usuario
