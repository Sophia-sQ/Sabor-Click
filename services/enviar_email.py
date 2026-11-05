from flask_mail import Message
from config import mail

from security import descriptografar

def enviar_email_nao_responda(assunto:str, destinatario:str, conteudo:str, conteudo_HTML:str):
    """Envia um e-mail transacional ("não responda") para um destinatário.

    O endereço de destino é descriptografado dentro da função antes do envio.

    Args:
        assunto (str): assunto do e-mail.
        destinatario (str): e-mail de destino (criptografado).
        conteudo (str): corpo do e-mail em texto puro.
        conteudo_HTML (str): corpo do e-mail em HTML (normalmente o resultado de
            render_template).
    """
    
    msg = Message(assunto, [descriptografar(destinatario)])
    msg.body = conteudo
    msg.html = conteudo_HTML
    
    mail.send(msg)