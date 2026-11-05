from controller.admin import admin_bp, _retorno

from flask import render_template, flash, request

from sqlalchemy.exc import SQLAlchemyError

from model.servico_model import (
    criar_servico,
    atualizar_servico,
    deletar_servico,
    buscar_servicos,
    associar_servico_cardapio,
    desassociar_servico_cardapio,
)
from model.pedido_model import buscar_bebidas
from model.ficha_model import (
    buscar_pratos,
    buscar_ingredientes,
    buscar_lotes,
    listar_ingredientes_abaixo_minimo,
)
# ============================== Servicos =============================

@admin_bp.get("/servicos")
def pagina_servicos():
    """Página de serviços com busca unificada.

    O parâmetro de query ``busca`` filtra, por correspondência parcial, todas as
    entidades exibidas nesta página: serviços, bebidas, pratos, ingredientes e
    lotes. Sem ``busca``, lista tudo. A página também recebe a lista de
    ingredientes abaixo do estoque mínimo, para o alerta de reposição.
    """
    busca = request.args.get("busca", "").strip()

    servicos = buscar_servicos(busca)
    bebidas = buscar_bebidas(busca)
    pratos = buscar_pratos(busca)
    ingredientes = buscar_ingredientes(busca)
    lotes = buscar_lotes(busca)
    ingredientes_repor = listar_ingredientes_abaixo_minimo()

    return render_template(
        "estoque.html",
        busca=busca,
        servicos=servicos,
        bebidas=bebidas,
        pratos=pratos,
        ingredientes=ingredientes,
        lotes=lotes,
        ingredientes_repor=ingredientes_repor,
    )


# ========================= CRIAR SERVIÇO =========================
@admin_bp.post("/servicos/criar_servico")
def c_servico():
    """Cadastra um novo serviço (ex.: Chef em casa, Buffet, Bar)."""
    nome = request.form.get("nome", "").strip()
    descricao = request.form.get("descricao", "").strip()

    if not nome or not descricao:
        flash("Preencha nome e descrição do serviço.", "danger")
        return _retorno()

    try:
        criar_servico(nome, descricao)
    except SQLAlchemyError:
        flash("Não foi possível criar o serviço. Verifique se o nome já existe.", "danger")
        return _retorno()

    flash("Serviço criado.", "success")
    return _retorno()


# ========================= ATUALIZAR SERVIÇO =========================
@admin_bp.post("/servicos/atualizar_servico/<int:id_servico>")
def at_servico(id_servico: int):
    """Atualiza o nome e a descrição de um serviço."""
    nome = request.form.get("nome", "").strip()
    descricao = request.form.get("descricao", "").strip()

    if not nome or not descricao:
        flash("Preencha nome e descrição do serviço.", "danger")
        return _retorno()

    sucesso = atualizar_servico(
        id_servico=id_servico,
        nome=nome,
        descricao=descricao,
    )

    if not sucesso:
        flash("Falha ao tentar atualizar o serviço", "danger")
        return _retorno()

    flash("Serviço atualizado.", "success")
    return _retorno()

# ========================= DELETAR SERVIÇO =========================
@admin_bp.post("/servicos/deletar_servico/<int:id_servico>")
def del_servico(id_servico: int):
    """Remove um serviço."""
    sucesso = deletar_servico(id_servico=id_servico)

    if not sucesso:
        flash("Falha ao tentar deletar o serviço", "danger")
        return _retorno()

    flash("Serviço deletado.", "success")
    return _retorno()


# ================= ASSOCIAÇÃO SERVIÇO / CARDÁPIO =================
@admin_bp.post("/servicos/servico-cardapio/criar")
def associar_servico_cardapio_route():
    """Associa um cardápio a um serviço."""
    id_servico = request.form.get("id_servico", type=int)
    id_cardapio = request.form.get("id_cardapio", type=int)

    if not id_servico or not id_cardapio:
        flash("Informe o serviço e o cardápio.", "danger")
        return _retorno()

    try:
        criada = associar_servico_cardapio(id_servico, id_cardapio)
    except SQLAlchemyError:
        flash("Não foi possível associar. Verifique se os registros existem.", "danger")
        return _retorno()

    flash("Cardápio associado ao serviço." if criada else "Essa associação já existe.",
          "success" if criada else "danger")
    return _retorno()


@admin_bp.post("/servicos/servico-cardapio/deletar/<int:id_servico>/<int:id_cardapio>")
def desassociar_servico_cardapio_route(id_servico: int, id_cardapio: int):
    """Remove a associação entre um serviço e um cardápio."""
    try:
        removida = desassociar_servico_cardapio(id_servico, id_cardapio)
    except SQLAlchemyError:
        flash("Não foi possível remover a associação.", "danger")
        return _retorno()

    flash("Associação removida." if removida else "Associação não encontrada.",
          "success" if removida else "danger")
    return _retorno()
