"""Rotas administrativas de gerenciamento de serviços e seu painel."""

from . import admin_bp, _retorno, _mapa_imagens, _imagem_rel

from flask import render_template, flash, request, redirect, url_for

from sqlalchemy.exc import SQLAlchemyError

from services import imagem_servico

from model.servico_model import (
    criar_servico, atualizar_servico, desativar_servico, deletar_servico,
    listar_servicos_ativos, buscar_servico_por_id, buscar_servico_por_nome,
    buscar_servicos,
)
from model.ficha_model import buscar_ingredientes, buscar_lotes

# ============================== Servicos =============================

@admin_bp.get("/servicos")
def pagina_servicos():
    """Renderiza a página de serviços com busca unificada.

    O parâmetro de query `busca` filtra, por correspondência parcial, serviços,
    ingredientes e lotes. Sem `busca`, lista tudo.

    Returns:
        str: HTML da página de estoque renderizada.
    """
    busca = request.args.get("busca", "").strip()

    servicos = buscar_servicos(busca)
    ingredientes = buscar_ingredientes(busca)
    lotes = buscar_lotes(busca)

    return render_template(
        "estoque.html",
        busca=busca,
        servicos=servicos,
        ingredientes=ingredientes,
        lotes=lotes,
    )


# ===================== CATÁLOGO DE SERVIÇOS (página real) =====================

def _itens_servico(mapa_imagens: dict) -> list:
    """Monta a lista de serviços ATIVOS para o catálogo admin (desativados são ocultados).

    A imagem de cada serviço é resolvida pelo imagem_slug do banco (via
    _imagem_rel) e, quando o serviço não tem upload (caso dos serviços seed, em
    que imagem_slug é None), cai no mesmo mapa fixo por slug que a home usa
    (_FOTOS_SERVICOS), para que a prévia da edição exiba a imagem padrão. Import
    tardio de controller.cliente_controller para evitar import circular.
    """
    from controller.cliente_controller import _FOTOS_SERVICOS

    itens = []
    for servico in listar_servicos_ativos() or []:
        imagem = _imagem_rel(mapa_imagens, servico.imagem_slug)
        if not imagem:
            imagem = _FOTOS_SERVICOS.get(servico.slug)
        itens.append({
            "id": servico.id_servico,
            "nome": servico.nome,
            "descricao": servico.descricao,
            "slug": servico.slug,
            "imagem": imagem,
            "ativo": servico.ativo,
        })
    return itens


@admin_bp.get("/catalogo-servicos")
def catalogo_servicos():
    """Renderiza a página real de catálogo de serviços (CMS).

    Lista apenas os serviços ATIVOS (via listar_servicos_ativos); serviços
    desativados (soft delete) não aparecem. Suporta ?editar=<id> (abre o
    formulário já preenchido) e ?gerenciar=1 (abre a seção de gerenciamento),
    como nas demais páginas. Possui campo de imagem (upload opcional).
    """
    mapa = _mapa_imagens("imagens-servicos.json")
    itens = _itens_servico(mapa)

    editar = request.args.get("editar", "")
    atual = None
    valores = {}
    if editar:
        atual = next((i for i in itens if str(i["id"]) == str(editar)), None)
        if atual:
            valores = dict(atual)

    return render_template(
        "catalogo_servicos.html",
        itens=itens,
        atual=atual,
        valores=valores,
        gerenciar=request.args.get("gerenciar") == "1",
    )


# ========================= CRIAR SERVIÇO =========================
@admin_bp.post("/servicos/criar")
def criar_servico_route():
    """Cria um serviço a partir do formulário, com imagem opcional.

    Valida nome e descrição (ambos obrigatórios), impede nome duplicado
    (Servico.nome é UNIQUE) e aceita upload opcional de imagem. Redireciona
    (PRG) para o catálogo de serviços.

    Returns:
        Response: redirecionamento para o catálogo de serviços.
    """
    voltar = redirect(url_for("admin.catalogo_servicos", gerenciar=1))

    nome = request.form.get("nome", "").strip()
    descricao = request.form.get("descricao", "").strip()

    if not nome or not descricao:
        flash("Preencha nome e descrição do serviço.", "danger")
        return voltar

    # Servico.nome é UNIQUE: evita o IntegrityError sinalizando ao admin.
    if buscar_servico_por_nome(nome) is not None:
        flash("Já existe um serviço com esse nome.", "danger")
        return voltar

    # Imagem opcional: salva o arquivo e sincroniza docs/imagens-servicos.json.
    imagem_slug = None
    arquivo = request.files.get("imagem")
    if arquivo is not None and arquivo.filename:
        try:
            imagem_slug = imagem_servico.salvar_imagem_servico(arquivo, nome)
        except ValueError as erro:
            flash(f"Imagem inválida: {erro}", "danger")
            return voltar

    try:
        criar_servico(nome=nome, descricao=descricao, imagem_slug=imagem_slug)
    except SQLAlchemyError:
        flash("Não foi possível criar o serviço.", "danger")
        return voltar

    flash("Serviço criado.", "success")
    return voltar


# ========================= ATUALIZAR SERVIÇO =========================
@admin_bp.post("/servicos/atualizar_servico/<int:id_servico>")
def at_servico(id_servico: int):
    """Atualiza um serviço a partir dos dados do formulário.

    Valida nome e descrição, impede colisão de nome com OUTRO serviço
    (Servico.nome é UNIQUE) e aceita upload opcional de nova imagem (quando um
    arquivo é enviado, mantém o mesmo slug). Redireciona (PRG) para o catálogo.

    Args:
        id_servico (int): identificador do serviço a atualizar.

    Returns:
        Response: redirecionamento para o catálogo de serviços.
    """
    voltar = redirect(url_for("admin.catalogo_servicos", gerenciar=1))

    servico = buscar_servico_por_id(id_servico)
    if servico is None:
        flash("Serviço não encontrado.", "danger")
        return voltar

    nome = request.form.get("nome", "").strip()
    descricao = request.form.get("descricao", "").strip()

    if not nome or not descricao:
        flash("Preencha nome e descrição do serviço.", "danger")
        return voltar

    # Se o nome submetido já pertence a OUTRO serviço, evita o IntegrityError.
    existente = buscar_servico_por_nome(nome)
    if existente is not None and existente.id_servico != id_servico:
        flash("Já existe um serviço com esse nome.", "danger")
        return voltar

    # Nova imagem é opcional: se enviada, sobrescreve a imagem atual (mantendo o
    # mesmo slug quando já existe); imagem_slug fica None quando nenhum arquivo é
    # enviado, preservando a imagem atual em atualizar_servico.
    imagem_slug = None
    arquivo = request.files.get("imagem")
    if arquivo is not None and arquivo.filename:
        try:
            imagem_slug = imagem_servico.atualizar_imagem_servico(
                arquivo, nome, servico.imagem_slug)
        except ValueError as erro:
            flash(f"Imagem inválida: {erro}", "danger")
            return voltar

    try:
        sucesso = atualizar_servico(
            id_servico=id_servico, nome=nome, descricao=descricao,
            imagem_slug=imagem_slug)
    except SQLAlchemyError:
        flash("Não foi possível atualizar o serviço.", "danger")
        return voltar

    if not sucesso:
        flash("Serviço não encontrado.", "danger")
        return voltar

    flash("Serviço atualizado.", "success")
    return voltar


# ========================= REMOVER SERVIÇO (SOFT DELETE) =========================
@admin_bp.post("/servicos/deletar_servico/<int:id_servico>")
def del_servico(id_servico: int):
    """Desativa (soft delete) um serviço e esconde sua imagem do JSON.

    Não remove fisicamente o registro (pode estar referenciado por ServicoBancada
    e ServicoCardapio): marca ativo=False (some das listagens) e retira a imagem
    do docs/imagens-servicos.json.

    Args:
        id_servico (int): identificador do serviço a desativar.

    Returns:
        Response: redirecionamento para o catálogo de serviços.
    """
    voltar = redirect(url_for("admin.catalogo_servicos", gerenciar=1))

    servico = buscar_servico_por_id(id_servico)
    if servico is None:
        flash("Serviço não encontrado.", "danger")
        return voltar

    slug = servico.imagem_slug
    if not desativar_servico(id_servico):
        flash("Serviço não encontrado.", "danger")
        return voltar

    if slug:
        imagem_servico.remover_imagem_servico(slug)

    flash("Serviço removido.", "success")
    return voltar
