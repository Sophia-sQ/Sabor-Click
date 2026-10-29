from decimal import Decimal, InvalidOperation

from . import _bool_form, _int_form, _retorno, admin_bp
from flask import flash, request
from sqlalchemy.exc import SQLAlchemyError

from model.ficha_model import (
    # Prato x cardápio
    associar_prato_cardapio,
    atualizar_prato,
    atualizar_prato_cardapio,
    criar_prato,
    deletar_prato,
    deletar_prato_cardapio,
)
from model.servico_model import atualizar_cardapio, criar_cardapio, deletar_cardapio


# ========================= CRIAR CARDÁPIO =========================
@admin_bp.post("/servicos/criar_cardapio")
def c_cardapio():
    nome = request.form.get("nome", "").strip()
    descricao = request.form.get("descricao", "").strip()
    preco_texto = request.form.get("preco_base", "").strip()

    if not nome or not descricao or not preco_texto:
        flash("Preencha todos os campos.", "danger")
        return _retorno()

    try:
        preco_base = Decimal(preco_texto.replace(",", "."))
    except InvalidOperation:
        flash("Preço inválido.", "danger")
        return _retorno()

    if not preco_base.is_finite() or preco_base < 0:
        flash("O preço deve ser válido e não negativo.", "danger")
        return _retorno()

    criar_cardapio(nome=nome, descricao=descricao, preco_base=preco_base)

    flash("Cardápio criado.", "success")
    return _retorno()

# ========================= ATUALIZAR CARDÁPIO =========================
@admin_bp.post("/servicos/atualizar_cardapio/<int:id_cardapio>")
def at_cardapio(id_cardapio):
    nome = request.form.get("nome", "").strip()
    descricao = request.form.get("descricao", "").strip()
    preco_texto = request.form.get("preco_base", "").strip()

    if not nome or not descricao or not preco_texto:
        flash("Preencha todos os campos.", "danger")
        return _retorno()

    try:
        preco_base = Decimal(preco_texto.replace(",", "."))
    except InvalidOperation:
        flash("Preço inválido.", "danger")
        return _retorno()

    if not preco_base.is_finite() or preco_base < 0:
        flash("O preço deve ser válido e não negativo.", "danger")
        return _retorno()

    sucesso = atualizar_cardapio(id_cardapio=id_cardapio, nome=nome, descricao=descricao, preco_base=preco_base)

    if not sucesso:
        flash("Cardápio não encontrado.", "danger")
        return _retorno()

    flash("Cardápio atualizado.", "success")
    return _retorno()

# ========================= DELETAR CARDÁPIO =========================
@admin_bp.route("/deletar_cardapio/<int:id_cardapio>", methods=("POST",))
def del_cardapio(id_cardapio):
    sucesso = deletar_cardapio(id_cardapio=id_cardapio)

    if not sucesso:
        flash("Cardápio não encontrado.", "danger")

    flash("Cardápio deletado.", "success")
    return _retorno()

# ========================= PRATO =========================

@admin_bp.post("/servicos/pratos/criar")
def criar_prato_route():
    nome = request.form.get("nome", "").strip()
    descricao = request.form.get("descricao", "").strip()
    tipo_prato = request.form.get("tipo_prato", "").strip()
    tempo_texto = request.form.get("tempo_preparo", "").strip()
    requer_pre_preparo = _bool_form(request.form.get("requer_pre_preparo", ""))

    tipos_validos = {"entrada", "acompanhamento", "prato principal", "sobremesa"}
    if not nome or not descricao or not tipo_prato or not tempo_texto:
        flash("Preencha todos os campos obrigatórios do prato.", "danger")
        return _retorno()
    if tipo_prato not in tipos_validos:
        flash("Tipo de prato inválido.", "danger")
        return _retorno()

    try:
        tempo_preparo = _int_form(tempo_texto)
    except ValueError:
        flash("O tempo de preparo deve ser um número inteiro.", "danger")
        return _retorno()

    if tempo_preparo < 0:
        flash("O tempo de preparo não pode ser negativo.", "danger")
        return _retorno()

    try:
        criar_prato(nome, descricao, tipo_prato, tempo_preparo, requer_pre_preparo)
    except SQLAlchemyError:
        flash("Não foi possível criar o prato.", "danger")
        return _retorno()

    flash("Prato criado.", "success")
    return _retorno()


@admin_bp.post("/servicos/pratos/atualizar/<int:id_prato>")
def atualizar_prato_route(id_prato):
    nome = request.form.get("nome", "").strip()
    descricao = request.form.get("descricao", "").strip()
    tipo_prato = request.form.get("tipo_prato", "").strip()
    tempo_texto = request.form.get("tempo_preparo", "").strip()
    requer_pre_preparo = _bool_form(request.form.get("requer_pre_preparo", ""))

    tipos_validos = {"entrada", "acompanhamento", "prato principal", "sobremesa"}
    if not nome or not descricao or not tipo_prato or not tempo_texto:
        flash("Preencha todos os campos obrigatórios do prato.", "danger")
        return _retorno()
    if tipo_prato not in tipos_validos:
        flash("Tipo de prato inválido.", "danger")
        return _retorno()

    try:
        tempo_preparo = _int_form(tempo_texto)
    except ValueError:
        flash("O tempo de preparo deve ser um número inteiro.", "danger")
        return _retorno()

    if tempo_preparo < 0:
        flash("O tempo de preparo não pode ser negativo.", "danger")
        return _retorno()

    try:
        sucesso = atualizar_prato(
            id_prato=id_prato, nome=nome, descricao=descricao,
            tipo_prato=tipo_prato, tempo_preparo=tempo_preparo,
            requer_pre_preparo=requer_pre_preparo,
        )
    except SQLAlchemyError:
        flash("Não foi possível atualizar o prato.", "danger")
        return _retorno()

    flash("Prato atualizado." if sucesso else "Prato não encontrado.",
          "success" if sucesso else "danger")
    return _retorno()


@admin_bp.post("/servicos/pratos/deletar/<int:id_prato>")
def deletar_prato_route(id_prato):
    try:
        sucesso = deletar_prato(id_prato)
    except SQLAlchemyError:
        flash("Não foi possível excluir o prato. Verifique se ele está vinculado a outros registros.", "danger")
        return _retorno()

    flash("Prato deletado." if sucesso else "Prato não encontrado.",
          "success" if sucesso else "danger")
    return _retorno()


# ========================= PRATO-CARDÁPIO =========================

@admin_bp.post("/servicos/prato-cardapio/criar")
def criar_prato_cardapio_route():
    prato_texto = request.form.get("id_prato", "").strip()
    cardapio_texto = request.form.get("id_cardapio", "").strip()
    qtd_texto = request.form.get("qtd", "").strip()
    descricao = request.form.get("descricao", "").strip() or None

    if not prato_texto or not cardapio_texto or not qtd_texto:
        flash("Informe prato, cardápio e quantidade.", "danger")
        return _retorno()
    try:
        id_prato, id_cardapio, qtd = _int_form(prato_texto), _int_form(cardapio_texto), _int_form(qtd_texto)
    except ValueError:
        flash("IDs e quantidade devem ser números inteiros.", "danger")
        return _retorno()
    if id_prato <= 0 or id_cardapio <= 0 or qtd <= 0:
        flash("IDs e quantidade devem ser positivos.", "danger")
        return _retorno()

    try:
        associar_prato_cardapio(id_prato, id_cardapio, qtd, descricao)
    except SQLAlchemyError:
        flash("Não foi possível associar o prato ao cardápio. Verifique se os registros existem e se a associação já não existe.", "danger")
        return _retorno()

    flash("Prato associado ao cardápio.", "success")
    return _retorno()

# essas rotas com 2 ids, ou você pega eles com a função de buscar por nome ou faz um card pronto já com os ids
@admin_bp.post("/servicos/prato-cardapio/atualizar/<int:id_prato>/<int:id_cardapio>")
def atualizar_prato_cardapio_route(id_prato, id_cardapio):
    qtd_texto = request.form.get("qtd", "").strip()
    descricao = request.form.get("descricao", "").strip()

    if not qtd_texto:
        flash("Informe a quantidade.", "danger")
        return _retorno()
    try:
        qtd = _int_form(qtd_texto)
    except ValueError:
        flash("A quantidade deve ser um número inteiro.", "danger")
        return _retorno()
    if qtd <= 0:
        flash("A quantidade deve ser positiva.", "danger")
        return _retorno()

    try:
        sucesso = atualizar_prato_cardapio(
            id_prato=id_prato, id_cardapio=id_cardapio,
            qtd=qtd, descricao=descricao or None,
        )
    except SQLAlchemyError:
        flash("Não foi possível atualizar a associação.", "danger")
        return _retorno()

    flash("Associação atualizada." if sucesso else "Associação não encontrada.",
          "success" if sucesso else "danger")
    return _retorno()


@admin_bp.post("/servicos/prato-cardapio/deletar/<int:id_prato>/<int:id_cardapio>")
def deletar_prato_cardapio_route(id_prato, id_cardapio):
    try:
        sucesso = deletar_prato_cardapio(id_prato, id_cardapio)
    except SQLAlchemyError:
        flash("Não foi possível remover a associação.", "danger")
        return _retorno()

    flash("Associação removida." if sucesso else "Associação não encontrada.",
          "success" if sucesso else "danger")
    return _retorno()
