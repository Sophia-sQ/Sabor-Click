from decimal import InvalidOperation

from . import _decimal_form, _int_form, _retorno, admin_bp
from flask import flash, request
from sqlalchemy.exc import SQLAlchemyError

from model.ficha_model import (
    atualizar_ficha_tecnica_bebida,
    criar_ficha_tecnica_bebida,
    deletar_ficha_tecnica_bebida,
)
from model.pedido_model import (
    atualizar_bebida,
    criar_bebida,
    deletar_bebida,
)

# ========================= BEBIDA =========================

@admin_bp.post("/servicos/bebidas/criar")
def criar_bebida_route():
    nome = request.form.get("nome", "").strip()
    descricao = request.form.get("descricao", "").strip()
    valor_texto = request.form.get("valor_unitario", "").strip()

    if not nome or not descricao or not valor_texto:
        flash("Preencha nome, descrição e valor unitário.", "danger")
        return _retorno()
    try:
        valor_unitario = _decimal_form(valor_texto)
    except InvalidOperation:
        flash("Valor unitário inválido.", "danger")
        return _retorno()
    if not valor_unitario.is_finite() or valor_unitario < 0:
        flash("O valor unitário deve ser válido e não negativo.", "danger")
        return _retorno()

    try:
        criar_bebida(nome, descricao, valor_unitario)
    except SQLAlchemyError:
        flash("Não foi possível criar a bebida.", "danger")
        return _retorno()

    flash("Bebida criada.", "success")
    return _retorno()


@admin_bp.post("/servicos/bebidas/atualizar/<int:id_bebida>")
def atualizar_bebida_route(id_bebida):
    nome = request.form.get("nome", "").strip()
    descricao = request.form.get("descricao", "").strip()
    valor_texto = request.form.get("valor_unitario", "").strip()

    if not nome or not descricao or not valor_texto:
        flash("Preencha todos os campos da bebida.", "danger")
        return _retorno()
    try:
        valor_unitario = _decimal_form(valor_texto)
    except InvalidOperation:
        flash("Valor unitário inválido.", "danger")
        return _retorno()
    if not valor_unitario.is_finite() or valor_unitario < 0:
        flash("O valor unitário deve ser válido e não negativo.", "danger")
        return _retorno()

    try:
        sucesso = atualizar_bebida(id_bebida, nome=nome, descricao=descricao, valor_unitario=valor_unitario)
    except SQLAlchemyError:
        flash("Não foi possível atualizar a bebida.", "danger")
        return _retorno()

    flash("Bebida atualizada." if sucesso else "Bebida não encontrada.",
          "success" if sucesso else "danger")
    return _retorno()


@admin_bp.post("/servicos/bebidas/deletar/<int:id_bebida>")
def deletar_bebida_route(id_bebida):
    try:
        sucesso = deletar_bebida(id_bebida)
    except SQLAlchemyError:
        flash("Não foi possível excluir a bebida. Verifique se ela está vinculada a fichas técnicas, cardápios ou pedidos.", "danger")
        return _retorno()

    flash("Bebida deletada." if sucesso else "Bebida não encontrada.",
          "success" if sucesso else "danger")
    return _retorno()


# ========================= FICHA TÉCNICA DA BEBIDA =========================
# Cada par (bebida, ingrediente) é uma linha na tabela ficha_tecnica_bebida.

@admin_bp.post("/servicos/ficha-tecnica-bebida/criar")
def criar_ficha_tecnica_bebida_route():
    bebida_texto = request.form.get("id_bebida", "").strip()
    ingrediente_texto = request.form.get("id_ingrediente", "").strip()
    qtd_texto = request.form.get("qtd_necessaria", "").strip()

    if not bebida_texto or not ingrediente_texto or not qtd_texto:
        flash("Informe bebida, ingrediente e quantidade necessária.", "danger")
        return _retorno()
    try:
        id_bebida = _int_form(bebida_texto)
        id_ingrediente = _int_form(ingrediente_texto)
        qtd = _int_form(qtd_texto)
    except ValueError:
        flash("Os IDs e a quantidade necessária devem ser números inteiros.", "danger")
        return _retorno()
    if id_bebida <= 0 or id_ingrediente <= 0 or qtd <= 0:
        flash("IDs devem ser positivos e a quantidade necessária deve ser maior que zero.", "danger")
        return _retorno()

    try:
        criar_ficha_tecnica_bebida(id_bebida, id_ingrediente, qtd)
    except SQLAlchemyError:
        flash("Não foi possível adicionar o ingrediente à ficha técnica da bebida. Verifique se os registros existem e se o vínculo já existe.", "danger")
        return _retorno()

    flash("Ingrediente adicionado à ficha técnica da bebida.", "success")
    return _retorno()


@admin_bp.post("/servicos/ficha-tecnica-bebida/atualizar/<int:id_bebida>/<int:id_ingrediente>")
def atualizar_ficha_tecnica_bebida_route(id_bebida, id_ingrediente):
    qtd_texto = request.form.get("qtd_necessaria", "").strip()
    if not qtd_texto:
        flash("Informe a quantidade necessária.", "danger")
        return _retorno()
    try:
        qtd = _int_form(qtd_texto)
    except ValueError:
        flash("A quantidade necessária deve ser um número inteiro.", "danger")
        return _retorno()
    if qtd <= 0:
        flash("A quantidade necessária deve ser maior que zero.", "danger")
        return _retorno()

    try:
        sucesso = atualizar_ficha_tecnica_bebida(id_bebida, id_ingrediente, qtd)
    except SQLAlchemyError:
        flash("Não foi possível atualizar a ficha técnica da bebida.", "danger")
        return _retorno()

    flash("Ficha técnica da bebida atualizada." if sucesso else "Item da ficha técnica não encontrado.",
          "success" if sucesso else "danger")
    return _retorno()


@admin_bp.post("/servicos/ficha-tecnica-bebida/deletar/<int:id_bebida>/<int:id_ingrediente>")
def deletar_ficha_tecnica_bebida_route(id_bebida, id_ingrediente):
    try:
        sucesso = deletar_ficha_tecnica_bebida(id_bebida, id_ingrediente)
    except SQLAlchemyError:
        flash("Não foi possível remover o item da ficha técnica da bebida.", "danger")
        return _retorno()

    flash("Ingrediente removido da ficha técnica da bebida." if sucesso else "Item da ficha técnica não encontrado.",
          "success" if sucesso else "danger")
    return _retorno()
