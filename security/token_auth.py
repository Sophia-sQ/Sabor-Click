import hashlib
import hmac
import secrets
from os import environ as env

from flask import render_template

from database import db
#
from services.enviar_email import enviar_email_nao_responda
from utils import hoje


def gerar_token():
    """Gera um código numérico aleatório de seis dígitos."""
    return f"{secrets.randbelow(1_000_000):06d}"


def enviar_token(email_criptografado: str, id_usuario: int):
    """Gera, armazena e envia o código de verificação."""
    chave = env.get("TOKEN_SHA")
    from model.usuario_model import criar_token
    if not chave:
        raise RuntimeError("A variável TOKEN_SHA não está configurada.")

    codigo = gerar_token()

    codigo_hash = hmac.new(
        chave.encode("utf-8"),
        codigo.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()

    registro = criar_token(codigo_hash, id_usuario)

    if registro is None:
        raise RuntimeError("Não foi possível registrar o token.")

    conteudo_html = render_template("email_token.html", token=codigo)

    conteudo_texto = (
        f"Seu código de verificação é: {codigo}\n"
        "Este código expira em 10 minutos.\n"
        "Não compartilhe este código com ninguém."
    )

    enviar_email_nao_responda(
        assunto="Seu código de verificação",
        destinatario=email_criptografado,
        conteudo=conteudo_texto,
        conteudo_HTML=conteudo_html,
    )


def validar_token(id_usuario: int, token_informado: str) -> bool:
    """Valida o código, o prazo de validade e as tentativas."""
    chave = env.get("TOKEN_SHA")
    from model.usuario_model import buscar_token
    if not chave:
        raise RuntimeError("A variável TOKEN_SHA não está configurada.")

    registro = buscar_token(id_usuario, hoje())

    if registro is None:
        return False

    hash_informado = hmac.new(
        chave.encode("utf-8"),
        token_informado.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()

    if not hmac.compare_digest(registro.codigo_hash, hash_informado):
        registro.tentativas += 1

        if registro.tentativas >= 5:
            registro.ativo = False

        db.session.commit()
        return False

    # Código correto: invalida para impedir reutilização.
    registro.ativo = False
    db.session.commit()

    return True
