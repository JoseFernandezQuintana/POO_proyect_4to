import webbrowser
import urllib.parse

class NotificationsHelper:
    
    @staticmethod
    def generar_link_whatsapp(telefono, mensaje):
        if not telefono: return None
        # Limpieza básica de número
        num = "".join(filter(str.isdigit, telefono))
        if len(num) < 10: return None # Número inválido
        
        msg_encoded = urllib.parse.quote(mensaje)
        return f"https://web.whatsapp.com/send?phone={num}&text={msg_encoded}"

    @staticmethod
    def generar_link_correo(email, asunto, cuerpo):
        if not email: return None
        # Codificamos texto para URL
        asunto_enc = urllib.parse.quote(asunto)
        cuerpo_enc = urllib.parse.quote(cuerpo)
        
        # TRUCO: Usamos la URL de composición de Gmail
        return f"https://mail.google.com/mail/?view=cm&fs=1&to={email}&su={asunto_enc}&body={cuerpo_enc}"

    @staticmethod
    def enviar_notificacion_agendar(nombre, fecha, hora, telefono, email):
        msg_wa = f"Hola {nombre}, tu cita en Ortho Guzmán quedó registrada para el {fecha} a las {hora}. Por favor llega 5 min antes. 🦷"
        
        # 1. WhatsApp
        link_wa = NotificationsHelper.generar_link_whatsapp(telefono, msg_wa)
        if link_wa: webbrowser.open(link_wa)

        # 2. Correo (Abre cliente predeterminado)
        if email:
            asunto = "Confirmación de Cita - Ortho Guzmán"
            link_mail = NotificationsHelper.generar_link_correo(email, asunto, msg_wa)
            webbrowser.open(link_mail)

    @staticmethod
    def enviar_notificacion_modificacion(nombre, fecha, hora, telefono, email, es_recorrida=False):
        tipo_msg = "ajustada" if es_recorrida else "modificada"
        extra = " debido a ajustes en la agenda" if es_recorrida else ""
        
        msg_wa = f"Hola {nombre}, tu cita en Ortho Guzmán ha sido {tipo_msg} para el {fecha} a las {hora}{extra}. Saludos."

        # WhatsApp
        link_wa = NotificationsHelper.generar_link_whatsapp(telefono, msg_wa)
        if link_wa: webbrowser.open(link_wa)
        
        # Correo
        if email:
            asunto = "Actualización de Cita - Ortho Guzmán"
            link_mail = NotificationsHelper.generar_link_correo(email, asunto, msg_wa)
            webbrowser.open(link_mail)
