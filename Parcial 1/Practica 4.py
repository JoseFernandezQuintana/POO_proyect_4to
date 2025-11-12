# Practica 4
# Clase Ticket
class Ticket:
    def __init__(self, id, tipo, prioridad, estado="pendiente"):
        self.id = id
        self.tipo = tipo
        self.prioridad = prioridad
        self.estado = estado

    def __str__(self):
        return f"Ticket ID: {self.id}, Tipo: {self.tipo}, Prioridad: {self.prioridad}, Estado: {self.estado}"


# Clase Empleado
class Empleado:
    def __init__(self, nombre):
        self.nombre = nombre

    def trabajar_ticket(self, ticket):
        print(f"El empleado {self.nombre} está trabajando en el ticket {ticket.id}")


# Clase Desarrollador
class Desarrollador(Empleado):
    def resolver_ticket(self, ticket):
        if ticket.tipo == "software":
            ticket.estado = "resuelto"
            print(f"El ticket {ticket.id} fue resuelto por {self.nombre}")
        else:
            print(f"{self.nombre} no puede resolver este ticket (tipo: {ticket.tipo})")


# Clase Project Manager
class ProjectManager(Empleado):
    def asignar_ticket(self, ticket, empleado):
        print(f"{self.nombre} asignó el ticket {ticket.id} al empleado {empleado.nombre}")
        empleado.trabajar_ticket(ticket)


# Parte adicional: Menú
tickets = []
contador_id = 1
pm1 = ProjectManager("Flor")
developer1 = Desarrollador("Owen")
tester1 = Empleado("Valentín")

import os
os.system("cls")

while True:
    os.system("cls")
    print("\n--- MENÚ ---")
    print("1. Crear ticket")
    print("2. Ver tickets")
    print("3. Asignar ticket")
    print("4. Salir")

    opcion = input("Elige una opción: ")

    if opcion == "1":
        id_ticket = len(tickets) + 1
        tipo = input("Tipo de ticket (software/prueba/otro): ")
        prioridad = input("Prioridad (alta/media/baja): ")
        nuevo_ticket = Ticket(contador_id, tipo, prioridad)
        tickets.append(nuevo_ticket)
        print(f"\nSe creó el ticket {nuevo_ticket}.")
        contador_id += 1

        input("Oprime enter para regresar al menú.")

    elif opcion == "2":
        if not tickets:
            print("No hay tickets registrados.")
        else:
            for i in tickets:
                print(f"\n{i}")
        input("Oprime enter para regresar al menú.")

    elif opcion == "3":
        if not tickets:
            print("No hay tickets disponibles para asignar.")
        else:
            for i in tickets:
                print(f"\n{i}")
            id_ticket = int(input("ID del ticket a asignar: "))
            empleado = input("Asignar a (dev/tester): ")

            ticket_encontrado = next((i for i in tickets if i.id == id_ticket), None)

        if ticket_encontrado:
            if empleado == "dev":
                pm1.asignar_ticket(ticket_encontrado, developer1)
                developer1.resolver_ticket(ticket_encontrado)
            elif empleado == "tester":
                pm1.asignar_ticket(ticket_encontrado, tester1)
                ticket_encontrado.estado = "resuelto"   # <<< cambio aquí >>>
                print(f"El ticket {ticket_encontrado.id} fue resuelto por {tester1.nombre}")
            else:
                print("Empleado no válido.")
        else:
            print("No se encontró el ticket.")
        input("Oprime enter para regresar al menú.")

    elif opcion == "4":
        print("Saliendo del programa...")
        break

    else:
        print("Opción no válida, intenta de nuevo.")
        input("Oprime enter para regresar al menú.")

