import secrets
import hashlib
import hmac
import time

from os import environ as env
from flask import render_template

from services.enviar_email import enviar_email_nao_responda

from model.usuario_model import criar_token, buscar_token, deletar_token

def gerar_token():
    """Gera um código numérico aleatório de 6 dígitos."""
    return f"{secrets.randbelow(1_000_000):06d}"

def enviar_token(email_criptografado: str, id_usuario: int):
    """
    Envia um código de verificação.

    email_criptografado:
        E-mail armazenado de forma criptografada.
        A função de envio descriptografa o destinatário.
    """
    token = gerar_token()

    # Armazena o hash do código, não o código em texto puro.
    chave_secret_hmac = env.get("TOKEN_SHA")
    token_hash = hmac.new(chave_secret_hmac.encode(), token.encode(), hashlib.sha256)
    criar_token(token_hash, id_usuario)
    
    conteudo_html = render_template("email_token.html", token=token)

    conteudo_texto = (
        f"Seu código de verificação é: {token}\n"
        "Este código expira em 10 minutos.\n"
        "Não compartilhe este código com ninguém."
    )

    enviar_email_nao_responda(
        assunto="Seu código de verificação",
        destinatario=email_criptografado,
        conteudo=conteudo_texto,
        conteudo_HTML=conteudo_html,
    )

def validar_token(email_criptografado, token_informado):
    """
    Retorna True se o código for válido.
    Retorna False se estiver incorreto, expirado
    ou se não houver código ativo.
    """
    #TODO: adicionar token na função de hmac
    chave_secret_hmac = env.get("TOKEN_SHA")
    from utils import hoje
    token = buscar_token(hmac.new(chave_secret_hmac.encode(), token.encode(), hashlib.sha256), hoje().date())

    # se o token não existe ou é inválido
    if token is None:
        return False
    else:
        deletar_token(token.id_token)
        return True
