from admin import admin_bp, _retorno, _int_form, _decimal_form

from flask import request, flash
from sqlalchemy.exc import SQLAlchemyError

from decimal import InvalidOperation

from model.ficha_model import (
    # Ingrediente
    criar_ingrediente, buscar_ingrediente_por_id, listar_ingredientes,
    atualizar_ingrediente, deletar_ingrediente,
    # Ficha técnica
    criar_ficha_tecnica, buscar_ficha_tecnica_item, listar_ficha_tecnica_por_prato,
    atualizar_ficha_tecnica, deletar_ficha_tecnica,
)

# ========================= INGREDIENTE =========================

@admin_bp.post("/servicos/ingredientes/criar")
def criar_ingrediente_route():
    nome = request.form.get("nome", "").strip()
    unidade = request.form.get("unidade", "").strip()
    qtd_texto = request.form.get("qtd", "0").strip()
    qtd_min_texto = request.form.get("qtd_min", "0").strip()

    if not nome or not unidade or not qtd_texto or not qtd_min_texto:
        flash("Preencha nome, unidade, quantidade e quantidade mínima.", "danger")
        return _retorno()
    try:
        qtd, qtd_min = _decimal_form(qtd_texto), _decimal_form(qtd_min_texto)
    except InvalidOperation:
        flash("Quantidade inválida.", "danger")
        return _retorno()
    if not qtd.is_finite() or not qtd_min.is_finite() or qtd < 0 or qtd_min < 0:
        flash("As quantidades devem ser válidas e não negativas.", "danger")
        return _retorno()

    if unidade == "kg":
        ...
    elif unidade == "L":
        ...

    try:
        criar_ingrediente(nome, unidade, qtd, qtd_min)
    except SQLAlchemyError:
        flash("Não foi possível criar o ingrediente.", "danger")
        return _retorno()

    flash("Ingrediente criado.", "success")
    return _retorno()

@admin_bp.post("/servicos/ingredientes/atualizar/<int:id_ingrediente>")
def atualizar_ingrediente_route(id_ingrediente):
    nome = request.form.get("nome", "").strip()
    unidade = request.form.get("unidade", "").strip()
    qtd_texto = request.form.get("qtd", "").strip()
    qtd_min_texto = request.form.get("qtd_min", "").strip()

    if not nome or not unidade or not qtd_texto or not qtd_min_texto:
        flash("Preencha todos os campos do ingrediente.", "danger")
        return _retorno()
    try:
        qtd, qtd_min = _decimal_form(qtd_texto), _decimal_form(qtd_min_texto)
    except InvalidOperation:
        flash("Quantidade inválida.", "danger")
        return _retorno()
    if not qtd.is_finite() or not qtd_min.is_finite() or qtd < 0 or qtd_min < 0:
        flash("As quantidades devem ser válidas e não negativas.", "danger")
        return _retorno()

    try:
        sucesso = atualizar_ingrediente(id_ingrediente, nome, unidade, qtd, qtd_min)
    except SQLAlchemyError:
        flash("Não foi possível atualizar o ingrediente.", "danger")
        return _retorno()

    flash("Ingrediente atualizado." if sucesso else "Ingrediente não encontrado.",
          "success" if sucesso else "danger")
    return _retorno()

@admin_bp.post("/servicos/ingredientes/deletar/<int:id_ingrediente>")
def deletar_ingrediente_route(id_ingrediente):
    try:
        sucesso = deletar_ingrediente(id_ingrediente)
    except SQLAlchemyError:
        flash("Não foi possível excluir o ingrediente. Verifique se ele está vinculado a fichas técnicas ou lotes.", "danger")
        return _retorno()

    flash("Ingrediente deletado." if sucesso else "Ingrediente não encontrado.",
          "success" if sucesso else "danger")
    return _retorno()

# ========================= FICHA TÉCNICA =========================

@admin_bp.post("/servicos/ficha-tecnica/criar")
def criar_ficha_tecnica_route():
    prato_texto = request.form.get("id_prato", "").strip()
    ingrediente_texto = request.form.get("id_ingrediente", "").strip()
    qtd_texto = request.form.get("qtd_necessaria", "").strip()

    if not prato_texto or not ingrediente_texto or not qtd_texto:
        flash("Informe prato, ingrediente e quantidade necessária.", "danger")
        return _retorno()
    try:
        id_prato = _int_form(prato_texto)
        id_ingrediente = _int_form(ingrediente_texto)
        qtd = _decimal_form(qtd_texto)
    except ValueError:
        flash("Os IDs devem ser números inteiros.", "danger")
        return _retorno()
    except InvalidOperation:
        flash("Quantidade necessária inválida.", "danger")
        return _retorno()
    if id_prato <= 0 or id_ingrediente <= 0 or not qtd.is_finite() or qtd <= 0:
        flash("IDs devem ser positivos e a quantidade necessária deve ser maior que zero.", "danger")
        return _retorno()

    try:
        criar_ficha_tecnica(id_prato, id_ingrediente, qtd)
    except SQLAlchemyError:
        flash("Não foi possível adicionar o ingrediente à ficha técnica. Verifique se os registros existem e se o vínculo já existe.", "danger")
        return _retorno()

    flash("Ingrediente adicionado à ficha técnica.", "success")
    return _retorno()

@admin_bp.post("/servicos/ficha-tecnica/atualizar/<int:id_prato>/<int:id_ingrediente>")
def atualizar_ficha_tecnica_route(id_prato, id_ingrediente):
    qtd_texto = request.form.get("qtd_necessaria", "").strip()
    if not qtd_texto:
        flash("Informe a quantidade necessária.", "danger")
        return _retorno()
    try:
        qtd = _decimal_form(qtd_texto)
    except InvalidOperation:
        flash("Quantidade necessária inválida.", "danger")
        return _retorno()
    if not qtd.is_finite() or qtd <= 0:
        flash("A quantidade necessária deve ser maior que zero.", "danger")
        return _retorno()

    try:
        sucesso = atualizar_ficha_tecnica(id_prato, id_ingrediente, qtd)
    except SQLAlchemyError:
        flash("Não foi possível atualizar a ficha técnica.", "danger")
        return _retorno()

    flash("Ficha técnica atualizada." if sucesso else "Item da ficha técnica não encontrado.",
          "success" if sucesso else "danger")
    return _retorno()

@admin_bp.post("/servicos/ficha-tecnica/deletar/<int:id_prato>/<int:id_ingrediente>")
def deletar_ficha_tecnica_route(id_prato, id_ingrediente):
    try:
        sucesso = deletar_ficha_tecnica(id_prato, id_ingrediente)
    except SQLAlchemyError:
        flash("Não foi possível remover o item da ficha técnica.", "danger")
        return _retorno()

    flash("Ingrediente removido da ficha técnica." if sucesso else "Item da ficha técnica não encontrado.",
          "success" if sucesso else "danger")
    return _retorno()
