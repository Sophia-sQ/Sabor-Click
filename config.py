import os
from os import path
<<<<<<< Updated upstream
from dotenv import load_dotenv
from flask_mail import Mail
=======

from dotenv import load_dotenv
from flask_mail import Mail

>>>>>>> Stashed changes
#caminho da raiz do projeto
basedir = path.abspath(path.dirname(__file__))

# Procura por um arquivo .env na raiz do projeto
<<<<<<< Updated upstream
if path.exists(path.join(basedir, '.env')):
    load_dotenv(path.join(basedir, '.env'))
=======
if path.exists(path.join(basedir, ".env")):
    load_dotenv(path.join(basedir, ".env"))
>>>>>>> Stashed changes

mail = Mail()

class Config:
    """Configurações base"""
<<<<<<< Updated upstream
    
    SECRET_KEY = os.environ.get('SECRET_KEY')
    
    # Configura o banco de dados
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'sqlite:///banco.db')
    
    # --- CONFIGURAÇÕES DO FLASK-MAIL ---
    MAIL_SERVER = os.environ.get('MAIL_SERVER')
    MAIL_PORT = int(os.environ.get('MAIL_PORT'))
    
    # Segurança da conexão
    MAIL_USE_TLS = bool(int(os.environ.get('MAIL_USE_TLS')))
    MAIL_USE_SSL = bool(int(os.environ.get('MAIL_USE_SSL')))
    
    # Credenciais de autenticação
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    
    # Remetente padrão dos e-mails
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER')
=======

    SECRET_KEY = os.environ.get("SECRET_KEY")

    # Configura o banco de dados
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL", "sqlite:///banco.db")

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
>>>>>>> Stashed changes


class DevelopmentConfig(Config):
    """Configurações para o ambiente de Desenvolvimento"""
<<<<<<< Updated upstream
    DEBUG = True
    # Impede que e-mails reais sejam disparados durante os testes de código
    # Os e-mails são interceptados na memória pelo Flask
    MAIL_SUPPRESS_SEND = False 
=======

    DEBUG = True
    # Impede que e-mails reais sejam disparados durante os testes de código
    # Os e-mails são interceptados na memória pelo Flask
    MAIL_SUPPRESS_SEND = False
>>>>>>> Stashed changes


class ProductionConfig(Config):
    """Configurações para o ambiente de Produção"""
<<<<<<< Updated upstream
=======

>>>>>>> Stashed changes
    DEBUG = False
    # Em produção, os e-mails DEVEM ser enviados de fato
    MAIL_SUPPRESS_SEND = False


# Dicionário auxiliar para mapear os ambientes no app.py
config_dict = {
<<<<<<< Updated upstream
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
=======
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "default": DevelopmentConfig,
>>>>>>> Stashed changes
}
