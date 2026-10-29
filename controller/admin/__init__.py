from decimal import Decimal

from flask import Blueprint, redirect, url_for

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

from . import (
    admin_bebidas,  # noqa: F401
    admin_funcionarios,  # noqa: F401
    admin_ingredientefichalote,  # noqa: F401
    admin_logs,  # noqa: F401
    admin_lote,  # noqa: F401
    admin_pratocardapio,  # noqa: F401
    admin_servicos,  # noqa: F401
)

