from os import environ as env

from cryptography.fernet import Fernet


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

