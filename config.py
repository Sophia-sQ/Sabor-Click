"""Configurações da aplicação Flask por ambiente.

    Carrega variáveis de ambiente a partir de um arquivo .env (quando existe) e
    expõe classes de configuração para desenvolvimento e produção, além do
    objeto `mail` (Flask-Mail) e do dicionário `config_dict` usado pelo app.
"""

import os
import sys
from os import path

from dotenv import load_dotenv
from flask_mail import Mail

#caminho da raiz do projeto
basedir = path.abspath(path.dirname(__file__))


def _dir_app() -> str:
    """Pasta onde a aplicação 'mora'.

    - Empacotado com PyInstaller (--onedir): a pasta do próprio executável
      (ex.: dist/SaborClick/). Assim o banco SQLite fica DENTRO dessa pasta e
      é removido junto quando o usuário apaga a pasta da aplicação.
    - Em desenvolvimento: a raiz do projeto (comportamento anterior).
    """
    if getattr(sys, "frozen", False):        # rodando sob PyInstaller
        return path.dirname(sys.executable)   # ex.: dist/SaborClick/
    return basedir


# Diretório da aplicação (executável quando empacotado, raiz do projeto em dev).
APP_DIR = _dir_app()

# True quando rodando como executável empacotado (modo apresentação/demo).
MODO_EMPACOTADO = getattr(sys, "frozen", False)

# Procura por um arquivo .env na raiz do projeto
if path.exists(path.join(basedir, ".env")):
    load_dotenv(path.join(basedir, ".env"))

mail = Mail()

class Config:
    """Configurações base compartilhadas por todos os ambientes."""
    import secrets
    if MODO_EMPACOTADO:
        SECRET_KEY = secrets.token_hex(32)
    else:
        SECRET_KEY = os.environ.get("SECRET_KEY")


    # Configura o banco de dados.
    # Caminho ABSOLUTO ao lado do executável: garante que o banco seja sempre
    # <APP_DIR>/banco.db (independente do diretório de trabalho) e que apagar a
    # pasta da aplicação remova o banco junto. DATABASE_URL (quando definida)
    # continua tendo prioridade.
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL",
        "sqlite:///" + path.join(APP_DIR, "banco.db"),
    )

    # --- CONFIGURAÇÕES DO FLASK-MAIL ---
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
    MAIL_SUPPRESS_SEND = True


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
