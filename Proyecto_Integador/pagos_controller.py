import database

class PagosController:
    def __init__(self):
        pass
    
    def buscar_pacientes_con_deuda(self, query):
        """
        Llama a la BD para buscar citas no pagadas.
        Si query está vacío, trae las últimas deudas generales.
        """
        return database.buscar_citas_con_deuda(query)

    def obtener_items_cita(self, cita_id):
        """
        Obtiene qué se hizo en esa cita (servicios) 
        para mostrarlos en el recibo o lista de cobro.
        """
        return database.obtener_detalle_deuda(cita_id)

    def procesar_pago(self, cita_id, monto, metodo, nota):
        """
        Registra el pago.
        Realiza validaciones básicas antes de enviar a BD.
        """
        try:
            monto_float = float(monto)
            if monto_float <= 0:
                return False, "El monto debe ser mayor a 0."
        except ValueError:
            return False, "El monto debe ser un número válido."

        if not metodo:
            return False, "Seleccione un método de pago."

        # Usuario ID: Por ahora usamos 4 (Admin) o podríamos pasarlo desde el Login.
        # Si tienes el ID del usuario logueado en una variable global, úsalo aquí.
        usuario_id = 4 
        
        return database.registrar_pago_bd(cita_id, monto_float, metodo, nota, usuario_id)