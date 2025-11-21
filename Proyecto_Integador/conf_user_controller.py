# conf_user_controller.py
# Controlador de usuarios: usa crear_conexion() desde database.py + CRUD + búsqueda + bcrypt

import bcrypt
from mysql.connector import Error
from database import crear_conexion  # usa tu archivo database.py (crear_conexion)

# Roles permitidos (asegúrate coincidan con tu ENUM en la BD)
VALID_ROLES = ("Administrador", "Doctora", "Recepcionista")

def hash_password(plain_password: str) -> str:
    hashed = bcrypt.hashpw(plain_password.encode("utf-8"), bcrypt.gensalt())
    return hashed.decode("utf-8")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    try:
        return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))
    except Exception:
        return False

# ------------------ CRUD usando crear_conexion() -------------------
def get_all_users():
    conn = crear_conexion()
    if not conn:
        return []
    try:
        cur = conn.cursor(dictionary=True)
        cur.execute("SELECT usuario_id, nombre, apellido, usuario, rol FROM usuarios ORDER BY usuario_id")
        rows = cur.fetchall()
        return rows
    except Error as e:
        print("Error get_all_users:", e)
        return []
    finally:
        try: cur.close()
        except: pass
        try: conn.close()
        except: pass

def get_user_by_id(user_id: int):
    conn = crear_conexion()
    if not conn:
        return None
    try:
        cur = conn.cursor(dictionary=True)
        cur.execute("SELECT usuario_id, nombre, apellido, usuario, password, rol FROM usuarios WHERE usuario_id = %s", (user_id,))
        return cur.fetchone()
    except Error as e:
        print("Error get_user_by_id:", e)
        return None
    finally:
        try: cur.close()
        except: pass
        try: conn.close()
        except: pass

def find_users_by_term(term: str):
    conn = crear_conexion()
    if not conn:
        return []
    try:
        cur = conn.cursor(dictionary=True)
        like = f"%{term}%"
        cur.execute("""
            SELECT usuario_id, nombre, apellido, usuario, rol
            FROM usuarios
            WHERE nombre LIKE %s OR apellido LIKE %s OR usuario LIKE %s
            ORDER BY usuario_id
        """, (like, like, like))
        return cur.fetchall()
    except Error as e:
        print("Error find_users_by_term:", e)
        return []
    finally:
        try: cur.close()
        except: pass
        try: conn.close()
        except: pass

def add_user(nombre: str, apellido: str, usuario: str, plain_password: str, rol: str = "empleado"):
    if rol not in VALID_ROLES:
        return False, f"Rol inválido. Roles permitidos: {VALID_ROLES}"
    if not all([nombre, apellido, usuario, plain_password]):
        return False, "Todos los campos son requeridos."

    conn = crear_conexion()
    if not conn:
        return False, "No se pudo conectar a la base de datos."

    try:
        cur = conn.cursor()
        hashed = hash_password(plain_password)
        cur.execute("""
            INSERT INTO usuarios (nombre, apellido, usuario, password, rol)
            VALUES (%s, %s, %s, %s, %s)
        """, (nombre, apellido, usuario, hashed, rol))
        conn.commit()
        return True, "Usuario creado correctamente."
    except Error as e:
        # si hay constraint (usuario duplicado) MySQL devolverá error
        print("Error add_user:", e)
        return False, f"Error al crear usuario: {e}"
    finally:
        try: cur.close()
        except: pass
        try: conn.close()
        except: pass

def update_user(user_id: int, nombre: str, apellido: str, usuario: str, plain_password: str = None, rol: str = None):
    if rol is not None and rol not in VALID_ROLES:
        return False, f"Rol inválido. Roles permitidos: {VALID_ROLES}"
    if not all([user_id, nombre, apellido, usuario]):
        return False, "ID, nombre, apellido y usuario son requeridos."

    conn = crear_conexion()
    if not conn:
        return False, "No se pudo conectar a la base de datos."

    try:
        cur = conn.cursor()
        if plain_password:  # actualizar contraseña
            hashed = hash_password(plain_password)
            if rol is not None:
                cur.execute("""
                    UPDATE usuarios
                    SET nombre=%s, apellido=%s, usuario=%s, password=%s, rol=%s
                    WHERE usuario_id=%s
                """, (nombre, apellido, usuario, hashed, rol, user_id))
            else:
                cur.execute("""
                    UPDATE usuarios
                    SET nombre=%s, apellido=%s, usuario=%s, password=%s
                    WHERE usuario_id=%s
                """, (nombre, apellido, usuario, hashed, user_id))
        else:
            if rol is not None:
                cur.execute("""
                    UPDATE usuarios
                    SET nombre=%s, apellido=%s, usuario=%s, rol=%s
                    WHERE usuario_id=%s
                """, (nombre, apellido, usuario, rol, user_id))
            else:
                cur.execute("""
                    UPDATE usuarios
                    SET nombre=%s, apellido=%s, usuario=%s
                    WHERE usuario_id=%s
                """, (nombre, apellido, usuario, user_id))
        conn.commit()
        return True, "Usuario actualizado correctamente."
    except Error as e:
        print("Error update_user:", e)
        return False, f"Error al actualizar: {e}"
    finally:
        try: cur.close()
        except: pass
        try: conn.close()
        except: pass

def delete_user(user_id: int):
    conn = crear_conexion()
    if not conn:
        return False, "No se pudo conectar a la base de datos."
    try:
        cur = conn.cursor()
        cur.execute("DELETE FROM usuarios WHERE usuario_id = %s", (user_id,))
        conn.commit()
        return True, "Usuario eliminado."
    except Error as e:
        print("Error delete_user:", e)
        return False, f"Error al eliminar: {e}"
    finally:
        try: cur.close()
        except: pass
        try: conn.close()
        except: pass
