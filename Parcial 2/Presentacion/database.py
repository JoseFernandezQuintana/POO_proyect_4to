import mysql.connector
from mysql.connector import Error

def crear_conexion():
    try:
        conexion = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="poo_proyecto_parcial2"
        )

        if conexion.is_connected():
            print("Conexión a la BD exitosa")

        return conexion  

    except Error as e:
        print(f"Error al conectar con la BD: {e}")
        return None

if __name__ == "__main__": 
    conexion = crear_conexion()
    if conexion:
        print("Conexión exitosa en SQL")
        conexion.close()
        print("Conexión cerrada.")
    else:
        print("No se pudo establecer la conexión a la base de datos.")