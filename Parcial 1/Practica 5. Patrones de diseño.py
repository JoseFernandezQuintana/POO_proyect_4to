#Practica 5. Patrones de diseño

class Logger:
    _instancia = None #Creamos un atributo de clase donde se guarda la unica instancia

    #__new__ Es el metodo que controla la creacion del objeto antes de init. Sirve para asegurarnos de que solo exista una unica instancia de la clase logger
    def __new__(cls, *args, **kwargs):
        #*arg Argumento posicional que permite resibir multiples parametros
        #**kwargs Permite cualquier cantidad de parametors con nombre

        #Validar si existe o no la instancia aun:
        if cls._instancia is None:
            cls._instancia = super().__new__(cls) #Creamos instancia de logger
            #Agregando un atributo "archivo" que aputa a un archivo fisico "a" significa apped = Todo lo que se escriba se agrega al final del archivo
            cls._instancia.archivo = open("app.log", "a")
        return cls._instancia #Devolvemos siempr la misma instancia 

    def log(self, mensaje):
        #Simulando un registro de logs
        self.archivo.write(mensaje + "\n")
        self.archivo.flush() #Método para guardar en el disco

logger1 = Logger() #Creamos la primera y única instancia
logger2 = Logger() #Devolver la misma instancia, sin crear una nueva

logger1.log("Inicio de sesión en la aplicación")
logger2.log("El usuario se autenticó correctamente")

print(logger1 is logger2) #True

# Actividad de la practica

class Presidente:
    _instancia = None

    def __new__(cls, nombre):
        if cls._instancia is None:
            cls._instancia = super().__new__(cls)
            cls._instancia.nombre = nombre
            cls._instancia.historial = []
        return cls._instancia

    def accion(self, accion):
        evento = f"{self.nombre} {accion}"
        self.historial.append(evento)
        print(evento)

p1 = Presidente("AMLO")
p2 = Presidente("Peña Nieto")
p3 = Presidente("Fox")

p1.accion("firmó decreto")
p2.accion("visitó España")
p3.accion("aprobó un presupuesto")

print("\n---Historial del Presidente:---")
print(p1.historial)

#Validacion de Singleton
print(p1 is p2 is p3) #True o False

#1. ¿Qué pasaria si eliminamos la verificación if cls._instancia is None en el metodo new?
    # Si quitamos el if, se crearían varias instancias y ya no sería Singleton.

#2. ¿Qué significa el "True" en el p1 is p2 is p3 en el contexto del método sigleton?
    # El True significa que p1, p2 y p3 son el mismo objeto en memoria.

#3. ¿Es buena idea usar Singleton para todo lo que sea global?
    # No, solo conviene usar Singleton en recursos únicos (ej. base de datos, logger), no en todo lo global.


