from os import environ as env

import hmac
import hashlib

def gerar_hmac(cpf: str = None, email: str = None) -> str:
    """Gera um hash HMAC determinístico de um CPF ou e-mail para buscas no banco.

    O hash permite localizar registros por valores sensíveis sem armazená-los em
    claro. Deve-se informar apenas CPF OU e-mail por chamada.

    Args:
        cpf (str, optional): CPF a ser transformado em hash.
        email (str, optional): e-mail a ser transformado em hash.

    Returns:
        str: hash HMAC-SHA256 em hexadecimal.

    Raises:
        ValueError: se a variável *_LOOKUP_HMAC_SECRET correspondente não estiver
            configurada no .env.
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