#Practica3. Introducción al Polimorfimo
# Simular un sistema de cobro con multiples opciones de pago.

class pago_tarjeta:
    def procesar_pago (self, cantidad):
        return f"Procesando pago de ${cantidad} con tarjeta bancaria."

class trasferencia:
    def procesar_pago(self, cantidad):
        return f"Procesadno pago con transferencia por la cantidad de ${cantidad}"

class deposito:
    def procesar_pago(self, cantidad):
        return f"Proceando pago por medio deposito en ventanilla la cantidad de ${cantidad}"

class paypal:
    def procesar_pago(self, cantidad):
        return f"Procesando pago de ${cantidad} por medio de paypla"

# Instancia
metodo_pago = {pago_tarjeta(), trasferencia(), deposito(), paypal()}

for m in metodo_pago:
    print(m.procesar_pago(500))

#Actividad. Procesar con diferentes cant en cada uno de las formas de pago ejemplo: 100 con tarjeta, 500 con transferencia, 2000 con pyapal, 400 con deposito.

# Instancia
pago1 = pago_tarjeta()
pago2 = trasferencia()
pago3 = deposito()
pago4 = paypal()

print(pago1.procesar_pago(100)) 
print(pago2.procesar_pago(500))
print(pago3.procesar_pago(400))
print(pago4.procesar_pago(2000))


class WhatsApp:
    def proceso(self, calf):
        return f"Este mesaje es enviado para hacer entrega de la calificación del alumno que es de {calf}. Por medio de WhatsApp."

class pag_web:
    def proceso(self, calf):
        return f"Alumno tiene la calificación de {calf}."

class correo:
    def proceso(self, calf):
        return f"Este corre es enviado para hacer entrega de la calificación del alumno que es de {calf}."

class mesanges:
    def proceso(self, calf):
        return f"Este mesaje es enviado para hacer entrega de la calificación del alumno que es de {calf}. Por medio de mensajes."

# Instancia
mostrar_calf = {WhatsApp(), pag_web(), correo(), mesanges()}

for m in mostrar_calf:
    print(m.proceso(9.7))

