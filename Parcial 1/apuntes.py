#¿Que es un paradigma en programacion?
    #Define los programas en términos de "clases de objetos", objetos que son entidades que combinan estado (proposito o datos), comportamiento (procedimientos o métodos) e identidad (prpiedad del objeto que lo difierencia del resto)

#Paradigma de programación orientada a objetos
    #Tecnología ya probada, se usa para construir y entregar sistemas complejos. Esta demanda crece vertiginosamente. El valor fundamental del desarrollo orientado a objetos es que libera a la mente humana para que pueda centrar sus energías creativas sobre las partes realmente difíciles de un sistema complejo.

#Paradigma
    #Intentar unificar y simplicar como resolver un frupo de problemas. En programación, principios y métodos que sirven para resolver los problemas para los desarrolladores de software al construir sistemas gendes y complejos

#Tipos de paradigmas
    #Estructurado:  Estructuras de control de flujo (if).
    #Funcional: Funciones y sus correspondientes, código con funciones pequeñas.
    #Orientado a objetos:   Trabajan con base en unidades llamadas objetos, siguen una serie de principios.

#Ventajas
    #Reutilización y extención del código
    #Sistemas más complejos
    #Relacionar el sistema al mundo real
    #Facilidad en progamación, visual
    #Costrucción de prototipos
    #Agiliza el dearrollo
    #Facilita el trabajo en equipo
    #Facil mantenimiento

class robot_limpieza_autonomo:
    def __init__(self, marca, bateria, capacidad_polvo):
        self.marca = marca
        self.bateria = bateria
        self.capacidad_polvo = capacidad_polvo

    def encender(self):
        print("Robot encendido")

    def limpiar(self):
        print("Iniciando limpieza")

    def regresar_base(self):
        print("Regresando a la base")


class drone_delivery:
    def __init__(self, modelo, carga_maxima, autonomia):
        self.modelo = modelo
        self.carga_maxima = carga_maxima
        self.autonomia = autonomia

    def despegar(self):
        print("Drone despegando")

    def entregar_paquete(self):
        print("Paquete entregado")

    def aterrizar(self):
        print("Drone aterrizando")


class hospital_inteligente:
    def __init__(self, nombre, capacidad_pacientes, nivel_seguridad):
        self.nombre = nombre
        self.capacidad_pacientes = capacidad_pacientes
        self.nivel_seguridad = nivel_seguridad

    def registrar_paciente(self, paciente):
        print(f"Paciente {paciente} registrado")

    def asignar_habitacion(self, paciente, habitacion):
        print(f"Habitación {habitacion} asignada a {paciente}")

    def monitorear_signos(self, paciente):
        print(f"Monitoreando signos vitales de {paciente}")

#===================================================================================================================================
#Principios de la POO

# Abstracción
    #Permite trabajr con objetos sin preocuparnos de como esten dentro, oculta detalles innecesarios, sabes que función tienen el acelerador y el freno, pero no como funciona el motor del carro.

# Encapsulamiento
    #Protege los datos de un objeto ocultando su estado interno. Solo se modifica atraves de metodos controlados (getters y setters). Evita accesos indebidos y mantiene la integridad del objeto.

    # Getters: Son métodos especiales que permiten acceder al valor de un atributo privado de una clase. Funcionan como una forma segura de “leer” la información de un objeto sin exponer directamente sus datos internos.
    # Setters: Son métodos especiales que permiten modificar o actualizar un atributo privado de una clase. Generalmente incluyen validaciones para asegurar que el valor nuevo sea válido antes de asignarlo.

    #Getter → Obtiene (lee) el valor de un atributo privado.

    #Setter → Asigna (modifica) el valor de un atributo privado.

# Herencia
    #Permite que una clase hija herede atributos y métodos de una clase padre. Es como los hijos, tiene caracteristicas de los padres y las suyas propias

# Polimorfismo
    #Un método puede tener diferentes comportamientos, según el objeto que lo use. Muchas formas.
    #Un perro, hablar0 = "guau". Un gato, hablar0 = "miau".

#===================================================================================================================================
#Singleton
    #Garatiza que solo exista una instancia en uan clase y solo accedan al mismo objeto, se usa para centralizar recursos.

#Factory
    #Delega la creación de objetos a una clase especial, cn esto no necesita sabe que clase concreta debe crear, solo se pide el objeto y decide cuando lo entrega.

#Observer
    #Permite centrar un objeto, notificando a otros objetos cada que cambia su estado.



