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

from controller.admin import admin_servicos  # noqa: E402,F401
from controller.admin import admin_pratocardapio  # noqa: E402,F401
from controller.admin import admin_ingredientefichalote  # noqa: E402,F401
from controller.admin import admin_funcionarios  # noqa: E402,F401
from controller.admin import admin_bebidas  # noqa: E402,F401
from controller.admin import admin_lote  # noqa: E402,F401
from controller.admin import admin_logs  # noqa: E402,F401

