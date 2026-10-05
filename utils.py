import smtplib
from email.message import EmailMessage
from os import environ as env
import hmac
import hashlib

from cryptography.fernet import Fernet
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



# ... (mantenha suas funções enviar_email_nao_responda, moeda_para_centavos, etc.)

def obter_chave_fernet() -> Fernet:
    """Recupera a chave Fernet do arquivo .env e inicializa o objeto."""
    chave = env.get("FERNET_ENCRYPTION_KEY")
    if not chave:
        raise ValueError("A variável FERNET_ENCRYPTION_KEY não está configurada no .env")
    # O Fernet exige que a chave esteja em bytes
    return Fernet(chave.encode())

def criptografar_cpf(cpf: str) -> str:
    """Criptografa o CPF de forma bidirecional (retorna string)."""
    if not cpf:
        return ""
    fernet = obter_chave_fernet()
    # Transforma a string do CPF em bytes, criptografa e decodifica o resultado para string
    cpf_criptografado = fernet.encrypt(cpf.encode())
    return cpf_criptografado.decode()

def descriptografar_cpf(cpf_criptografado: str) -> str:
    """Descriptografa o CPF retornando a string original."""
    if not cpf_criptografado:
        return ""
    fernet = obter_chave_fernet()
    # Transforma a string criptografada em bytes, descriptografa e decodifica para string original
    cpf_bytes = fernet.decrypt(cpf_criptografado.encode())
    return cpf_bytes.decode()

def gerar_hmac_cpf(cpf: str) -> str:
    """Gera um hash determinístico do CPF para ser utilizado em buscas no banco de dados."""
    if not cpf:
        return ""
    chave_secret_hmac = env.get("CPF_LOOKUP_HMAC_SECRET")
    if not chave_secret_hmac:
        raise ValueError("A variável CPF_LOOKUP_HMAC_SECRET não está configurada no .env")
    
    # Gera o HMAC utilizando SHA-256
    resultado = hmac.new(chave_secret_hmac.encode(), cpf.encode(), hashlib.sha256)
    return resultado.hexdigest()
