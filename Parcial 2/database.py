
import mysql.connector 
from mysql.connector import Error

def crear_conexion():
    #Crear la conexión con la base de datos Mysql
    try:
        conexion = mysql.connector.connect(
            host = 'localhost',
            user = 'root',
            password = '',
            database = 'poo_proyecto_parcial2'
        )
        
        if conexion.is_connected():
            print("Conexión con Mysql establecida")
            return conexion

    except Error as e:
        print (f"Error al conectar a Mtsql: {e}")
        return None



