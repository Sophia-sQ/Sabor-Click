from flask import Blueprint, redirect, url_for
from decimal import Decimal

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")

# ========================== funções internas ==========================
def _retorno():
    return redirect(url_for("admin.pagina_servicos"))

def _decimal_form(valor):
    """Converte decimal aceitando vírgula ou ponto."""
    return Decimal(valor.strip().replace(",", "."))

def _int_form(valor):
    return int(valor.strip())

def _bool_form(valor):
    return valor.strip().lower() in {"1", "true", "on", "sim", "yes"}

# ============================== routes ==============================

from admin import admin_servicos, admin_pratocardapio, admin_ingredientefichalote, admin_funcionarios, admin_bebidas