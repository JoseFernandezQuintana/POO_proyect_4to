import database

def login_user(usuario, password):
    """
    Verifica credenciales y retorna la tupla de sesión:
    (user_id, nombre_completo, rol, id_rol)
    """
    # Llama a la función optimizada en database.py
    datos = database.validar_login(usuario, password)
    
    if datos:
        # Retornamos los datos necesarios para la sesión global
        return (datos['id'], datos['nombre_completo'], datos['rol'], datos['rol_id'])
    
    return None
