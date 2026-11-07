"""Rotas administrativas de consulta e gerenciamento dos logs de atividade."""

from . import admin_bp

from flask import render_template, request, flash, redirect, url_for, Response
from sqlalchemy.exc import SQLAlchemyError

from model.usuario_model import listar_logs, buscar_log_por_id, deletar_log

# ========================= LOG DE ATIVIDADE =========================
# A trilha de auditoria é somente leitura (gerada automaticamente pelo
# sistema via registrar_log). O admin pode consultar e excluir registros,
# mas não criar/editar manualmente.

def _retorno_logs() -> Response:
    """Redireciona para a página de logs do admin."""
    return redirect(url_for("admin.pagina_logs"))

@admin_bp.get("/logs")
def pagina_logs():
    """Lista os registros de atividade, com filtro opcional por ação (query 'busca')."""
    busca = request.args.get("busca", "").strip()
    logs = listar_logs(busca)
    return render_template("log_atividade.html", logs=logs, busca=busca)  # TODO: confirmar nome do template

@admin_bp.get("/logs/<int:id_atividade>")
def detalhe_log(id_atividade):
    """Exibe os detalhes de um registro de atividade.

    Args:
        id_atividade (int): identificador do registro.

    Returns:
        Response | str: redirecionamento se o registro não existir; caso
        contrário, o template de detalhe renderizado.
    """
    log = buscar_log_por_id(id_atividade)
    if not log:
        flash("Registro de atividade não encontrado.", "danger")
        return _retorno_logs()
    return render_template("log_atividade_detalhe.html", log=log)  # TODO: confirmar nome do template

@admin_bp.post("/logs/deletar/<int:id_atividade>")
def deletar_log_route(id_atividade):
    """Remove um registro de atividade da trilha de auditoria.

    Args:
        id_atividade (int): identificador do registro.

    Returns:
        Response: redirecionamento para a página de logs.
    """
    
    """Remove um registro de atividade da trilha de auditoria."""
    try:
        sucesso = deletar_log(id_atividade)
    except SQLAlchemyError:
        flash("Não foi possível excluir o registro de atividade.", "danger")
        return _retorno_logs()

    flash("Registro de atividade deletado." if sucesso else "Registro de atividade não encontrado.",
          "success" if sucesso else "danger")
    return _retorno_logs()
