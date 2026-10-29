import hashlib
import hmac
from os import environ as env


def gerar_hmac(cpf: str | None = None, email: str | None = None) -> str:
    """Gera um hash determinístico do CPF ou email para ser utilizado em buscas no banco de dados.
    
    Warning: essa função trata apenas cpf ou email.
    """
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
