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

# ============================== routes ==============================

from . import admin_servicos, admin_pratocardapio, admin_ingredientefichalote, admin_funcionarios, admin_bebidas, admin_lote, admin_logs

