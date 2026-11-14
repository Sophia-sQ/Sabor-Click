"""Configurações da aplicação Flask por ambiente.

    Carrega variáveis de ambiente a partir de um arquivo .env (quando existe) e
    expõe classes de configuração para desenvolvimento e produção, além do
    objeto `mail` (Flask-Mail) e do dicionário `config_dict` usado pelo app.
"""

import os
from os import path

from dotenv import load_dotenv
from flask_mail import Mail

#caminho da raiz do projeto
basedir = path.abspath(path.dirname(__file__))

# Procura por um arquivo .env na raiz do projeto
if path.exists(path.join(basedir, ".env")):
    load_dotenv(path.join(basedir, ".env"))

mail = Mail()

class Config:
    """Configurações base compartilhadas por todos os ambientes."""

    SECRET_KEY = os.environ.get("SECRET_KEY")

    # Configura o banco de dados
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL", "sqlite:///banco.db")

    # Autenticação com bancos Turso (libSQL): quando a URL for de um banco
    # remoto libSQL, o token precisa ser entregue ao driver via connect_args,
    # pois passá-lo apenas na query string da URL não é lido de forma confiável.
    # Para SQLite local (sem libsql na URL) nada muda.
    SQLALCHEMY_ENGINE_OPTIONS = {}
    if "libsql" in SQLALCHEMY_DATABASE_URI:
        _turso_auth_token = os.environ.get("TURSO_AUTH_TOKEN")
        if _turso_auth_token:
            SQLALCHEMY_ENGINE_OPTIONS = {
                "connect_args": {"auth_token": _turso_auth_token},
            }

    # --- CONFIGURAÇÕES DO FLASK-MAIL ---
    MAIL_SERVER = os.environ.get("MAIL_SERVER")
    MAIL_PORT = int(os.environ.get("MAIL_PORT"))

    # Segurança da conexão
    MAIL_USE_TLS = bool(int(os.environ.get("MAIL_USE_TLS")))
    MAIL_USE_SSL = bool(int(os.environ.get("MAIL_USE_SSL")))

    # Credenciais de autenticação
    MAIL_USERNAME = os.environ.get("MAIL_USERNAME")
    MAIL_PASSWORD = os.environ.get("MAIL_PASSWORD")

    # Remetente padrão dos e-mails
    MAIL_DEFAULT_SENDER = os.environ.get("MAIL_DEFAULT_SENDER")


class DevelopmentConfig(Config):
    """Configurações para o ambiente de Desenvolvimento"""

    DEBUG = True
    # Impede que e-mails reais sejam disparados durante os testes de código
    # Os e-mails são interceptados na memória pelo Flask
    MAIL_SUPPRESS_SEND = False


class ProductionConfig(Config):
    """Configurações para o ambiente de Produção"""
    DEBUG = False
    # Em produção, os e-mails DEVEM ser enviados de fato
    MAIL_SUPPRESS_SEND = False


# Dicionário auxiliar para mapear os ambientes no app.py
config_dict = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "default": DevelopmentConfig,
}
