import smtplib
from email.message import EmailMessage
from os import environ as env


def enviar_email_nao_responda(assunto:str, destinatario:str, conteudo:str, conteudo_HTML:str):
    """envia um email para um cliente.
    
    conteudo_HTML deve ser uma f-string
    """
    
    email = EmailMessage()

    email["Subject"] = assunto
    email["From"] = env.get("EMAIL")
    email["To"] = destinatario

    # Versão para clientes que não exibem HTML
    email.set_content(conteudo)
    
    # Versão HTML
    email.add_alternative(conteudo_HTML, subtype="html")
    
    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        smtp.login(env.get("EMAIL"), env.get("PASSWORD"))
        smtp.send_message(email)
