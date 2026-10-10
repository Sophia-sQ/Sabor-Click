from os import environ as env

import smtplib
from email.message import EmailMessage

import hmac
import hashlib

from cryptography.fernet import Fernet

from decimal import Decimal, InvalidOperation, ROUND_HALF_UP

#interação com cliente
def enviar_email_nao_responda(assunto:str, destinatario:str, conteudo:str, conteudo_HTML:str):
    """envia um email para um cliente. O email é descriptografado na função.
    
    conteudo_HTML deve ser uma f-string.
    """
    
    email = EmailMessage()

    email["Subject"] = assunto
    email["From"] = env.get("EMAIL")
    email["To"] = descriptografar(destinatario)

    # Versão para clientes que não exibem HTML
    email.set_content(conteudo)
    
    # Versão HTML
    email.add_alternative(conteudo_HTML, subtype="html")
    
    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        smtp.login(env.get("EMAIL"), env.get("PASSWORD"))
        smtp.send_message(email)

#formatação monetária
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

#segurança
def obter_chave_fernet() -> Fernet:
    """Recupera a chave Fernet do arquivo .env e inicializa o objeto."""
    chave = env.get("FERNET_ENCRYPTION_KEY")
    
    if not chave:
        raise ValueError("A variável FERNET_ENCRYPTION_KEY não está configurada no .env")
    
    # O Fernet exige que a chave esteja em bytes
    return Fernet(chave.encode("utf-8"))

def criptografar(dado: str) -> str:
    """Criptografa o dado de forma bidirecional (retorna string)."""
    
    if not dado:
        return False
    
    fernet = obter_chave_fernet()
    
    # Transforma a string bytes, criptografa e decodifica o resultado para string
    dado_criptografado = fernet.encrypt(dado.encode())
    return dado_criptografado.decode()

def descriptografar(dado_criptografado: str) -> str:
    """Descriptografa o dado retornando a string original."""
    
    if not dado_criptografado:
        return False
    
    fernet = obter_chave_fernet()
    
    # Transforma a string criptografada em bytes, descriptografa e decodifica para string original
    dado_bytes = fernet.decrypt(dado_criptografado.encode())
    return dado_bytes.decode()

def gerar_hmac(cpf: str = None, email: str = None) -> str:
    """Gera um hash determinístico do CPF ou email para ser utilizado em buscas no banco de dados.
    
    Warning: essa função trata apenas cpf ou email."""
    
    if cpf:
        chave_secret_hmac = env.get("CPF_LOOKUP_HMAC_SECRET")
        dado=cpf
        
    elif email:
        chave_secret_hmac = env.get("EMAIL_LOOKUP_HMAC_SECRET")
        dado=email
    
    if not chave_secret_hmac:
        raise ValueError("A variável . . ._LOOKUP_HMAC_SECRET não está configurada no .env")
            
    resultado = hmac.new(chave_secret_hmac.encode(), dado.encode(), hashlib.sha256)
    return resultado.hexdigest()