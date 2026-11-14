"""Rotas administrativas de gerenciamento de bebidas."""

from . import admin_bp, _retorno, _int_form, _decimal_form, _mapa_imagens, _imagem_rel

from flask import request, flash, redirect, render_template, url_for
from sqlalchemy.exc import SQLAlchemyError

from decimal import InvalidOperation

from services import imagem_bebida

from model.pedido_model import (
    # Bebida
    criar_bebida, buscar_bebida_por_id, atualizar_bebida, deletar_bebida,
    desativar_bebida, listar_bebidas_ativas,
)
from model.ficha_model import (
    # Ficha técnica da bebida (uma linha por par bebida-ingrediente)
    criar_ficha_tecnica_bebida, buscar_ficha_tecnica_bebida,
    atualizar_ficha_tecnica_bebida, deletar_ficha_tecnica_bebida,
    volume_ml_bebida,
)

# Dois tipos de bebida exibidos no catálogo (mesmo esquema da prévia).
_OPCOES_BEBIDA = [("Sem álcool", "Sem álcool"), ("Com álcool", "Com álcool")]
_CATEGORIAS_VALIDAS = {valor for valor, _ in _OPCOES_BEBIDA}


# ===================== CATÁLOGO DE BEBIDAS (página real) =====================

def _categoria_bebida(bebida) -> str:
    """Deriva a categoria de exibição ('Com álcool'/'Sem álcool') de uma bebida.

    Não há coluna de categoria no banco; reutiliza a mesma heurística das páginas
    do cliente (bebidas alcoólicas conhecidas -> 'Com álcool').
    """
    import unicodedata

    nome = "".join(
        c for c in unicodedata.normalize("NFD", (bebida.nome or "").replace("_", " "))
        if unicodedata.category(c) != "Mn"
    ).lower().strip()
    return "Com álcool" if nome in {"gin", "uisque de centeio rye"} else "Sem álcool"


def _itens_bebida(mapa_imagens: dict) -> list:
    """Monta a lista de bebidas (todas) para o catálogo admin."""
    itens = []
    for bebida in listar_bebidas_ativas() or []:
        itens.append({
            "id": bebida.id_bebida,
            "nome": bebida.nome,
            "descricao": bebida.descricao,
            "categoria": _categoria_bebida(bebida),
            "preco": float(bebida.valor_unitario) if bebida.valor_unitario is not None else None,
            "imagem": _imagem_rel(mapa_imagens, bebida.imagem_slug),
            "volume_ml": volume_ml_bebida(bebida.id_bebida),
            "ativo": bebida.ativo,
        })
    return itens


@admin_bp.get("/bebidas")
def catalogo_bebidas():
    """Renderiza a página real de catálogo de bebidas (CMS)."""
    mapa = _mapa_imagens("imagens-bebidas.json")
    itens = _itens_bebida(mapa)

    editar = request.args.get("editar", "")
    atual = None
    valores = {}
    if editar:
        atual = next((i for i in itens if str(i["id"]) == str(editar)), None)
        if atual:
            valores = dict(atual)

    return render_template(
        "catalogo_admin.html",
        tipo="bebidas",
        itens=itens,
        opcoes=_OPCOES_BEBIDA,
        servicos_catalogo={},
        atual=atual,
        valores=valores,
        gerenciar=request.args.get("gerenciar") == "1",
    )


# ========================= BEBIDA =========================

@admin_bp.post("/servicos/bebidas/criar")
def criar_bebida_route():
    """Cria uma bebida a partir do formulário, com upload de imagem opcional.

    Returns:
        Response: redirecionamento para o catálogo de bebidas.
    """
    voltar = redirect(url_for("admin.catalogo_bebidas", gerenciar=1))

    nome = request.form.get("nome", "").strip()
    descricao = request.form.get("descricao", "").strip()
    valor_texto = request.form.get("valor_unitario", "").strip()

    if not nome or not descricao or not valor_texto:
        flash("Preencha nome, descrição e valor unitário.", "danger")
        return voltar
    try:
        valor_unitario = _decimal_form(valor_texto)
    except InvalidOperation:
        flash("Valor unitário inválido.", "danger")
        return voltar
    if not valor_unitario.is_finite() or valor_unitario < 0:
        flash("O valor unitário deve ser válido e não negativo.", "danger")
        return voltar

    # Imagem opcional: salva o arquivo e sincroniza docs/imagens-bebidas.json.
    imagem_slug = None
    arquivo = request.files.get("imagem")
    if arquivo is not None and arquivo.filename:
        try:
            imagem_slug = imagem_bebida.salvar_imagem_bebida(arquivo, nome)
        except ValueError as erro:
            flash(f"Imagem inválida: {erro}", "danger")
            return voltar

    try:
        criar_bebida(nome, descricao, valor_unitario, imagem_slug=imagem_slug)
    except SQLAlchemyError:
        flash("Não foi possível criar a bebida.", "danger")
        return voltar

    flash("Bebida criada.", "success")
    return voltar


@admin_bp.post("/servicos/bebidas/atualizar/<int:id_bebida>")
def atualizar_bebida_route(id_bebida):
    """Atualiza uma bebida (com upload opcional de nova imagem).

    Args:
        id_bebida (int): identificador da bebida.

    Returns:
        Response: redirecionamento para o catálogo de bebidas.
    """
    voltar = redirect(url_for("admin.catalogo_bebidas", gerenciar=1))

    bebida = buscar_bebida_por_id(id_bebida)
    if bebida is None:
        flash("Bebida não encontrada.", "danger")
        return voltar

    nome = request.form.get("nome", "").strip()
    descricao = request.form.get("descricao", "").strip()
    valor_texto = request.form.get("valor_unitario", "").strip()

    if not nome or not descricao or not valor_texto:
        flash("Preencha todos os campos da bebida.", "danger")
        return voltar
    try:
        valor_unitario = _decimal_form(valor_texto)
    except InvalidOperation:
        flash("Valor unitário inválido.", "danger")
        return voltar
    if not valor_unitario.is_finite() or valor_unitario < 0:
        flash("O valor unitário deve ser válido e não negativo.", "danger")
        return voltar

    imagem_slug = None
    arquivo = request.files.get("imagem")
    if arquivo is not None and arquivo.filename:
        try:
            imagem_slug = imagem_bebida.atualizar_imagem_bebida(
                arquivo, nome, bebida.imagem_slug)
        except ValueError as erro:
            flash(f"Imagem inválida: {erro}", "danger")
            return voltar

    try:
        sucesso = atualizar_bebida(id_bebida, nome=nome, descricao=descricao,
                                   valor_unitario=valor_unitario, imagem_slug=imagem_slug)
    except SQLAlchemyError:
        flash("Não foi possível atualizar a bebida.", "danger")
        return voltar

    flash("Bebida atualizada." if sucesso else "Bebida não encontrada.",
          "success" if sucesso else "danger")
    return voltar


@admin_bp.post("/servicos/bebidas/deletar/<int:id_bebida>")
def deletar_bebida_route(id_bebida):
    """Desativa (soft delete) uma bebida e esconde sua imagem do JSON.

    Não remove fisicamente o registro (pode estar referenciado por pedidos):
    marca ativo=False (some das listagens do cliente) e retira a imagem do
    docs/imagens-bebidas.json.

    Args:
        id_bebida (int): identificador da bebida.

    Returns:
        Response: redirecionamento para o catálogo de bebidas.
    """
    voltar = redirect(url_for("admin.catalogo_bebidas", gerenciar=1))

    bebida = buscar_bebida_por_id(id_bebida)
    if bebida is None:
        flash("Bebida não encontrada.", "danger")
        return voltar

    slug = bebida.imagem_slug
    if not desativar_bebida(id_bebida):
        flash("Bebida não encontrada.", "danger")
        return voltar

    if slug:
        imagem_bebida.remover_imagem_bebida(slug)

    flash("Bebida removida.", "success")
    return voltar


# ========================= FICHA TÉCNICA DA BEBIDA =========================
# Cada par (bebida, ingrediente) é uma linha na tabela ficha_tecnica_bebida.

@admin_bp.post("/servicos/ficha-tecnica-bebida/criar")
def criar_ficha_tecnica_bebida_route():
    """Adiciona um ingrediente à ficha técnica de uma bebida a partir do formulário.

    Returns:
        Response: redirecionamento para a página de serviços.
    """
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
    """Atualiza a quantidade necessária de um item da ficha técnica da bebida.

    Args:
        id_bebida (int): identificador da bebida.
        id_ingrediente (int): identificador do ingrediente.

    Returns:
        Response: redirecionamento para a página de serviços.
    """
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
    """Remove um ingrediente da ficha técnica de uma bebida.

    Args:
        id_bebida (int): identificador da bebida.
        id_ingrediente (int): identificador do ingrediente.

    Returns:
        Response: redirecionamento para a página de serviços.
    """
    try:
        sucesso = deletar_ficha_tecnica_bebida(id_bebida, id_ingrediente)
    except SQLAlchemyError:
        flash("Não foi possível remover o item da ficha técnica da bebida.", "danger")
        return _retorno()

    flash("Ingrediente removido da ficha técnica da bebida." if sucesso else "Item da ficha técnica não encontrado.",
          "success" if sucesso else "danger")
    return _retorno()
