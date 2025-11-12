import os
os.system("cls")

#Practica 1. Clases, obejtos y atributos

#Una clase es una plantilla o un molde que define como será un objeto
class Persona:
    def __init__(self, nombre, edad): #Constructor de una clase
        self.nombre = nombre
        self.edad = edad

    def estudiar(self):
        print(f"Hola mi nombre es {self.nombre} y tengo {self.edad} años.")
    
    def cumplir_anios(self):
        print(f"Este año voy a cumplir {self.edad + 1} años.")
    #pass # Clase vacia temporalmente

#Un objeto es una instancia creada a partir de una clase
# Crear objeto que pertenece a una clase
estudiante1 = Persona("José", 19)
estudiante2 = Persona("Emilio", 20)

# Paso 1. Agregar un método cumplir_anios() que aumente en 1 la edad
# Asignar métodos a esos objetos (Acciones)
estudiante1.estudiar()
estudiante1.cumplir_anios()
estudiante2.estudiar()
estudiante2.cumplir_anios()

#Instancia: 
# Cada objeto creado de una clase es una instancia
# Podemos tener varias instancias que coexistan con sus propios datos
# Objeto - instancia de la clase
# Cada vez que se crea un objeto con Clase() se obtiene una instancia dependiente
# Cada instancia tiene sus propios datos aunque vengan de la misma clase

#Abstracción 
# Representar solo lo importante del mundo real, ocultando detalles inecesarios

class automovil:
    def __init__(self, marca):
        self.marca = marca

    def arrancar(self):
        print(f"{self.marca} arrancó")

# Crear un obejto auto y asignar una marca
obj_carro = automovil("Rolls-Royce")
obj_carro.arrancar()

#Abstracción: Nos centramos solo en lo imporatante (accion) que es arrancar el automovil, ocultando detalles como motor, transmision, tipo_combustible
# Enfoque solo en la acción del objeto
# Objetivo es hacer el codigo mas limpio y facil de usar

#Practica 1.2
#1. Crear una clase mascota 
#2. Agregar minimo 4 atributos
#3. Definir al menos 4 metodos
#4. Crear 2 intancias de la clase
#5. Llamar los métodos y aplicar abstracción, (Agregar un atributo innecesario)

import os
os.system("cls")

class Mascota:
    def __init__(self, nombre, edad, cumpl, collar):
        self.nombre = nombre
        self.edad = edad
        self.cumpl = cumpl
        self.collar = collar
    
    def presentacion(self):
        print(f"La mascota se llama: {self.nombre}.")
    
    def edad_act(self):
        print(f"La mascota tiene la edad actual de: {self.edad} años.")
    
    def cumpleanos(self):
        self.cumpl = self.edad + 1
        print(f"Este año va a cumplir: {self.cumpl} años.")
    
    def usa_collar(self):
        self.collar = "Si"

animal = Mascota("Pelusa", 2, 0, "No")
animal.presentacion()
animal.edad_act()
animal.cumpleanos()
animal.usa_collar()
