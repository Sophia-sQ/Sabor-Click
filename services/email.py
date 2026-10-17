from flask_mail import Message
from config import mail

from security import descriptografar

def enviar_email_nao_responda(assunto:str, destinatario:str, conteudo:str, conteudo_HTML:str):
    """envia um email para um cliente. O email é descriptografado na função.
    
    conteudo_HTML deve ser uma chamada de render_template.
    """
    
    msg = Message(assunto, [descriptografar(destinatario)])
    msg.body = conteudo
    msg.html = conteudo_HTML
    
    mail.send(msg)