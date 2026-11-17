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


def _gerar_segredos_demo() -> None:
    """Gera segredos efêmeros em memória quando empacotado (modo demo).

    No executável empacotado não há arquivo .env, então as chaves de
    criptografia/HMAC/token usadas pela aplicação e pela carga de dados (seeds)
    ficam indefinidas, o que quebra o seed inicial (criptografar/gerar_hmac) e,
    por consequência, deixa o banco vazio. Como o modo empacotado RECRIA o banco
    do zero a cada execução (database.init_app), gerar um conjunto de chaves novo
    por execução é consistente: o que é cifrado/hasheado no seed é lido de volta
    na mesma execução. Espelha a geração automática de SECRET_KEY já existente.

    Só define cada variável se ela ainda não existir no ambiente (um .env ou
    variáveis reais, quando presentes, continuam tendo prioridade).
    """
    if not MODO_EMPACOTADO:
        return

    import secrets as _secrets

    from cryptography.fernet import Fernet

    if MODO_EMPACOTADO:
        os.environ.setdefault("SECRET_KEY", _secrets.token_hex(32))


# Em modo empacotado, garante os segredos antes de qualquer seed/criptografia.
_gerar_segredos_demo()


def _dir_recursos() -> str:
    """Pasta dos recursos SOMENTE LEITURA empacotados (templates, static, docs).

    - Empacotado com PyInstaller: a pasta temporária de extração (sys._MEIPASS),
      onde ficam os arquivos adicionados via 'datas' no .spec.
    - Em desenvolvimento: a raiz do projeto.
    """
    base = getattr(sys, "_MEIPASS", None)
    if base:
        return base
    return basedir


# Raiz dos recursos empacotados (leitura). Em dev é igual a APP_DIR/basedir.
RECURSOS_DIR = _dir_recursos()


def caminho_docs(nome_arquivo: str) -> str:
    """Resolve o caminho de leitura de um arquivo de docs/ (ex.: JSON de imagens).

    Prefere a cópia GRAVÁVEL ao lado do executável (APP_DIR/docs), que recebe as
    alterações feitas pelo admin em tempo de execução; se ela não existir, usa a
    cópia SOMENTE LEITURA empacotada (RECURSOS_DIR/docs). Em desenvolvimento
    ambos apontam para a raiz do projeto.

    Args:
        nome_arquivo (str): nome do arquivo dentro de docs/ (ex.:
            "imagens-menu.json").

    Returns:
        str: caminho absoluto para leitura.
    """
    gravavel = path.join(APP_DIR, "docs", nome_arquivo)
    if path.exists(gravavel):
        return gravavel
    return path.join(RECURSOS_DIR, "docs", nome_arquivo)


def carregar_json_docs(nome_arquivo: str) -> dict:
    """Lê um JSON de docs/ tolerando ausência/corrupção (retorna {} nesses casos).

    Centraliza a leitura dos registros de imagens usados pelas páginas do
    cliente e do admin. A ausência de um registro de imagens NUNCA deve derrubar
    uma página (resultando em 500): sem o arquivo, a página apenas não mostra as
    imagens. Resolve o caminho via caminho_docs (gravável -> bundle).

    Args:
        nome_arquivo (str): nome do arquivo em docs/ (ex.: "imagens-menu.json").

    Returns:
        dict: conteúdo do JSON, ou {} se o arquivo não existir ou for inválido.
    """
    import json

    try:
        with open(caminho_docs(nome_arquivo), encoding="utf-8") as arq:
            return json.load(arq)
    except (FileNotFoundError, json.JSONDecodeError, OSError):
        return {}


def caminho_docs_gravavel(nome_arquivo: str) -> str:
    """Caminho de ESCRITA de um arquivo de docs/ (sempre em APP_DIR/docs)."""
    return path.join(APP_DIR, "docs", nome_arquivo)


def pasta_static_gravavel(*partes: str) -> str:
    """Caminho de ESCRITA dentro de static/ (sempre em APP_DIR/static).

    Usado pelos uploads de imagem do admin. Quando empacotado, APP_DIR é a pasta
    do executável — gravável — enquanto RECURSOS_DIR (sys._MEIPASS) é temporário.
    """
    return path.join(APP_DIR, "static", *partes)


def preparar_dados_empacotado() -> None:
    """Semeia os dados graváveis a partir do bundle no modo empacotado.

    Copia, uma única vez e apenas quando empacotado (PyInstaller), as pastas
    SOMENTE LEITURA do bundle (RECURSOS_DIR/docs e RECURSOS_DIR/static) para a
    pasta GRAVÁVEL ao lado do executável (APP_DIR), permitindo que o admin
    altere JSONs de imagens e envie uploads em runtime. É idempotente: só copia
    o que ainda não existe no destino.

    Em desenvolvimento é um no-op (RECURSOS_DIR == APP_DIR == raiz do projeto).
    """
    if not MODO_EMPACOTADO:
        return
    if path.abspath(RECURSOS_DIR) == path.abspath(APP_DIR):
        return

    import shutil

    for sub in ("docs", "static"):
        origem = path.join(RECURSOS_DIR, sub)
        destino = path.join(APP_DIR, sub)
        if not path.isdir(origem):
            # O bundle não traz esta pasta (ex.: .spec sem 'docs'). Não há o que
            # semear; a leitura (caminho_docs) continuará usando o fallback.
            continue
        try:
            # copytree com dirs_exist_ok preserva o que o usuário já alterou e só
            # preenche os arquivos ausentes no destino (não sobrescreve existentes).
            shutil.copytree(origem, destino, dirs_exist_ok=True,
                            copy_function=_copiar_se_ausente)
        except OSError:
            # Falha de permissão/antivírus ao copiar não deve derrubar o app: a
            # leitura cai no fallback RECURSOS_DIR (bundle), que é somente-leitura
            # mas suficiente para as páginas do cliente.
            pass


def _copiar_se_ausente(origem: str, destino: str) -> None:
    """copy2 que NÃO sobrescreve um arquivo de destino já existente."""
    import shutil

    if path.exists(destino):
        return
    shutil.copy2(origem, destino)

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
