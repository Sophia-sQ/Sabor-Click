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

    # --- CONFIGURAÇÕES DO FLASK-MAIL ---
    # Usa valores padrão seguros quando a variável não está definida, para não
    # impedir a inicialização da aplicação por configuração de e-mail ausente.
    MAIL_SERVER = os.environ.get("MAIL_SERVER")
    MAIL_PORT = int(os.environ.get("MAIL_PORT") or 587)

    # Segurança da conexão
    MAIL_USE_TLS = bool(int(os.environ.get("MAIL_USE_TLS") or 0))
    MAIL_USE_SSL = bool(int(os.environ.get("MAIL_USE_SSL") or 0))

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
