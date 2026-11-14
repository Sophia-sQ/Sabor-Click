"""Rotas administrativas de bancadas e suas associações a serviços.

Espelha o catálogo de cardápios (controller/admin/admin_pratocardapio.py), mas
SEM imagem e SEM preço: bancadas têm apenas nome e descrição, e se associam a
serviços pela tabela ServicoBancada via checkboxes de slug.
"""

from . import admin_bp

from flask import request, flash, redirect, render_template, url_for

from sqlalchemy.exc import SQLAlchemyError

from model.servico_model import (
    criar_bancada, atualizar_bancada, desativar_bancada,
    listar_bancadas_ativas, buscar_bancada_por_id,
    listar_servicos, buscar_servico_por_slug,
    associar_servico_bancada, desassociar_servico_bancada,
    Servico, ServicoBancada, Bancada,
)
from database import db


# ===================== CATÁLOGO DE BANCADAS (página real) =====================

def _servicos_catalogo() -> dict:
    """Mapeia slug -> (nome, None) a partir dos serviços reais do banco.

    Usado para montar as checkboxes do formulário de bancada (associação a
    serviços) e para exibir os serviços associados a cada bancada na listagem.
    Espelha _servicos_catalogo do cardápio, mantendo o formato de tupla que o
    template espera (slug -> (nome, categoria)); categoria é None (não há
    categoria por serviço no banco).

    Returns:
        dict: {slug: (nome, None)} ordenado pelos serviços cadastrados.
    """
    return {s.slug: (s.nome, None) for s in (listar_servicos() or [])}


def _slugs_servicos_da_bancada(id_bancada: int) -> list:
    """Lista os slugs dos serviços atualmente associados a uma bancada."""
    slugs = db.session.execute(
        db.select(Servico.slug)
        .join(ServicoBancada, Servico.id_servico == ServicoBancada.id_servico)
        .where(ServicoBancada.id_bancada == id_bancada),
    ).scalars().all()
    return list(slugs)


def _itens_bancada() -> list:
    """Monta a lista de bancadas ATIVAS para o catálogo admin (desativadas são ocultadas)."""
    itens = []
    for bancada in listar_bancadas_ativas() or []:
        itens.append({
            "id": bancada.id_bancada,
            "nome": bancada.nome,
            "descricao": bancada.descricao,
            "servicos": _slugs_servicos_da_bancada(bancada.id_bancada),
            "ativo": bancada.ativo,
        })
    return itens


@admin_bp.get("/bancadas")
def catalogo_bancadas():
    """Renderiza a página real de catálogo de bancadas (CMS).

    Lista apenas as bancadas ATIVAS (via listar_bancadas_ativas); bancadas
    desativadas (soft delete) não aparecem. Suporta ?editar=<id> (abre o
    formulário já preenchido) e ?gerenciar=1 (abre a seção de gerenciamento),
    como nas demais páginas. NÃO há campo de imagem (bancadas não têm imagem).
    """
    itens = _itens_bancada()
    servicos_catalogo = _servicos_catalogo()

    editar = request.args.get("editar", "")
    atual = None
    valores = {}
    if editar:
        atual = next((i for i in itens if str(i["id"]) == str(editar)), None)
        if atual:
            valores = dict(atual)

    return render_template(
        "catalogo_bancadas.html",
        itens=itens,
        servicos_catalogo=servicos_catalogo,
        atual=atual,
        valores=valores,
        gerenciar=request.args.get("gerenciar") == "1",
    )


def _sincronizar_servicos_da_bancada(id_bancada: int, slugs_enviados: list) -> None:
    """Sincroniza ServicoBancada com os slugs marcados (associa/desassocia).

    A partir dos slugs de serviço marcados nos checkboxes, associa os novos
    (associar_servico_bancada) e desassocia os retirados
    (desassociar_servico_bancada), comparando com as associações atuais da
    bancada. Espelha _sincronizar_servicos do cardápio.

    Atenção à ordem dos parâmetros no model:
    associar_servico_bancada(id_servico, id_bancada, id_usuario) e
    desassociar_servico_bancada(id_servico, id_bancada, id_usuario). Passamos
    id_usuario=None (o log pega o usuário da sessão).

    Apenas slugs válidos (correspondentes a Servico.slug reais) são considerados;
    slugs desconhecidos são ignorados silenciosamente.
    """
    validos = {}
    for slug in dict.fromkeys(slugs_enviados):
        servico = buscar_servico_por_slug(slug)
        if servico is not None:
            validos[slug] = servico.id_servico

    atuais = set(_slugs_servicos_da_bancada(id_bancada))
    desejados = set(validos.keys())

    for slug in desejados - atuais:
        associar_servico_bancada(validos[slug], id_bancada, id_usuario=None)

    atuais_por_slug = {}
    for slug in atuais:
        servico = buscar_servico_por_slug(slug)
        if servico is not None:
            atuais_por_slug[slug] = servico.id_servico
    for slug in atuais - desejados:
        if slug in atuais_por_slug:
            desassociar_servico_bancada(atuais_por_slug[slug], id_bancada, id_usuario=None)


# ========================= BANCADA =========================

@admin_bp.post("/servicos/bancadas/criar")
def criar_bancada_route():
    """Cria uma bancada a partir do formulário e sincroniza serviços marcados.

    Valida nome e descrição (ambos obrigatórios; Bancada.descricao é NOT NULL) e
    associa os serviços marcados nos checkboxes. Redireciona (PRG) para a página
    de bancadas.

    Returns:
        Response: redirecionamento para o catálogo de bancadas.
    """
    voltar = redirect(url_for("admin.catalogo_bancadas", gerenciar=1))

    nome = request.form.get("nome", "").strip()
    descricao = request.form.get("descricao", "").strip()

    if not nome or not descricao:
        flash("Preencha nome e descrição da bancada.", "danger")
        return voltar

    try:
        novo_id = criar_bancada(nome=nome, descricao=descricao)
    except SQLAlchemyError:
        flash("Não foi possível criar a bancada.", "danger")
        return voltar

    # Sincroniza os serviços marcados nas checkboxes (associa os novos).
    _sincronizar_servicos_da_bancada(novo_id, request.form.getlist("servicos"))

    flash("Bancada criada.", "success")
    return voltar


@admin_bp.post("/servicos/bancadas/atualizar/<int:id_bancada>")
def atualizar_bancada_route(id_bancada):
    """Atualiza uma bancada e ressincroniza os serviços associados.

    Args:
        id_bancada (int): identificador da bancada a atualizar.

    Returns:
        Response: redirecionamento para o catálogo de bancadas.
    """
    voltar = redirect(url_for("admin.catalogo_bancadas", gerenciar=1))

    bancada = buscar_bancada_por_id(id_bancada)
    if bancada is None:
        flash("Bancada não encontrada.", "danger")
        return voltar

    nome = request.form.get("nome", "").strip()
    descricao = request.form.get("descricao", "").strip()

    if not nome or not descricao:
        flash("Preencha nome e descrição da bancada.", "danger")
        return voltar

    try:
        sucesso = atualizar_bancada(id_bancada, id_usuario=None, nome=nome,
                                    descricao=descricao)
    except SQLAlchemyError:
        flash("Não foi possível atualizar a bancada.", "danger")
        return voltar

    if not sucesso:
        flash("Bancada não encontrada.", "danger")
        return voltar

    # Sincroniza os serviços marcados (associa os novos, desassocia os retirados).
    _sincronizar_servicos_da_bancada(id_bancada, request.form.getlist("servicos"))

    flash("Bancada atualizada.", "success")
    return voltar


@admin_bp.post("/servicos/bancadas/deletar/<int:id_bancada>")
def desativar_bancada_route(id_bancada):
    """Desativa (soft delete) uma bancada.

    Não remove fisicamente o registro (pode estar referenciado por ServicoBancada
    e outros vínculos): marca ativo=False (some das listagens de ativas) mas
    continua no banco. Espelha o soft delete de cardápio/bebida.

    Args:
        id_bancada (int): identificador da bancada a desativar.

    Returns:
        Response: redirecionamento para o catálogo de bancadas.
    """
    voltar = redirect(url_for("admin.catalogo_bancadas", gerenciar=1))

    bancada = buscar_bancada_por_id(id_bancada)
    if bancada is None:
        flash("Bancada não encontrada.", "danger")
        return voltar

    try:
        sucesso = desativar_bancada(id_bancada)
    except SQLAlchemyError:
        flash("Não foi possível remover a bancada.", "danger")
        return voltar

    if not sucesso:
        flash("Bancada não encontrada.", "danger")
        return voltar

    flash("Bancada removida.", "success")
    return voltar
