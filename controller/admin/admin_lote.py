from datetime import date, datetime
from decimal import InvalidOperation

from . import _decimal_form, _int_form, _retorno, admin_bp
from flask import flash, request
from sqlalchemy.exc import SQLAlchemyError

from model.ficha_model import (
    atualizar_lote,
    criar_lote,
    deletar_lote,
)

# ========================= LOTE =========================
# Lote é sempre vinculado a um ingrediente.

@admin_bp.post("/servicos/lotes/criar")
def criar_lote_route():
    num_lote = request.form.get("num_lote", "").strip()
    marca = request.form.get("marca", "").strip()
    recebimento_texto = request.form.get("data_recebimento", "").strip()
    validade_texto = request.form.get("data_validade", "").strip()
    qtd_texto = request.form.get("qtd_inicial", "").strip()
    ingrediente_texto = request.form.get("id_ingrediente", "").strip()

    if not num_lote or not marca or not recebimento_texto or not qtd_texto or not ingrediente_texto:
        flash("Preencha número do lote, marca, recebimento, quantidade inicial e ingrediente.", "danger")
        return _retorno()
    try:
        data_recebimento = datetime.fromisoformat(recebimento_texto)
        qtd_inicial = _decimal_form(qtd_texto)
        id_ingrediente = _int_form(ingrediente_texto)
    except ValueError:
        flash("Data de recebimento, quantidade ou ID inválido.", "danger")
        return _retorno()
    except InvalidOperation:
        flash("Quantidade inicial inválida.", "danger")
        return _retorno()

    try:
        data_validade = date.fromisoformat(validade_texto) if validade_texto else None
    except ValueError:
        flash("Data de validade inválida.", "danger")
        return _retorno()

    if id_ingrediente <= 0 or not qtd_inicial.is_finite() or qtd_inicial < 0:
        flash("O ingrediente deve ser válido e a quantidade inicial não pode ser negativa.", "danger")
        return _retorno()

    try:
        criar_lote(
            num_lote=num_lote, marca=marca,
            data_recebimento=data_recebimento, data_validade=data_validade,
            qtd_inicial=qtd_inicial, id_ingrediente=id_ingrediente,
        )
    except SQLAlchemyError:
        flash("Não foi possível criar o lote. Verifique o ingrediente informado.", "danger")
        return _retorno()

    flash("Lote criado.", "success")
    return _retorno()

@admin_bp.post("/servicos/lotes/atualizar/<int:id_lote>")
def atualizar_lote_route(id_lote):
    num_lote = request.form.get("num_lote", "").strip()
    marca = request.form.get("marca", "").strip()
    recebimento_texto = request.form.get("data_recebimento", "").strip()
    validade_texto = request.form.get("data_validade", "").strip()
    qtd_texto = request.form.get("qtd_inicial", "").strip()
    ingrediente_texto = request.form.get("id_ingrediente", "").strip()

    if not num_lote or not marca or not recebimento_texto or not qtd_texto or not ingrediente_texto:
        flash("Preencha todos os campos obrigatórios do lote.", "danger")
        return _retorno()
    try:
        data_recebimento = datetime.fromisoformat(recebimento_texto)
        qtd_inicial = _decimal_form(qtd_texto)
        id_ingrediente = _int_form(ingrediente_texto)
        data_validade = date.fromisoformat(validade_texto) if validade_texto else None
    except ValueError:
        flash("Data, quantidade ou ID inválido.", "danger")
        return _retorno()
    except InvalidOperation:
        flash("Quantidade inicial inválida.", "danger")
        return _retorno()

    if id_ingrediente <= 0 or not qtd_inicial.is_finite() or qtd_inicial < 0:
        flash("O ingrediente deve ser válido e a quantidade inicial não pode ser negativa.", "danger")
        return _retorno()

    try:
        sucesso = atualizar_lote(
            id_lote=id_lote, num_lote=num_lote, marca=marca,
            data_recebimento=data_recebimento, data_validade=data_validade,
            qtd_inicial=qtd_inicial, id_ingrediente=id_ingrediente,
        )
    except SQLAlchemyError:
        flash("Não foi possível atualizar o lote.", "danger")
        return _retorno()

    flash("Lote atualizado." if sucesso else "Lote não encontrado.",
          "success" if sucesso else "danger")
    return _retorno()

@admin_bp.post("/servicos/lotes/deletar/<int:id_lote>")
def deletar_lote_route(id_lote):
    try:
        sucesso = deletar_lote(id_lote)
    except SQLAlchemyError:
        flash("Não foi possível excluir o lote.", "danger")
        return _retorno()

    flash("Lote deletado." if sucesso else "Lote não encontrado.",
          "success" if sucesso else "danger")
    return _retorno()
