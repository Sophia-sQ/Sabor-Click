"""Geração, envio e verificação de tokens de autenticação por e-mail."""

import secrets
import hashlib
import hmac

from os import environ as env
from flask import render_template

from services.enviar_email import enviar_email_nao_responda
from model.usuario_model import criar_token, buscar_token
from database import db
from utils import hoje


def gerar_token() -> str:
    """Gera um código numérico aleatório de seis dígitos (com zeros à esquerda)."""
    return f"{secrets.randbelow(1_000_000):06d}"


def enviar_token(email_criptografado: str, id_usuario: int) -> None:
    """Gera, armazena (hash) e envia por e-mail o código de verificação.

    Cria um código de seis dígitos, grava seu HMAC no banco e dispara o e-mail
    com o código em texto e HTML.

    Args:
        email_criptografado (str): e-mail de destino (criptografado).
        id_usuario (int): identificador do usuário dono do token.

    Raises:
        RuntimeError: se a variável TOKEN_SHA não estiver configurada ou se não
            for possível registrar o token.
    """

    chave = env.get("TOKEN_SHA")

    if not chave:
        raise RuntimeError("A variável TOKEN_SHA não está configurada.")

    codigo = gerar_token()

    codigo_hash = hmac.new(
        chave.encode("utf-8"),
        codigo.encode("utf-8"),
        hashlib.sha256
    ).hexdigest()

    registro = criar_token(codhash=codigo_hash, id_usuario=id_usuario)

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
    """Valida o código informado, verificando validade, tentativas e expiração.

    Compara o hash do código informado com o armazenado. Em caso de erro,
    incrementa o contador de tentativas e desativa o token após 5 tentativas.
    Em caso de sucesso, invalida o token para impedir reutilização.

    Args:
        id_usuario (int): identificador do usuário dono do token.
        token_informado (str): código digitado pelo usuário.

    Returns:
        bool: True se o código for válido; False caso contrário.

    Raises:
        RuntimeError: se a variável TOKEN_SHA não estiver configurada.
    """

    chave = env.get("TOKEN_SHA")

    if not chave:
        raise RuntimeError("A variável TOKEN_SHA não está configurada.")

    registro = buscar_token(id_usuario, hoje())

    if registro is None:
        return False

    hash_informado = hmac.new(
        chave.encode("utf-8"),
        token_informado.encode("utf-8"),
        hashlib.sha256
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


def registrar_comandos(app) -> None:
    """Registra os comandos de CLI deste módulo na aplicação Flask.

    Deve ser chamada pela fábrica da aplicação (app.create_app) após o app ser
    criado, evitando o import circular que ocorreria ao importar 'app' no topo.

    Args:
        app (Flask): instância da aplicação Flask.
    """

    @app.cli.command("token")
    def ver_token():
        """Exibe o token ativo (código de 6 dígitos + expiração) dos usuários da lista.

        Considera apenas o administrador (ADMIN_EMAIL) e os usuários cadastrados
        em seeds.lista_usuarios. Para cada um que tenha um token ativo,
        reconstrói o código de seis dígitos a partir do codigo_hash por
        força-bruta do espaço de 000000 a 999999 (viável por ser pequeno),
        usando a chave TOKEN_SHA.

        Raises:
            RuntimeError: se a variável TOKEN_SHA não estiver configurada.
        """
        from datetime import timedelta

        from click import secho

        from security import gerar_hmac
        from model.usuario_model import Usuario
        from seeds import lista_usuarios

        chave = env.get("TOKEN_SHA")

        if not chave:
            raise RuntimeError("A variável TOKEN_SHA não está configurada.")

        chave_bytes = chave.encode("utf-8")

        # Tabela hash -> código (uma única varredura reaproveitada para todos).
        por_hash = {
            hmac.new(chave_bytes, f"{numero:06d}".encode("utf-8"), hashlib.sha256).hexdigest(): f"{numero:06d}"
            for numero in range(1_000_000)
        }

        # Usuários da lista: admin + cadastrados em seeds.lista_usuarios.
        emails = [env.get("ADMIN_EMAIL")]
        emails += [email for (_, _, email, _, _) in lista_usuarios]

        for email in emails:
            if not email:
                continue

            usuario = db.session.execute(
                db.select(Usuario).where(Usuario.email_hmac == gerar_hmac(email=email)),
            ).scalar_one_or_none()

            if usuario is None:
                continue

            # buscar_token já valida 'ativo' e a expiração de 10 minutos.
            registro = buscar_token(usuario.id_usuario, hoje())

            if registro is None:
                secho(f"{email}: nenhum token ativo", fg="yellow")
                continue

            codigo = por_hash.get(registro.codigo_hash, "(não encontrado)")
            expira_em = registro.criado_em + timedelta(minutes=10)

            secho(
                f"{email}: código {codigo} · válido até {expira_em:%d/%m/%Y %H:%M:%S}",
                fg="green",
                bold=True,
            )