import smtplib
from email.message import EmailMessage
from os import environ as env

from decimal import Decimal, InvalidOperation, ROUND_HALF_UP

def enviar_email_nao_responda(assunto:str, destinatario:str, conteudo:str, conteudo_HTML:str):
    """envia um email para um cliente.
    
    conteudo_HTML deve ser uma f-string.
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

def moeda_para_centavos(valor):
    """Pega um valor monetário e o transforma em centavos."""
    
    texto = str(valor).strip().replace("R$", "").replace(" ", "")
    if "," in texto:
        texto = texto.replace(".", "").replace(",", ".")
    try:
        return int((Decimal(texto) * 100).quantize(Decimal("1"), rounding=ROUND_HALF_UP))
    except InvalidOperation as erro:
        raise ValueError("Valor monetário inválido") from erro

def formatar_moeda(centavos):
    """Pega um valor em centavos e retorna formatado como Real."""
    
    valor = Decimal(int(centavos)) / 100
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
