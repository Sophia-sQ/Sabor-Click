"""Funções de criptografia simétrica (Fernet) de dados sensíveis."""

from os import environ as env

from cryptography.fernet import Fernet

def obter_chave_fernet() -> Fernet:
    """Recupera a chave Fernet do .env e inicializa o objeto Fernet.

    Returns:
        Fernet: objeto de criptografia inicializado com a chave do ambiente.

    Raises:
        ValueError: se a variável FERNET_ENCRYPTION_KEY não estiver configurada.
    """
    
    chave = env.get("FERNET_ENCRYPTION_KEY")
    
    if not chave:
        raise ValueError("A variável FERNET_ENCRYPTION_KEY não está configurada no .env")
    
    # O Fernet exige que a chave esteja em bytes
    return Fernet(chave.encode("utf-8"))

def criptografar(dado: str) -> str | None:
    """Criptografa uma string de forma bidirecional (reversível).

    Args:
        dado (str): texto a ser criptografado.

    Returns:
        str: texto criptografado; None se `dado` for vazio/None.
    """
    
    if not dado:
        return None
    
    fernet = obter_chave_fernet()
    
    # Transforma a string bytes, criptografa e decodifica o resultado para string
    dado_criptografado = fernet.encrypt(dado.encode())
    return dado_criptografado.decode()

def descriptografar(dado_criptografado: str) -> str | None:
    """Descriptografa uma string, retornando o texto original.

    Args:
        dado_criptografado (str): texto criptografado a ser revertido.

    Returns:
        str: texto original; False se a entrada for vazia/None.
    """
    
    if not dado_criptografado:
        return None
    
    fernet = obter_chave_fernet()
    
    # Transforma a string criptografada em bytes, descriptografa e decodifica para string original
    dado_bytes = fernet.decrypt(dado_criptografado.encode())
    return dado_bytes.decode()

