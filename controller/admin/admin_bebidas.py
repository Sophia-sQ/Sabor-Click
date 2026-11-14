"""Rotas administrativas de gerenciamento de bebidas."""

from . import admin_bp, _retorno, _int_form, _decimal_form, _mapa_imagens, _imagem_rel

from flask import request, flash, redirect, render_template, url_for
from sqlalchemy.exc import SQLAlchemyError

from decimal import Decimal, InvalidOperation

from services import imagem_bebida

from utils import nome_exibicao

from database import db

from model.pedido_model import (
    # Bebida
    criar_bebida, buscar_bebida_por_id, atualizar_bebida, deletar_bebida,
    desativar_bebida, listar_bebidas_ativas,
)
from model.ficha_model import (
    # Ficha técnica da bebida (uma linha por par bebida-ingrediente)
    criar_ficha_tecnica_bebida, buscar_ficha_tecnica_bebida,
    atualizar_ficha_tecnica_bebida, deletar_ficha_tecnica_bebida,
    listar_ficha_tecnica_por_bebida, volume_ml_bebida,
    # Ingredientes (catálogo da ficha técnica)
    listar_ingredientes, buscar_ingrediente_por_id,
)

# Dois tipos de bebida exibidos no catálogo (mesmo esquema da prévia).
_OPCOES_BEBIDA = [("Sem álcool", "Sem álcool"), ("Com álcool", "Com álcool")]
_CATEGORIAS_VALIDAS = {valor for valor, _ in _OPCOES_BEBIDA}


# ===================== FICHA TÉCNICA DA BEBIDA (ingredientes) =====================
# Convenção de unidades da BEBIDA (FEAT-001, DIFERENTE do prato): o valor
# digitado em g/ml/unidade é gravado DIRETO como inteiro, SEM multiplicar por
# 1000. Isso mantém a coerência com o seed de bebidas, com volume_ml_bebida (que
# soma qtd_necessaria assumindo ml direto) e com a exibição "X ml por porção".
# A coluna qtd_necessaria é Integer com CHECK > 0, então o valor é inteiro >= 1.

def _qtd_bebida_para_armazenar(valor_digitado: float, unidade: str) -> int:
    """Converte a quantidade digitada no form para o inteiro armazenado na ficha.

    Segue a convenção de unidades do seed de BEBIDA (FEAT-001): valor gravado
    DIRETO como inteiro (SEM ×1000), com piso 1.

    - unidade 'ml'/'g': armazenado = max(1, int(round(valor)))
    - demais unidades (ex.: 'unidade'): armazenado = max(1, int(round(valor)))

    Args:
        valor_digitado (float): quantidade digitada (em g/ml/unidade).
        unidade (str): unidade do ingrediente (não altera o resultado; mantido
            por simetria com o helper do prato).

    Returns:
        int: quantidade a gravar (inteiro >= 1).
    """
    return max(1, int(round(valor_digitado)))


def _qtd_bebida_para_exibir(qtd_armazenada: int, unidade: str):
    """Converte a quantidade armazenada de volta para a exibição no form.

    Para bebida a conversão é identidade (armazenado == exibido), pois não há
    fator 1000.
    """
    return qtd_armazenada


def _ficha_atual_da_bebida(id_bebida: int) -> dict:
    """Retorna a ficha técnica atual da bebida como {id_ingrediente: qtd}.

    listar_ficha_tecnica_por_bebida retorna uma lista vazia quando não há itens.
    """
    itens = listar_ficha_tecnica_por_bebida(id_bebida) or []
    return {f.id_ingrediente: f.qtd_necessaria for f in itens}


def _ler_ingredientes_do_form(form) -> tuple[dict, bool]:
    """Lê ingredientes marcados + quantidades do formulário da bebida.

    Mesmo padrão de nomes de FEAT-002: checkbox name='ingredientes' value='<id>'
    indica inclusão e input name='qtd_ingrediente_<id>' traz a quantidade
    digitada (aceita vírgula ou ponto). Só ingredientes marcados COM quantidade
    > 0 entram na ficha; a conversão segue a convenção de unidade da bebida
    (valor direto, sem ×1000).

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
        itens[id_ingrediente] = _qtd_bebida_para_armazenar(valor, ingrediente.unidade)
    return itens, invalido


def _sincronizar_ficha_da_bebida(id_bebida: int, itens: dict) -> int:
    """Sincroniza a FichaTecnica_bebida com os ingredientes desejados.

    'itens' é {id_ingrediente: qtd_armazenada_inteira_positiva}. Espelha a
    sincronização do prato: cria os novos (criar_ficha_tecnica_bebida), atualiza
    os que mudaram de quantidade (atualizar_ficha_tecnica_bebida) e remove os
    desmarcados (deletar_ficha_tecnica_bebida). Apenas ids válidos (existentes em
    buscar_ingrediente_por_id) são considerados.

    Args:
        id_bebida (int): identificador da bebida.
        itens (dict): {id_ingrediente: qtd_armazenada} desejado.

    Returns:
        int: contagem final de ingredientes válidos na ficha (len dos desejados),
            usada pela regra de "avulsa" (exatamente 1 ingrediente).
    """
    desejados = {}
    for id_ingrediente, qtd in itens.items():
        if buscar_ingrediente_por_id(id_ingrediente) is not None:
            desejados[id_ingrediente] = qtd

    atuais = _ficha_atual_da_bebida(id_bebida)

    for id_ingrediente, qtd in desejados.items():
        if id_ingrediente not in atuais:
            criar_ficha_tecnica_bebida(id_bebida, id_ingrediente, qtd)
        elif atuais[id_ingrediente] != qtd:
            atualizar_ficha_tecnica_bebida(id_bebida, id_ingrediente, qtd)

    for id_ingrediente in set(atuais) - set(desejados):
        deletar_ficha_tecnica_bebida(id_bebida, id_ingrediente)

    return len(desejados)


def _ingredientes_catalogo() -> list:
    """Monta a lista de ingredientes disponíveis para o formulário de bebida.

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


# ===================== REGRA DE PREÇO POR PORÇÃO (avulsa) =====================
# A regra de "avulsa" é derivada no servidor: a bebida é avulsa se, e somente
# se, tiver EXATAMENTE 1 ingrediente na ficha técnica. Avulsa -> preço por porção
# exigido e > 0; 2+ ingredientes -> preço sempre 0. A contagem efetiva da ficha
# (após a sincronização) é a FONTE ÚNICA dessa regra; estes dois helpers separam
# a validação do texto (_ler_preco_porcao) da gravação coerente do valor final
# (_aplicar_preco_porcao), evitando duplicar a decisão em dois pontos.

def _ler_preco_porcao(valor_texto: str, avulsa: bool) -> Decimal:
    """Valida o texto do preço por porção conforme a bebida ser avulsa ou não.

    Não decide o valor final gravado (isso cabe a _aplicar_preco_porcao, após a
    sincronização da ficha). Apenas valida sintaxe/finitude/sinal e devolve o
    valor informado pelo admin, para que a gravação posterior possa aplicá-lo
    (quando avulsa) ou zerá-lo (quando não avulsa).

    Args:
        valor_texto (str): conteúdo do campo valor_unitario do formulário.
        avulsa (bool): se a bebida é avulsa (exatamente 1 ingrediente) segundo a
            contagem lida do formulário.

    Returns:
        Decimal: o preço informado (sempre válido e não negativo). Quando não
            avulsa e o campo veio vazio, retorna Decimal('0').

    Raises:
        ValueError: com a mensagem de flash apropriada quando o preço é exigido
            (avulsa sem valor > 0) ou inválido/negativo.
    """
    if avulsa:
        if not valor_texto:
            raise ValueError("Bebidas avulsas (1 ingrediente) exigem um preço "
                             "por porção maior que zero.")
        try:
            valor = _decimal_form(valor_texto)
        except InvalidOperation:
            raise ValueError("Valor unitário inválido.")
        if not valor.is_finite() or valor <= 0:
            raise ValueError("Bebidas avulsas (1 ingrediente) exigem um preço "
                             "por porção maior que zero.")
        return valor

    # Não avulsa: o preço será zerado, mas um valor informado precisa ser
    # sintaticamente/semanticamente válido para evitar confusão silenciosa.
    if not valor_texto:
        return Decimal("0")
    try:
        valor = _decimal_form(valor_texto)
    except InvalidOperation:
        raise ValueError("Valor unitário inválido.")
    if not valor.is_finite() or valor < 0:
        raise ValueError("O valor unitário deve ser válido e não negativo.")
    return valor


def _aplicar_preco_porcao(id_bebida: int, total_ingredientes: int,
                          valor_informado: Decimal) -> None:
    """Grava o preço por porção coerente com a contagem efetiva de ingredientes.

    Fonte ÚNICA da regra de avulsa: a bebida criada/atualizada antes da
    sincronização pode ter sido gravada com um preço provisório; aqui, após
    sincronizar a ficha, definimos o valor final a partir de total_ingredientes
    (recontagem autoritativa). Avulsa (==1) mantém o preço informado; caso
    contrário força 0 e, quando o admin digitou um preço > 0, emite um flash
    informativo explicando que o preço foi ignorado por a bebida não ser avulsa.

    Args:
        id_bebida (int): identificador da bebida já persistida.
        total_ingredientes (int): contagem final de ingredientes na ficha (saída
            de _sincronizar_ficha_da_bebida).
        valor_informado (Decimal): preço que o admin enviou (já validado).
    """
    valor_final = valor_informado if total_ingredientes == 1 else Decimal("0")
    atualizar_bebida(id_bebida, valor_unitario=valor_final)

    if total_ingredientes != 1 and valor_informado > Decimal("0"):
        flash("O preço por porção foi ignorado porque a bebida não é avulsa "
              "(tem 2 ou mais ingredientes).", "info")


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
    ingredientes_catalogo = _ingredientes_catalogo()
    # mapa auxiliar id -> unidade para converter a ficha de volta à exibição.
    unidade_por_ingrediente = {i["id"]: i["unidade"] for i in ingredientes_catalogo}

    editar = request.args.get("editar", "")
    atual = None
    valores = {}
    ficha_bebida = {}
    if editar:
        atual = next((i for i in itens if str(i["id"]) == str(editar)), None)
        if atual:
            valores = dict(atual)
            # Pré-carrega a ficha atual (exibição == armazenado para bebida).
            for id_ingrediente, qtd in _ficha_atual_da_bebida(atual["id"]).items():
                unidade = unidade_por_ingrediente.get(id_ingrediente, "")
                ficha_bebida[id_ingrediente] = _qtd_bebida_para_exibir(qtd, unidade)

    return render_template(
        "catalogo_admin.html",
        tipo="bebidas",
        itens=itens,
        opcoes=_OPCOES_BEBIDA,
        servicos_catalogo={},
        ingredientes_catalogo=ingredientes_catalogo,
        ficha_bebida=ficha_bebida,
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

    # O preço (valor_unitario) NÃO é mais obrigatório de forma incondicional:
    # a exigência passa a depender da bebida ser avulsa (exatamente 1
    # ingrediente). Aqui só validamos nome/descrição; o preço é tratado adiante.
    if not nome or not descricao:
        flash("Preencha nome e descrição.", "danger")
        return voltar

    # Regra de negócio (servidor é a autoridade): a bebida precisa de ficha
    # técnica com PELO MENOS 1 ingrediente. Ler a seleção antes de criar para
    # rejeitar formulários inválidos sem poluir o banco.
    itens_ficha, invalido = _ler_ingredientes_do_form(request.form)
    if invalido:
        flash("Informe uma quantidade válida (maior que zero) para cada "
              "ingrediente selecionado.", "danger")
        return voltar
    if not itens_ficha:
        flash("Selecione ao menos um ingrediente para a bebida.", "danger")
        return voltar

    # Preço por porção: só é exigido quando a bebida é AVULSA (exatamente 1
    # ingrediente). Validamos o texto do preço aqui (parse/finitude/sinal), mas
    # NÃO decidimos ainda o valor gravado: a contagem final de ingredientes
    # (após a sincronização) é a fonte única da regra de avulsa.
    avulsa = len(itens_ficha) == 1
    try:
        valor_informado = _ler_preco_porcao(valor_texto, avulsa)
    except ValueError as erro:
        flash(str(erro), "danger")
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

    # Ordem das operações: cria a bebida (com preço provisório) -> obtém o id ->
    # sincroniza a ficha -> a contagem efetiva pós-sync define o preço final
    # coerente (fonte única da regra avulsa), gravado com _aplicar_preco_porcao.
    try:
        bebida = criar_bebida(nome, descricao, valor_informado, imagem_slug=imagem_slug)
    except SQLAlchemyError:
        flash("Não foi possível criar a bebida.", "danger")
        return voltar

    # Sequência pós-entidade (sincronização da ficha + preço coerente): cada
    # função do model commita individualmente (como no resto do projeto), então
    # não há transação compartilhada aqui. Mesmo assim, envolvemos a sequência
    # num try/except para SINALIZAR ao admin uma falha de banco (em vez de deixar
    # a exceção escapar com estado parcial e sem aviso), alinhando ao tratamento
    # de erro já aplicado na criação da entidade.
    try:
        total_ingredientes = _sincronizar_ficha_da_bebida(bebida.id_bebida, itens_ficha)
        _aplicar_preco_porcao(bebida.id_bebida, total_ingredientes, valor_informado)
    except SQLAlchemyError:
        db.session.rollback()
        flash("Não foi possível salvar a ficha técnica/preço da bebida.", "danger")
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

    # Preço condicional (ver criar_bebida_route): só nome/descrição são
    # obrigatórios aqui; a exigência do preço depende da bebida ser avulsa.
    if not nome or not descricao:
        flash("Preencha nome e descrição.", "danger")
        return voltar

    # A bebida continua exigindo ao menos 1 ingrediente na ficha técnica.
    itens_ficha, invalido = _ler_ingredientes_do_form(request.form)
    if invalido:
        flash("Informe uma quantidade válida (maior que zero) para cada "
              "ingrediente selecionado.", "danger")
        return voltar
    if not itens_ficha:
        flash("Selecione ao menos um ingrediente para a bebida.", "danger")
        return voltar

    # Preço por porção: exigido (> 0) apenas quando avulsa (1 ingrediente); caso
    # contrário o valor gravado será 0. Aqui só validamos o texto; a decisão do
    # valor final é tomada após a sincronização da ficha (fonte única da regra).
    avulsa = len(itens_ficha) == 1
    try:
        valor_informado = _ler_preco_porcao(valor_texto, avulsa)
    except ValueError as erro:
        flash(str(erro), "danger")
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

    # Ordem das operações: atualiza os dados básicos (com preço provisório) ->
    # sincroniza a ficha -> a contagem efetiva pós-sync define o preço final
    # coerente, gravado por _aplicar_preco_porcao (estado final sempre coerente
    # com a regra de avulsa).
    try:
        sucesso = atualizar_bebida(id_bebida, nome=nome, descricao=descricao,
                                   valor_unitario=valor_informado, imagem_slug=imagem_slug)
    except SQLAlchemyError:
        flash("Não foi possível atualizar a bebida.", "danger")
        return voltar

    if not sucesso:
        flash("Bebida não encontrada.", "danger")
        return voltar

    # Sequência pós-entidade: ver comentário em criar_bebida_route. Sinaliza a
    # falha de banco com flash 'danger' em vez de deixá-la escapar.
    try:
        total_ingredientes = _sincronizar_ficha_da_bebida(id_bebida, itens_ficha)
        _aplicar_preco_porcao(id_bebida, total_ingredientes, valor_informado)
    except SQLAlchemyError:
        db.session.rollback()
        flash("Não foi possível salvar a ficha técnica/preço da bebida.", "danger")
        return voltar

    flash("Bebida atualizada.", "success")
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
