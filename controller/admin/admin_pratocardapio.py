"""Rotas administrativas de pratos, cardápios e suas associações."""

from . import admin_bp, _retorno, _bool_form, _int_form, _mapa_imagens, _imagem_rel

from flask import request, flash, redirect, render_template, url_for

from sqlalchemy.exc import SQLAlchemyError

from utils import moeda_para_centavos

from services import imagem_cardapio, imagem_prato

from model.servico_model import (
    criar_cardapio, atualizar_cardapio, buscar_cardapio_por_id,
    listar_cardapios_ativos, listar_servicos, buscar_servico_por_slug,
    associar_servico_cardapio, desassociar_servico_cardapio,
    listar_cardapios_do_servico, desativar_cardapio,
    ServicoCardapio, Servico, Cardapio,
)
from model.ficha_model import (
    # Prato
    criar_prato, buscar_prato_por_id, atualizar_prato,
    desativar_prato, listar_pratos_ativos,
    # Prato x cardápio
    associar_prato_cardapio, buscar_prato_cardapio, listar_pratos_por_cardapio,
    atualizar_prato_cardapio, deletar_prato_cardapio, PratoCardapio,
    # Ingredientes e ficha técnica
    listar_ingredientes, buscar_ingrediente_por_id,
    criar_ficha_tecnica, atualizar_ficha_tecnica, deletar_ficha_tecnica,
    listar_ficha_tecnica_por_prato,
)
from utils import nome_exibicao
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
    """Monta a lista de cardápios ATIVOS para o catálogo admin (desativados são ocultados)."""
    itens = []
    for cardapio in listar_cardapios_ativos() or []:
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

# ===================== CATÁLOGO DE PRATOS (página real) =====================

def _cardapios_associados_do_prato(id_prato: int) -> list[int]:
    """Lista os ids dos cardápios atualmente associados a um prato."""
    ids = db.session.execute(
        db.select(PratoCardapio.id_cardapio)
        .where(PratoCardapio.id_prato == id_prato),
    ).scalars().all()
    return list(ids)


def _cardapios_catalogo() -> dict:
    """Mapeia id_cardapio -> nome a partir dos cardápios reais do banco.

    Usado para montar as checkboxes do formulário de prato (associação a
    cardápios) e para exibir os cardápios de cada prato na listagem. Espelha
    _servicos_catalogo do cardápio, mas chaveado por id (não por slug) porque a
    associação prato-cardápio usa a chave composta (id_prato, id_cardapio).

    Returns:
        dict: {id_cardapio: nome} ordenado pelos cardápios cadastrados.
    """
    return {c.id_cardapio: c.nome for c in (listar_cardapios_ativos() or [])}


def _itens_prato(mapa_imagens: dict) -> list:
    """Monta a lista de pratos ATIVOS para o catálogo admin (desativados são ocultados)."""
    itens = []
    for prato in listar_pratos_ativos() or []:
        itens.append({
            "id": prato.id_prato,
            "nome": prato.nome,
            "descricao": prato.descricao,
            "tipo_prato": prato.tipo_prato,
            "tempo_preparo": prato.tempo_preparo,
            "requer_pre_preparo": prato.requer_pre_preparo,
            "imagem": _imagem_rel(mapa_imagens, prato.imagem_slug),
            "cardapios": _cardapios_associados_do_prato(prato.id_prato),
            "ativo": prato.ativo,
        })
    return itens


@admin_bp.get("/pratos")
def catalogo_pratos():
    """Renderiza a página real de catálogo de pratos (CMS).

    Lista apenas os pratos ATIVOS (via listar_pratos_ativos); pratos desativados
    (soft delete) não aparecem. Suporta ?editar=<id> (abre o formulário já
    preenchido) e ?gerenciar=1 (abre a seção de gerenciamento), como nas demais
    páginas.
    """
    mapa = _mapa_imagens("imagens-pratos.json")
    itens = _itens_prato(mapa)
    cardapios_catalogo = _cardapios_catalogo()
    ingredientes_catalogo = _ingredientes_catalogo()
    # mapa auxiliar id -> unidade para converter a ficha de volta à exibição.
    unidade_por_ingrediente = {i["id"]: i["unidade"] for i in ingredientes_catalogo}

    editar = request.args.get("editar", "")
    atual = None
    valores = {}
    ficha_prato = {}
    if editar:
        atual = next((i for i in itens if str(i["id"]) == str(editar)), None)
        if atual:
            valores = dict(atual)
            # Pré-carrega a ficha atual convertida de volta para g/ml/unidade.
            for id_ingrediente, qtd in _ficha_atual_do_prato(atual["id"]).items():
                unidade = unidade_por_ingrediente.get(id_ingrediente, "")
                ficha_prato[id_ingrediente] = _qtd_para_exibir(qtd, unidade)

    return render_template(
        "catalogo_pratos.html",
        itens=itens,
        cardapios_catalogo=cardapios_catalogo,
        ingredientes_catalogo=ingredientes_catalogo,
        ficha_prato=ficha_prato,
        atual=atual,
        valores=valores,
        gerenciar=request.args.get("gerenciar") == "1",
    )


def _sincronizar_cardapios_do_prato(id_prato: int, ids_cardapio_enviados: list) -> None:
    """Sincroniza PratoCardapio com os cardápios marcados (associa/desassocia).

    A partir dos ids de cardápio marcados nos checkboxes, associa os novos
    (associar_prato_cardapio com qtd padrão 1 e descricao None) e desassocia os
    retirados (deletar_prato_cardapio), comparando com as associações atuais do
    prato. Espelha _sincronizar_servicos do cardápio.

    Nota de decisão: pratos se ligam a SERVIÇOS INDIRETAMENTE via cardápios (não
    há tabela prato-servico no schema). Portanto associar o prato a cardápios é a
    forma de colocá-lo em serviços -- o cardápio já carrega a associação com os
    serviços (ServicoCardapio).

    Apenas ids válidos (correspondentes a Cardapio reais) são considerados; ids
    desconhecidos são ignorados silenciosamente.
    """
    validos = set()
    for texto in dict.fromkeys(ids_cardapio_enviados):
        try:
            id_cardapio = int(str(texto).strip())
        except (TypeError, ValueError):
            continue
        if db.session.get(Cardapio, id_cardapio) is not None:
            validos.add(id_cardapio)

    atuais = set(_cardapios_associados_do_prato(id_prato))

    for id_cardapio in validos - atuais:
        associar_prato_cardapio(id_prato, id_cardapio, 1, None)

    for id_cardapio in atuais - validos:
        deletar_prato_cardapio(id_prato, id_cardapio)


# ===================== FICHA TÉCNICA DO PRATO (ingredientes) =====================

def _qtd_para_armazenar(valor_digitado: float, unidade: str) -> int:
    """Converte a quantidade digitada no form para o inteiro armazenado na ficha.

    Segue a convenção de unidades do seed de PRATO (FEAT-001): a coluna
    qtd_necessaria é Integer com CHECK qtd_necessaria > 0, então o valor
    armazenado é sempre inteiro e estritamente positivo.

    - unidade 'g'/'ml': armazenado = int(round(valor * 1000)), com piso 1
      (ex.: 0.077 g -> 77).
    - demais unidades (ex.: 'unidade'): armazenado = max(1, round(valor)).

    Args:
        valor_digitado (float): quantidade digitada (em g/ml/unidade).
        unidade (str): unidade do ingrediente (comparada case-insensitive).

    Returns:
        int: quantidade a gravar (inteiro >= 1).
    """
    unidade_norm = (unidade or "").strip().lower()
    if unidade_norm in {"g", "ml"}:
        return max(1, int(round(valor_digitado * 1000)))
    return max(1, int(round(valor_digitado)))


def _qtd_para_exibir(qtd_armazenada: int, unidade: str):
    """Converte a quantidade armazenada de volta para a exibição no form.

    Inversa de _qtd_para_armazenar: 'g'/'ml' -> armazenado / 1000 (ex.: 77 ->
    0.077); demais unidades mostram o inteiro cru.

    Args:
        qtd_armazenada (int): quantidade gravada na ficha técnica.
        unidade (str): unidade do ingrediente.

    Returns:
        float | int: valor para pré-preencher o input do formulário.
    """
    unidade_norm = (unidade or "").strip().lower()
    if unidade_norm in {"g", "ml"}:
        return qtd_armazenada / 1000
    return qtd_armazenada


def _ficha_atual_do_prato(id_prato: int) -> dict:
    """Retorna a ficha técnica atual do prato como {id_ingrediente: qtd_armazenada}.

    listar_ficha_tecnica_por_prato retorna None quando a ficha está vazia; nesse
    caso devolvemos {} para facilitar as comparações de sincronização.
    """
    itens = listar_ficha_tecnica_por_prato(id_prato) or []
    return {f.id_ingrediente: f.qtd_necessaria for f in itens}


def _ler_ingredientes_do_form(form) -> tuple[dict, bool]:
    """Lê ingredientes marcados + quantidades do formulário.

    Padrão de campos no form: para cada ingrediente, um checkbox
    name='ingredientes' value='<id>' indica inclusão, e um input numérico
    name='qtd_ingrediente_<id>' traz a quantidade digitada (em g/ml/unidade,
    aceitando vírgula ou ponto). Só ingredientes marcados COM quantidade > 0
    entram na ficha; a conversão para o inteiro armazenado segue a convenção de
    unidades do prato.

    Args:
        form: request.form (MultiDict) do POST.

    Returns:
        tuple[dict, bool]: (itens, invalido) onde itens é
            {id_ingrediente: qtd_armazenada_inteira_positiva} e invalido é True
            quando algum ingrediente foi marcado sem quantidade válida (> 0).
    """
    itens = {}
    invalido = False
    for texto in dict.fromkeys(form.getlist("ingredientes")):
        try:
            id_ingrediente = int(str(texto).strip())
        except (TypeError, ValueError):
            continue
        ingrediente = buscar_ingrediente_por_id(id_ingrediente)
        if ingrediente is None:
            # ids desconhecidos são ignorados silenciosamente.
            continue
        bruto = form.get(f"qtd_ingrediente_{id_ingrediente}", "").strip()
        if not bruto:
            invalido = True
            continue
        try:
            valor = float(bruto.replace(",", "."))
        except ValueError:
            invalido = True
            continue
        if valor <= 0:
            invalido = True
            continue
        itens[id_ingrediente] = _qtd_para_armazenar(valor, ingrediente.unidade)
    return itens, invalido


def _sincronizar_ficha_do_prato(id_prato: int, itens: dict) -> None:
    """Sincroniza a FichaTecnica do prato com os ingredientes desejados.

    'itens' é {id_ingrediente: qtd_armazenada_inteira_positiva}. Espelha
    _sincronizar_cardapios_do_prato: cria os novos (criar_ficha_tecnica),
    atualiza os que mudaram de quantidade (atualizar_ficha_tecnica) e remove os
    desmarcados (deletar_ficha_tecnica). Apenas ids válidos (existentes em
    buscar_ingrediente_por_id) são considerados.

    Args:
        id_prato (int): identificador do prato.
        itens (dict): {id_ingrediente: qtd_armazenada} desejado.
    """
    desejados = {}
    for id_ingrediente, qtd in itens.items():
        if buscar_ingrediente_por_id(id_ingrediente) is not None:
            desejados[id_ingrediente] = qtd

    atuais = _ficha_atual_do_prato(id_prato)

    for id_ingrediente, qtd in desejados.items():
        if id_ingrediente not in atuais:
            criar_ficha_tecnica(id_prato, id_ingrediente, qtd)
        elif atuais[id_ingrediente] != qtd:
            atualizar_ficha_tecnica(id_prato, id_ingrediente, qtd)

    for id_ingrediente in set(atuais) - set(desejados):
        deletar_ficha_tecnica(id_prato, id_ingrediente)


def _ingredientes_catalogo() -> list:
    """Monta a lista de ingredientes disponíveis para o formulário de prato.

    Returns:
        list: dicts {id, nome (exibição), unidade}, ordenados por nome exibido.
            Vazia quando não há ingredientes (listar_ingredientes -> None).
    """
    itens = []
    for ing in listar_ingredientes() or []:
        itens.append({
            "id": ing.id_ingrediente,
            "nome": nome_exibicao(ing.nome),
            "unidade": ing.unidade,
        })
    itens.sort(key=lambda i: i["nome"].lower())
    return itens


# ========================= PRATO =========================

@admin_bp.post("/servicos/pratos/criar")
def criar_prato_route():
    """Cria um prato a partir do formulário, com imagem e cardápios opcionais.

    Valida nome/descrição/tipo/tempo de preparo, aceita upload opcional de imagem
    e sincroniza as associações a cardápios marcadas nos checkboxes. Redireciona
    (PRG) para a página de pratos.

    Returns:
        Response: redirecionamento para o catálogo de pratos.
    """
    voltar = redirect(url_for("admin.catalogo_pratos", gerenciar=1))

    nome = request.form.get("nome", "").strip()
    descricao = request.form.get("descricao", "").strip()
    tipo_prato = request.form.get("tipo_prato", "").strip()
    tempo_texto = request.form.get("tempo_preparo", "").strip()
    requer_pre_preparo = _bool_form(request.form.get("requer_pre_preparo", ""))

    tipos_validos = {"entrada", "acompanhamento", "prato principal", "sobremesa"}
    if not nome or not descricao or not tipo_prato or not tempo_texto:
        flash("Preencha todos os campos obrigatórios do prato.", "danger")
        return voltar
    if tipo_prato not in tipos_validos:
        flash("Tipo de prato inválido.", "danger")
        return voltar

    try:
        tempo_preparo = _int_form(tempo_texto)
    except ValueError:
        flash("O tempo de preparo deve ser um número inteiro.", "danger")
        return voltar

    if tempo_preparo < 0:
        flash("O tempo de preparo não pode ser negativo.", "danger")
        return voltar

    # Imagem opcional: salva o arquivo e sincroniza docs/imagens-pratos.json.
    imagem_slug = None
    arquivo = request.files.get("imagem")
    if arquivo is not None and arquivo.filename:
        try:
            imagem_slug = imagem_prato.salvar_imagem_prato(arquivo, nome)
        except ValueError as erro:
            flash(f"Imagem inválida: {erro}", "danger")
            return voltar

    try:
        novo_id = criar_prato(nome, descricao, tipo_prato, tempo_preparo,
                              requer_pre_preparo, imagem_slug=imagem_slug)
    except SQLAlchemyError:
        flash("Não foi possível criar o prato.", "danger")
        return voltar

    # Sincroniza a ficha técnica (ingredientes + quantidades). Se algum
    # ingrediente foi marcado sem quantidade válida, o prato já foi criado, mas
    # a ficha NÃO é gravada: sinaliza o erro para o admin corrigir na edição.
    itens_ficha, invalido = _ler_ingredientes_do_form(request.form)
    if invalido:
        flash("Prato criado, mas a ficha técnica não foi salva: informe uma "
              "quantidade válida (maior que zero) para cada ingrediente "
              "selecionado.", "danger")
        return voltar

    # Sequência pós-entidade (associações a cardápios + ficha técnica): cada
    # função do model commita individualmente (padrão do projeto), sem transação
    # compartilhada. Envolvemos a sequência num try/except para SINALIZAR uma
    # falha de banco ao admin em vez de deixar a exceção escapar com estado
    # parcial e sem aviso, alinhando ao tratamento de erro da criação da entidade.
    try:
        # Sincroniza os cardápios marcados nas checkboxes (associa os novos).
        _sincronizar_cardapios_do_prato(novo_id, request.form.getlist("cardapios"))
        _sincronizar_ficha_do_prato(novo_id, itens_ficha)
    except SQLAlchemyError:
        db.session.rollback()
        flash("Não foi possível salvar as associações/ficha técnica do prato.", "danger")
        return voltar

    flash("Prato criado.", "success")
    return voltar


@admin_bp.post("/servicos/pratos/atualizar/<int:id_prato>")
def atualizar_prato_route(id_prato):
    """Atualiza um prato (imagem e cardápios opcionais) a partir do formulário.

    Args:
        id_prato (int): identificador do prato a atualizar.

    Returns:
        Response: redirecionamento para o catálogo de pratos.
    """
    voltar = redirect(url_for("admin.catalogo_pratos", gerenciar=1))

    prato = buscar_prato_por_id(id_prato)
    if prato is None:
        flash("Prato não encontrado.", "danger")
        return voltar

    nome = request.form.get("nome", "").strip()
    descricao = request.form.get("descricao", "").strip()
    tipo_prato = request.form.get("tipo_prato", "").strip()
    tempo_texto = request.form.get("tempo_preparo", "").strip()
    requer_pre_preparo = _bool_form(request.form.get("requer_pre_preparo", ""))

    tipos_validos = {"entrada", "acompanhamento", "prato principal", "sobremesa"}
    if not nome or not descricao or not tipo_prato or not tempo_texto:
        flash("Preencha todos os campos obrigatórios do prato.", "danger")
        return voltar
    if tipo_prato not in tipos_validos:
        flash("Tipo de prato inválido.", "danger")
        return voltar

    try:
        tempo_preparo = _int_form(tempo_texto)
    except ValueError:
        flash("O tempo de preparo deve ser um número inteiro.", "danger")
        return voltar

    if tempo_preparo < 0:
        flash("O tempo de preparo não pode ser negativo.", "danger")
        return voltar

    # Nova imagem é opcional: se enviada, sobrescreve a imagem atual (mantendo o
    # mesmo slug quando já existe); se não, mantém a imagem atual.
    imagem_slug = None
    arquivo = request.files.get("imagem")
    if arquivo is not None and arquivo.filename:
        try:
            imagem_slug = imagem_prato.atualizar_imagem_prato(
                arquivo, nome, prato.imagem_slug)
        except ValueError as erro:
            flash(f"Imagem inválida: {erro}", "danger")
            return voltar

    try:
        sucesso = atualizar_prato(
            id_prato=id_prato, nome=nome, descricao=descricao,
            tipo_prato=tipo_prato, tempo_preparo=tempo_preparo,
            requer_pre_preparo=requer_pre_preparo, imagem_slug=imagem_slug,
        )
    except SQLAlchemyError:
        flash("Não foi possível atualizar o prato.", "danger")
        return voltar

    if not sucesso:
        flash("Prato não encontrado.", "danger")
        return voltar

    # Sincroniza a ficha técnica (cria/atualiza/remove ingredientes). Se algum
    # ingrediente foi marcado sem quantidade válida, o prato já foi atualizado,
    # mas a ficha NÃO é alterada: sinaliza o erro sem mexer na ficha existente.
    itens_ficha, invalido = _ler_ingredientes_do_form(request.form)
    if invalido:
        flash("Prato atualizado, mas a ficha técnica não foi alterada: informe "
              "uma quantidade válida (maior que zero) para cada ingrediente "
              "selecionado.", "danger")
        return voltar

    # Sequência pós-entidade (ver criar_prato_route): sinaliza falha de banco com
    # flash 'danger' em vez de deixar a exceção escapar.
    try:
        # Sincroniza os cardápios marcados (associa os novos, desassocia os retirados).
        _sincronizar_cardapios_do_prato(id_prato, request.form.getlist("cardapios"))
        _sincronizar_ficha_do_prato(id_prato, itens_ficha)
    except SQLAlchemyError:
        db.session.rollback()
        flash("Não foi possível salvar as associações/ficha técnica do prato.", "danger")
        return voltar

    flash("Prato atualizado.", "success")
    return voltar


@admin_bp.post("/servicos/pratos/deletar/<int:id_prato>")
def deletar_prato_route(id_prato):
    """Desativa (soft delete) um prato e esconde sua imagem do JSON.

    Não remove fisicamente o registro (pode estar referenciado por pedidos
    antigos, que a cozinha continua resolvendo): marca ativo=False (some das
    listagens do admin) e retira a imagem do docs/imagens-pratos.json.

    Args:
        id_prato (int): identificador do prato a desativar.

    Returns:
        Response: redirecionamento para o catálogo de pratos.
    """
    voltar = redirect(url_for("admin.catalogo_pratos", gerenciar=1))

    prato = buscar_prato_por_id(id_prato)
    if prato is None:
        flash("Prato não encontrado.", "danger")
        return voltar

    slug = prato.imagem_slug
    if not desativar_prato(id_prato):
        flash("Prato não encontrado.", "danger")
        return voltar

    if slug:
        imagem_prato.remover_imagem_prato(slug)

    flash("Prato removido.", "success")
    return voltar


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
@admin_bp.post("/servicos/prato-cardapio/atualizar/<int:id_prato>/<int:id_cardapio>")
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