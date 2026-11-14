"""Blueprint administrativo e utilitários de conversão de dados de formulário."""

from flask import Blueprint, redirect, url_for
from decimal import Decimal

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")

# ========================== funções internas ==========================

def _retorno():
    """Redireciona para a página de serviços do admin."""
    return redirect(url_for("admin.pagina_servicos"))

def _decimal_form(valor) -> Decimal:
    """Converte texto de formulário em Decimal, aceitando vírgula ou ponto."""
    return Decimal(valor.strip().replace(",", "."))

def _int_form(valor) -> int:
    """Converte texto de formulário em inteiro."""
    return int(valor.strip())

def _bool_form(valor) -> bool:
    """Converte texto de formulário em booleano (1/true/on/sim/yes -> True)."""
    return valor.strip().lower() in {"1", "true", "on", "sim", "yes"}


def _mapa_imagens(nome_json: str) -> dict:
    """Carrega docs/<nome_json> (registro de imagens), tolerando ausência.

    Args:
        nome_json (str): nome do arquivo em docs/ (ex.: "imagens-menu.json").

    Returns:
        dict: dicionário slug -> metadados da imagem (vazio se o arquivo não
            existir ou estiver corrompido).
    """
    import json
    import os
    from flask import current_app

    caminho = os.path.join(current_app.root_path, "docs", nome_json)
    try:
        with open(caminho, encoding="utf-8") as arq:
            return json.load(arq)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def _imagem_rel(mapa: dict, slug: str | None) -> str | None:
    """Resolve o caminho relativo a static/ da imagem de um slug.

    Lê o campo 'arquivo' do registro (ex.: 'static/images/menu/feijoada.jpg') e
    remove o prefixo 'static/' para uso com url_for('static', filename=...),
    exatamente como fazem as páginas do cliente.

    Args:
        mapa (dict): dicionário de imagens (de _mapa_imagens).
        slug (str | None): slug da imagem.

    Returns:
        str | None: caminho relativo (ex.: 'images/menu/feijoada.jpg') ou None.
    """
    if not slug:
        return None
    arquivo = (mapa.get(slug) or {}).get("arquivo")
    if arquivo and arquivo.startswith("static/"):
        return arquivo[len("static/"):]
    return arquivo

# ============================== routes ==============================

from . import admin_servicos, admin_pratocardapio, admin_ingredientefichalote, admin_funcionarios, admin_bebidas, admin_lote, admin_logs, admin_pedidos

