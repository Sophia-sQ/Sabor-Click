"""Rotas administrativas de pratos, cardápios e suas associações."""

from . import admin_bp, _retorno, _bool_form, _int_form, _mapa_imagens, _imagem_rel

from flask import request, flash, redirect, render_template, url_for

from sqlalchemy.exc import SQLAlchemyError

from utils import moeda_para_centavos

from services import imagem_cardapio

from model.servico_model import (
    criar_cardapio, atualizar_cardapio, buscar_cardapio_por_id,
    listar_cardapios, listar_servicos, buscar_servico_por_slug,
    associar_servico_cardapio, desassociar_servico_cardapio,
    listar_cardapios_do_servico, desativar_cardapio,
    ServicoCardapio, Servico,
)
from model.ficha_model import (
    # Prato
    criar_prato, buscar_prato_por_id, listar_pratos, atualizar_prato, deletar_prato,
    # Prato x cardápio
    associar_prato_cardapio, buscar_prato_cardapio, listar_pratos_por_cardapio,
    atualizar_prato_cardapio, deletar_prato_cardapio
)
from database import db


# ===================== CATÁLOGO DE CARDÁPIOS (página real) =====================

def _servicos_catalogo() -> dict:
    """Mapeia slug -> (nome, categoria) a partir dos serviços reais do banco.

    Usado tanto para montar as checkboxes do formulário quanto para exibir os
    serviços associados a cada cardápio na listagem. A categoria é mantida como
    None (não há categoria por serviço no banco), preservando o formato de tupla
    que o template espera (slug -> (nome, categoria)).

    Returns:
        dict: {slug: (nome, None)} ordenado pelos serviços cadastrados.
    """
    return {s.slug: (s.nome, None) for s in (listar_servicos() or [])}


def _slugs_associados(id_cardapio: int) -> list:
    """Lista os slugs dos serviços atualmente associados a um cardápio."""
    slugs = db.session.execute(
        db.select(Servico.slug)
        .join(ServicoCardapio, Servico.id_servico == ServicoCardapio.id_servico)
        .where(ServicoCardapio.id_cardapio == id_cardapio),
    ).scalars().all()
    return list(slugs)


def _itens_cardapio(mapa_imagens: dict) -> list:
    """Monta a lista de cardápios (todos, ativos e inativos) para o catálogo admin."""
    itens = []
    for cardapio in listar_cardapios() or []:
        itens.append({
            "id": cardapio.id_cardapio,
            "nome": cardapio.nome,
            "descricao": cardapio.descricao,
            # Categoria do cardápio não é armazenada; os serviços associados a
            # representam. O template usa 'categoria' apenas para o rótulo da
            # listagem, então deixamos o primeiro serviço associado (ou vazio).
            "categoria": "",
            "preco": cardapio.preco_base / 100,  # exibição em R$
            "imagem": _imagem_rel(mapa_imagens, _slug_imagem(cardapio)),
            "servicos": _slugs_associados(cardapio.id_cardapio),
            "ativo": cardapio.ativo,
        })
    return itens


def _slug_imagem(cardapio):
    """Resolve o slug de imagem de um cardápio (prioriza o imagem_slug do banco)."""
    from controller.cliente_controller import _slug_imagem_do_cardapio
    return _slug_imagem_do_cardapio(cardapio)


@admin_bp.get("/cardapio")
def catalogo_cardapio():
    """Renderiza a página real de catálogo de cardápios (CMS)."""
    mapa = _mapa_imagens("imagens-menu.json")
    itens = _itens_cardapio(mapa)
    servicos_catalogo = _servicos_catalogo()
    opcoes = [("", "Cardápio")]

    editar = request.args.get("editar", "")
    atual = None
    valores = {}
    if editar:
        try:
            atual = next((i for i in itens if str(i["id"]) == str(editar)), None)
        except ValueError:
            atual = None
        if atual:
            valores = dict(atual)

    return render_template(
        "catalogo_admin.html",
        tipo="cardapio",
        itens=itens,
        opcoes=opcoes,
        servicos_catalogo=servicos_catalogo,
        atual=atual,
        valores=valores,
        gerenciar=request.args.get("gerenciar") == "1",
    )


def _sincronizar_servicos(id_cardapio: int, slugs_enviados: list) -> None:
    """Sincroniza ServicoCardapio com os slugs marcados (associa/desassocia).

    Apenas slugs válidos (correspondentes a Servico.slug reais) são considerados;
    slugs desconhecidos são ignorados silenciosamente.
    """
    validos = {}
    for slug in dict.fromkeys(slugs_enviados):
        servico = buscar_servico_por_slug(slug)
        if servico is not None:
            validos[slug] = servico.id_servico

    atuais = set(_slugs_associados(id_cardapio))
    desejados = set(validos.keys())

    for slug in desejados - atuais:
        associar_servico_cardapio(validos[slug], id_cardapio, id_usuario=None)

    atuais_por_slug = {}
    for slug in atuais:
        servico = buscar_servico_por_slug(slug)
        if servico is not None:
            atuais_por_slug[slug] = servico.id_servico
    for slug in atuais - desejados:
        if slug in atuais_por_slug:
            desassociar_servico_cardapio(atuais_por_slug[slug], id_cardapio, id_usuario=None)
# ========================= CRIAR CARDÁPIO =========================
@admin_bp.post("/servicos/criar_cardapio")
def c_cardapio():
    """Cria um cardápio a partir dos dados do formulário.

    Valida nome, descrição e preço-base e sinaliza o resultado via flash.

    Returns:
        Response: redirecionamento para a página de serviços.
    """
    voltar = redirect(url_for("admin.catalogo_cardapio", gerenciar=1))

    nome = request.form.get("nome", "").strip()
    descricao = request.form.get("descricao", "").strip()
    preco_texto = request.form.get("preco_base", "").strip()

    if not nome or not descricao or not preco_texto:
        flash("Preencha todos os campos.", "danger")
        return voltar
    
    # preco_base é armazenado em CENTAVOS (inteiro); converte o texto digitado
    # (ex.: "149,90" / "149.90") para centavos.
    try:
        preco_base = moeda_para_centavos(preco_texto)
    except ValueError:
        flash("Preço inválido.", "danger")
        return voltar

    if preco_base < 0:
        flash("O preço deve ser válido e não negativo.", "danger")
        return voltar

    # Imagem é opcional: se enviada, salva o arquivo e atualiza o JSON de imagens,
    # obtendo o slug persistido no cardápio; se não, o cardápio é criado sem imagem.
    imagem_slug = None
    arquivo = request.files.get("imagem")
    if arquivo is not None and arquivo.filename:
        try:
            imagem_slug = imagem_cardapio.salvar_imagem_cardapio(arquivo, nome)
        except ValueError as erro:
            flash(f"Imagem inválida: {erro}", "danger")
            return voltar

    novo_id = criar_cardapio(nome=nome, descricao=descricao, preco_base=preco_base, imagem_slug=imagem_slug)

    # Sincroniza os serviços marcados nas checkboxes na tabela de associação.
    _sincronizar_servicos(novo_id, request.form.getlist("servicos"))

    flash("Cardápio criado.", "success")
    return redirect(url_for("admin.catalogo_cardapio", gerenciar=1))

# ========================= ATUALIZAR CARDÁPIO =========================
@admin_bp.post("/servicos/atualizar_cardapio/<int:id_cardapio>")
def at_cardapio(id_cardapio):
    """Atualiza um cardápio a partir dos dados do formulário.

    Args:
        id_cardapio (int): identificador do cardápio a atualizar.

    Returns:
        Response: redirecionamento para a página de serviços.
    """
    voltar = redirect(url_for("admin.catalogo_cardapio", gerenciar=1))

    cardapio = buscar_cardapio_por_id(id_cardapio)
    if cardapio is None:
        flash("Cardápio não encontrado.", "danger")
        return voltar

    nome = request.form.get("nome", "").strip()
    descricao = request.form.get("descricao", "").strip()
    preco_texto = request.form.get("preco_base", "").strip()

    if not nome or not descricao or not preco_texto:
        flash("Preencha todos os campos.", "danger")
        return voltar

    # preco_base é armazenado em CENTAVOS (inteiro), igual à criação. O código
    # anterior gravava um Decimal de reais (bug latente); agora converte para
    # centavos via moeda_para_centavos.
    try:
        preco_base = moeda_para_centavos(preco_texto)
    except ValueError:
        flash("Preço inválido.", "danger")
        return voltar

    if preco_base < 0:
        flash("O preço deve ser válido e não negativo.", "danger")
        return voltar

    # Nova imagem é opcional na edição: se enviada, sobrescreve a imagem atual
    # (mantendo o mesmo slug quando já existe) e persiste o slug no cardápio.
    imagem_slug = None
    arquivo = request.files.get("imagem")
    if arquivo is not None and arquivo.filename:
        try:
            imagem_slug = imagem_cardapio.atualizar_imagem_cardapio(
                arquivo, nome, cardapio.imagem_slug)
        except ValueError as erro:
            flash(f"Imagem inválida: {erro}", "danger")
            return voltar

    sucesso = atualizar_cardapio(
        id_cardapio=id_cardapio, nome=nome, descricao=descricao,
        preco_base=preco_base, imagem_slug=imagem_slug)

    if not sucesso:
        flash("Cardápio não encontrado.", "danger")
        return voltar

    # Sincroniza os serviços marcados (associa os novos, desassocia os retirados).
    _sincronizar_servicos(id_cardapio, request.form.getlist("servicos"))

    flash("Cardápio atualizado.", "success")
    return voltar

# ========================= REMOVER CARDÁPIO (SOFT DELETE) =========================
@admin_bp.route("/deletar_cardapio/<int:id_cardapio>", methods=("POST",))
def del_cardapio(id_cardapio):
    """Desativa (soft delete) um cardápio e esconde sua imagem do JSON.

    Não remove fisicamente o registro (pode estar referenciado por pedidos):
    apenas marca ativo=False (some das listagens do cliente) e retira a imagem
    do docs/imagens-menu.json.

    Args:
        id_cardapio (int): identificador do cardápio a desativar.

    Returns:
        Response: redirecionamento para o catálogo de cardápios.
    """
    voltar = redirect(url_for("admin.catalogo_cardapio", gerenciar=1))

    cardapio = buscar_cardapio_por_id(id_cardapio)
    if cardapio is None:
        flash("Cardápio não encontrado.", "danger")
        return voltar

    slug = cardapio.imagem_slug
    if not desativar_cardapio(id_cardapio):
        flash("Cardápio não encontrado.", "danger")
        return voltar

    if slug:
        imagem_cardapio.remover_imagem_cardapio(slug)

    flash("Cardápio removido.", "success")
    return voltar

# ========================= PRATO =========================

@admin_bp.post("/servicos/pratos/criar")
def criar_prato_route():
    """Cria um prato a partir do formulário, validando tipo e tempo de preparo.

    Returns:
        Response: redirecionamento para a página de serviços.
    """
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
    """Atualiza um prato a partir do formulário, validando tipo e tempo.

    Args:
        id_prato (int): identificador do prato a atualizar.

    Returns:
        Response: redirecionamento para a página de serviços.
    """
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
    """Exclui um prato e sinaliza o resultado via flash.

    Args:
        id_prato (int): identificador do prato a excluir.

    Returns:
        Response: redirecionamento para a página de serviços.
    """
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
    """Associa um prato a um cardápio a partir do formulário.

    Returns:
        Response: redirecionamento para a página de serviços.
    """
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
def atualizar_prato_cardapio_route(id_prato, id_cardapio):
    """Atualiza a associação prato-cardápio (quantidade/descrição).

    Valida a quantidade recebida do formulário e sinaliza o resultado via flash.

    Args:
        id_prato (int): identificador do prato.
        id_cardapio (int): identificador do cardápio.

    Returns:
        Response: redirecionamento para a página de serviços.
    """
    
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
    """Remove a associação entre um prato e um cardápio.

    Args:
        id_prato (int): identificador do prato.
        id_cardapio (int): identificador do cardápio.

    Returns:
        Response: redirecionamento para a página de serviços.
    """
    try:
        sucesso = deletar_prato_cardapio(id_prato, id_cardapio)
    except SQLAlchemyError:
        flash("Não foi possível remover a associação.", "danger")
        return _retorno()

    flash("Associação removida." if sucesso else "Associação não encontrada.",
          "success" if sucesso else "danger")
    return _retorno()