
from datetime import date

# Clase Libro
class Libro:
    def __init__(self, titulo, autor, anio, codigo_libro, disponible=True):
        self.titulo = titulo
        self.autor = autor
        self.anio = anio
        self.codigo_libro = codigo_libro
        self.disponible = disponible

    def mostrar_info(self):
        estado = "Disponible" if self.disponible else "Prestado"
        print(f"{self.titulo} - {self.autor} ({self.anio}) [{estado}]")

    def prestar(self):
        if self.disponible:
            self.disponible = False
            print(f"El libro '{self.titulo}' ha sido prestado.")
        else:
            print(f"El libro '{self.titulo}' no está disponible.")

    def devolver(self):
        self.disponible = True
        print(f"El libro '{self.titulo}' fue devuelto y ahora está disponible.")


# Clase Usuario
class Usuario:
    def __init__(self, nombre, id, correo):
        self.nombre = nombre
        self.id = id
        self.correo = correo

    def mostrar_info(self):
        print(f"Usuario: {self.nombre} (ID: {self.id}) - Correo: {self.correo}")

    def pedir_libro(self, libro):
        print(f"{self.nombre} está solicitando el libro '{libro.titulo}'.")


# Subclase Estudiante
class Estudiante(Usuario):
    def __init__(self, nombre, id, correo, carrera, semestre):
        super().__init__(nombre, id, correo)
        self.carrera = carrera
        self.semestre = semestre

    def mostrar_info(self):  # Polimorfismo
        print(f"Estudiante: {self.nombre}, {self.carrera} - Semestre {self.semestre}")


# Subclase Profesor
class Profesor(Usuario):
    def __init__(self, nombre, id, correo, departamento, tipo_contrato):
        super().__init__(nombre, id, correo)
        self.departamento = departamento
        self.tipo_contrato = tipo_contrato

    def mostrar_info(self):  # Polimorfismo
        print(f"Profesor: {self.nombre}, {self.departamento} - {self.tipo_contrato}")


# Clase Prestamo
class Prestamo:
    def __init__(self, libro, usuario, fecha_prestamo, fecha_devolucion=None):
        self.libro = libro
        self.usuario = usuario
        self.fecha_prestamo = fecha_prestamo
        self.fecha_devolucion = fecha_devolucion

    def registrar(self):
        if self.libro.disponible:
            self.libro.prestar()
            print(f"Prestamo registrado: {self.usuario.nombre} tomó '{self.libro.titulo}' el {self.fecha_prestamo}.")
        else:
            print(f"No se puede registrar. '{self.libro.titulo}' no está disponible.")

    def devolver(self, fecha):
        self.fecha_devolucion = fecha
        self.libro.devolver()
        print(f"{self.usuario.nombre} devolvió '{self.libro.titulo}' el {fecha}.")


# Simulación
libro1 = Libro("El principito", "Antoine de Saint-Exupéry", 1943, "LB01")
libro2 = Libro("Cien años de soledad", "Gabriel García Márquez", 1967, "LB02")

est1 = Estudiante("Luis García", "E101", "luisg@utd.mx", "Sistemas", 4)
prof1 = Profesor("María Torres", "P202", "mtorres@utd.mx", "Literatura", "Tiempo completo")

prestamo1 = Prestamo(libro1, est1, date(2025, 10, 7))
prestamo2 = Prestamo(libro2, prof1, date(2025, 10, 7))

print("=== Información de Libros ===")
libro1.mostrar_info()
libro2.mostrar_info()

print("\n=== Información de Usuarios ===")
est1.mostrar_info()
prof1.mostrar_info()

print("\n=== Registro de Préstamos ===")
prestamo1.registrar()
prestamo2.registrar()

print("\n=== Devolución de Libros ===")
prestamo1.devolver(date(2025, 10, 14))

print("\n=== Polimorfismo ===")
usuarios = [est1, prof1]
for u in usuarios:
    u.mostrar_info()

