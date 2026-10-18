import secrets
import hashlib
import hmac
import time

from flask import render_template

from services.enviar_email import enviar_email_nao_responda


TEMPO_EXPIRACAO = 10 * 60  # 10 minutos

tokens_ativos = {}


def gerar_token():
    """Gera um código numérico aleatório de 6 dígitos."""
    return f"{secrets.randbelow(1_000_000):06d}"


def enviar_token(email_criptografado):
    """
    Gera e envia um código de verificação.

    email_criptografado:
        E-mail armazenado de forma criptografada.
        A função de envio descriptografa o destinatário.
    """
    token = gerar_token()

    # Armazena o hash do código, não o código em texto puro.
    token_hash = hashlib.sha256(token.encode("utf-8")).hexdigest()
    expiracao = time.time() + TEMPO_EXPIRACAO

    tokens_ativos[email_criptografado] = {
        "hash": token_hash,
        "expiracao": expiracao,
        "tentativas": 0,
    }


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
    registro = tokens_ativos.get(email_criptografado)

    if registro is None:
        return False

    # Verifica se o código expirou.
    if time.time() >= registro["expiracao"]:
        del tokens_ativos[email_criptografado]
        return False

    # Limita a 5 tentativas por código.
    if registro["tentativas"] >= 5:
        del tokens_ativos[email_criptografado]
        return False

    if not isinstance(token_informado, str):
        registro["tentativas"] += 1
        return False

    if ( len(token_informado) != 6 or not token_informado.isdigit()):
        registro["tentativas"] += 1
        return False

    token_hash = hashlib.sha256(token_informado.encode("utf-8")).hexdigest()

    if hmac.compare_digest(registro["hash"],token_hash):
        # Impede que o mesmo código seja reutilizado.
        del tokens_ativos[email_criptografado]
        return True

    registro["tentativas"] += 1
    return False
