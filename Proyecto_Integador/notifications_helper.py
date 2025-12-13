import webbrowser
import urllib.parse
import time

class NotificationsHelper:
    
    @staticmethod
    def generar_link_whatsapp(telefono, mensaje):
        if not telefono: return None
        # Dejar solo números
        num = "".join(filter(str.isdigit, telefono))
        if len(num) < 10: return None
        
        msg_encoded = urllib.parse.quote(mensaje)
        return f"https://web.whatsapp.com/send?phone={num}&text={msg_encoded}"

    @staticmethod
    def generar_link_correo(email, asunto, cuerpo):
        if not email: return None
        asunto_enc = urllib.parse.quote(asunto)
        cuerpo_enc = urllib.parse.quote(cuerpo)
        # Usamos la interfaz web de Gmail para evitar configurar Outlook
        return f"https://mail.google.com/mail/?view=cm&fs=1&to={email}&su={asunto_enc}&body={cuerpo_enc}"

    @staticmethod
    def enviar_notificacion_agendar(nombre, fecha, hora, telefono, email):
        msg_wa = f"Hola {nombre}, tu cita en Ortho Guzmán quedó registrada para el {fecha} a las {hora}. Por favor llega 5 min antes. 🦷"
        NotificationsHelper._abrir_enlaces(telefono, email, msg_wa, "Confirmación de Cita")

    @staticmethod
    def enviar_notificacion_modificacion(nombre, fecha, hora, telefono, email, es_recorrida=False):
        tipo_msg = "ajustada" if es_recorrida else "modificada"
        extra = " debido a ajustes en la agenda" if es_recorrida else ""
        
        msg_wa = f"Hola {nombre}, tu cita en Ortho Guzmán ha sido {tipo_msg} para el {fecha} a las {hora}{extra}. Saludos."
        asunto = "Actualización de Cita - Ortho Guzmán"
        
        NotificationsHelper._abrir_enlaces(telefono, email, msg_wa, asunto)

    @staticmethod
    def _abrir_enlaces(telefono, email, mensaje_wa, asunto_mail):
        abrio_algo = False
        
        # 1. WhatsApp
        link_wa = NotificationsHelper.generar_link_whatsapp(telefono, mensaje_wa)
        if link_wa:
            webbrowser.open_new_tab(link_wa)
            abrio_algo = True

        # Pequeña pausa si se van a abrir dos cosas para el mismo paciente
        if abrio_algo and email: 
            time.sleep(1)

        # 2. Correo
        link_mail = NotificationsHelper.generar_link_correo(email, asunto_mail, mensaje_wa)
        if link_mail:
            webbrowser.open_new_tab(link_mail)
