import os
os.system("cls")

# Diagnostico_Jose.py
# Simulador de pedidos
# Conceptos básicos: variables, inputs, condicionales, funciones y bucles

# Elegir una temática de tienda y escribir 3 productos
productos = ["Frappe", "Bubba", "Americano"]
precios = [68, 70, 50]

# Función para calcular total
def calcular_total(cantidades, precios):
    total = 0
    for i in range(len(cantidades)):
        total += cantidades[i] * precios[i]
    return total

# Menú para usuario (Outputs)
print("Menú de cafetería, sea usted Bienvenido")

nombre = input("Nombre del cliente: ")
cantidades = []

# Captura de cantidades
for i in range(len(productos)):
    print(f"{i+1}. {productos[i]} - ${precios[i]}")
    cant = int(input(f"¿Cuántos {productos[i]} desea? "))
    cantidades.append(cant)

# Impresión del pedido
print(f"\n--- Resumen del pedido de {nombre} ---")
for i in range(len(productos)):
    if cantidades[i] > 0:
        subtotal = cantidades[i] * precios[i]
        print(f"{productos[i]} x {cantidades[i]} = ${subtotal}")

# Cálculo y muestra del total
total = calcular_total(cantidades, precios)
print(f"\nTotal a pagar: ${total}")
print("¡Gracias por su compra!")















