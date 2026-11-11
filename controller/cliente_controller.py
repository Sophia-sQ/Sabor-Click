"""Rotas do cliente: pedidos, endereços, serviços, carrinho e perfil."""
    
import json
from datetime import date, datetime, time
from decimal import Decimal
from zoneinfo import ZoneInfo

from flask import (
    Blueprint,
    Response,
    abort,
    current_app,
    flash,
    jsonify,
    redirect,
    render_template,
    request,
    session,
    url_for,
)

from model.pedido_model import (
    atualizar_pedido,
    buscar_pedido_por_id,
    buscar_bebida_por_id,
    listar_bebidas_do_pedido,
    buscar_cardapios_pedido,
    criar_pedido,
    listar_pedidos_por_cliente,
    listar_bebidas,
)
from model.servico_model import (
    buscar_cardapio_por_id,
    buscar_cardapio_por_nome,
    buscar_servico_por_id,
    buscar_servico_por_slug,
    listar_cardapios_do_servico,
)
from model.usuario_model import (
    adicionar_endereco,
    atualizar_endereco,
    atualizar_usuario,
    buscar_endereco_por_id,
    buscar_usuario_por_id,
    listar_enderecos_do_usuario,
    deletar_endereco,
    registrar_log,
)
from services import enviar_email_nao_responda
from endereco_evento import apresentar_endereco_evento, validar_endereco_evento

cliente_bp = Blueprint("cliente", __name__, url_prefix="/home")

# Mapa nome do prato -> slug usada em docs/imagens-menu.json
# Mapa id_cardapio (ordem fixa dos seeds) -> (slug da imagem em docs/imagens-menu.json,
# chave do preço em docs/precos-menu.json). Usa o id porque Cardapio.nome é gravado
# normalizado (minúsculo/sem acento) e não casa com as chaves dos JSON.
_CARDAPIO_POR_ID = {
    1:  ("feijoada", "Feijoada completa"),
    2:  ("bobo-camarao", "Bobó de camarão"),
    3:  ("tilapia", "Tilápia com alcaparras"),
    4:  ("strogonoff", "Strogonoff de filé-mignon"),
    5:  ("nhoque", "Nhoque ao molho"),
    6:  ("risoto", "Risoto de cogumelos"),
    7:  ("escondidinho", "Escondidinho de carne-seca"),
    8:  ("ravioli", "Ravioli de queijo"),
    9:  ("salgados-completo", "Salgados completo"),
    10: ("salgados-reduzido", "Salgados reduzido"),
    11: ("hamburguer", "Hambúrguer tradicional"),
    12: ("smash", "Hambúrguer smash"),
    13: ("bacon", "Hambúrguer mega bacon"),
    14: ("mexicano", "Mexicano"),
    15: ("boteco", "Boteco brasileiro"),
    16: ("sem-alcool", "Sem álcool"),
    17: ("com-alcool", "Com álcool"),
    18: ("misto", "Misto"),
}

@cliente_bp.get("")
def pagina_inicial():
    """Renderiza a home page."""
    return render_template("home.html")

# =========================== PEDIDO ===========================

@cliente_bp.post("/carrinho/fazer_pedido")
def fazer_pedido():
    """Valida o checkout e registra o pedido com os valores do catálogo."""
    endereco = _endereco_evento_selecionado()
    if endereco is None:
        flash("Escolha um endereço válido para o evento.", "danger")
        return redirect(url_for("cliente.mostrar_carrinho"))

    itens, total_centavos = _itens_carrinho()
    try:
        data_evento = date.fromisoformat(request.form.get("data_evento", ""))
        hora_inicio = time.fromisoformat(request.form.get("hora_inicio", ""))
        hora_fim = time.fromisoformat(request.form.get("hora_fim", ""))
        if (data_evento < datetime.now(ZoneInfo("America/Sao_Paulo")).date()
                or hora_inicio.tzinfo or hora_fim.tzinfo or hora_fim <= hora_inicio):
            raise ValueError
    except ValueError:
        flash("Informe uma data válida e um horário de término posterior ao início.", "danger")
        return redirect(url_for("cliente.checkout"))

    selecionadas = request.form.get("bebidas", "{}")
    try:
        quantidades = json.loads(selecionadas)
        if not isinstance(quantidades, dict):
            raise ValueError
        catalogo = {bebida["id"]: bebida for bebida in _catalogo_bebidas()}
        bebidas = []
        for codigo, qtd in quantidades.items():
            bebida = catalogo.get(codigo)
            if bebida is None or bebida["preco"] is None or type(qtd) is not int or not 1 <= qtd <= 99:
                raise ValueError
            valor = Decimal(str(bebida["preco"])) * qtd
            total_centavos += int(valor * 100)
            bebidas.append({"id_bebida": int(codigo), "qtd": qtd, "valor_total": valor})
    except ValueError:
        flash("Confira as bebidas selecionadas antes de enviar o pedido.", "danger")
        return redirect(url_for("cliente.checkout"))

    if not itens and not bebidas:
        flash("Adicione itens ao carrinho antes de confirmar.", "danger")
        return redirect(url_for("cliente.mostrar_carrinho"))

    convidados = max((item["qtd"] for item in itens), default=1)
    if not itens:
        convidados = request.form.get("convidados", type=int)
        if convidados is None or not 1 <= convidados <= 500:
            flash("Informe de 1 a 500 convidados.", "danger")
            return redirect(url_for("cliente.checkout"))

    pedido = criar_pedido(
        id_cliente=session["id"], id_endereco=endereco.id_endereco,
        num_convidados=convidados, valor_total=Decimal(total_centavos) / 100,
        data_evento=data_evento, hora_inicio=hora_inicio, hora_fim=hora_fim,
        cardapios=itens, observacao=request.form.get("obs", "").strip()[:1000] or None,
        bebidas=bebidas,
    )
    if pedido is None:
        flash("Não foi possível registrar seu pedido. Tente novamente.", "danger")
        return redirect(url_for("cliente.checkout"))

    id_pedido = pedido.id_pedido
    session.pop("carrinho", None)
    session.pop("endereco_evento_id", None)
    session["pedido_recebido"] = id_pedido
    try:
        cliente = buscar_usuario_por_id(session["id"])
        mensagem = f"Recebemos o pedido nº {id_pedido}. Ele aguarda confirmação."
        enviar_email_nao_responda("Pedido recebido", cliente.email_criptografado, mensagem, f"<p>{mensagem}</p>")
    except Exception:
        current_app.logger.exception("Falha ao enviar e-mail do pedido %s", id_pedido)
    return redirect(url_for("cliente.pedido_recebido", id_pedido=id_pedido), code=303)


@cliente_bp.get("/pedido/<int:id_pedido>")
def pedido_recebido(id_pedido):
    pedido = buscar_pedido_por_id(id_pedido)
    if pedido is None or pedido.id_cliente != session.get("id"):
        return redirect(url_for("cliente.mostrar_carrinho"))
    limpar_bebidas = session.get("pedido_recebido") == id_pedido
    if limpar_bebidas:
        session.pop("pedido_recebido", None)
    return render_template("checkout.html", pedido=pedido, limpar_bebidas=limpar_bebidas)


@cliente_bp.post("/cancelar_pedido/<int:id_pedido>")
def cancelar_pedido(id_pedido):
    pedido = buscar_pedido_por_id(id_pedido)
    if pedido is None or pedido.id_cliente != session.get("id"):
        return redirect(url_for("cliente.mostrar_carrinho"))
    if pedido.status == "aguardando" and atualizar_pedido(id_pedido, status="cancelado"):
        flash("Pedido cancelado.", "success")
    else:
        flash("O pedido não pôde ser cancelado.", "danger")
    return redirect(url_for("cliente.pedido_recebido", id_pedido=id_pedido))

# =========================== BEBIDA ===========================

def _catalogo_bebidas():
    from bebidas_data import formatar_bebidas
    return formatar_bebidas([dict(id=b.id_bebida, nome=b.nome,
        descricao=b.descricao, preco=b.valor_unitario) for b in listar_bebidas()])


@cliente_bp.get("/bebidas")
def bebidas_avulsas():
    return render_template("bebidas.html", bebidas=_catalogo_bebidas(),
                           carrinho_url=url_for("cliente.mostrar_carrinho"))


# =========================== ENDERECO ===========================

def _endereco_evento_selecionado():
    id_endereco = session.get("endereco_evento_id")
    endereco = buscar_endereco_por_id(id_endereco) if id_endereco else None
    if endereco is None or endereco.id_usuario != session.get("id"):
        session.pop("endereco_evento_id", None)
        return None
    return endereco


def _apresentar_endereco_cadastrado(endereco):
    cep = endereco.cep.replace("-", "")
    return apresentar_endereco_evento({
        "rua": endereco.logradouro,
        "numero": endereco.numero,
        "complemento": endereco.complemento or "",
        "bairro": endereco.bairro,
        "cidade": endereco.cidade,
        "cep": f"{cep[:5]}-{cep[5:]}" if len(cep) == 8 else endereco.cep,
        "uf": endereco.uf or "",
    })


@cliente_bp.post("/carrinho/endereco")
def selecionar_endereco():
    if not request.is_json:
        return jsonify(erro="Envie os dados do endereço em JSON."), 415
    dados = request.get_json(silent=True)
    if not isinstance(dados, dict):
        return jsonify(erro="Informe os dados do endereço."), 400
    if "id_endereco" in dados:
        id_endereco = dados["id_endereco"]
        if not isinstance(id_endereco, int) or isinstance(id_endereco, bool):
            return jsonify(erro="Endereço inválido."), 400
        endereco = buscar_endereco_por_id(id_endereco)
        if endereco is None or endereco.id_usuario != session.get("id"):
            return jsonify(erro="Endereço não encontrado."), 404
    else:
        try:
            campos = validar_endereco_evento(dados)
        except ValueError as erro:
            return jsonify(erro=str(erro)), 400
        atributos = {
            "logradouro": campos["rua"], "numero": campos["numero"],
            "complemento": campos["complemento"], "bairro": campos["bairro"],
            "cidade": campos["cidade"], "cep": campos["cep"].replace("-", ""), "uf": campos["uf"],
        }
        # Uma repetição do envio reutiliza um endereço já cadastrado.
        endereco = next((item for item in listar_enderecos_do_usuario(session["id"])
                         if all((getattr(item, chave) or "") == valor for chave, valor in atributos.items())), None)
        if endereco is None:
            endereco = adicionar_endereco(nome="Endereço do evento", **atributos)
        if endereco is None:
            return jsonify(erro="Não foi possível salvar o endereço. Tente novamente."), 500
    session["endereco_evento_id"] = endereco.id_endereco
    return jsonify(_apresentar_endereco_cadastrado(endereco))


@cliente_bp.get("/checkout")
def checkout():
    endereco = _endereco_evento_selecionado()
    if endereco is None:
        flash("Escolha o endereço do evento no carrinho.", "danger")
        return redirect(url_for("cliente.mostrar_carrinho"))
    itens, total = _itens_carrinho()
    return render_template("checkout.html", itens_checkout=itens, total_centavos=total,
                           bebidas=_catalogo_bebidas(), **_apresentar_endereco_cadastrado(endereco))


@cliente_bp.get("/endereco")
def endereco():
    """Redireciona para a âncora de endereços na página de perfil."""
    return redirect(url_for("cliente.perfil") + "#enderecos")

@cliente_bp.post("/adicionar_endereco")
def novo_endereco():
    """Adiciona um novo endereço ao cliente logado a partir do formulário.

    Valida o CEP e sinaliza o resultado via flash.

    Returns:
        Response: redirecionamento para a página de endereços.
    """
    nome=request.form.get("nome").strip()
    logadouro=request.form.get("logadouro").strip()
    numero=request.form.get("num").strip()
    complemento=request.form.get("compl").strip()
    bairro=request.form.get("bairro").strip()
    cidade=request.form.get("cidade").strip()
    cep=request.form.get("cep").replace("-", "").strip()

    if not cep.isdigit():
        flash("CEP inválido", "danger")
        return redirect(url_for("cliente.endereco"))

    if adicionar_endereco(nome, logadouro, numero, complemento, bairro, cidade, cep) is None:
        flash("Falha no cadastro de novo endereço", "danger")
        return redirect(url_for("cliente.endereco"))

    flash("Endereço cadastrado com sucesso.", "success")
    return redirect(url_for("cliente.endereco"))

@cliente_bp.post("/endereco/atualizar/<int:id_endereco>")
def editar_endereco(id_endereco):
    """Atualiza um endereço do usuário logado a partir do formulário.

    Garante que o endereço pertence ao usuário antes de atualizar.

    Args:
        id_endereco (int): identificador do endereço.

    Returns:
        Response: redirecionamento para a página de endereços.
    """
    endereco = buscar_endereco_por_id(id_endereco)

    # garante que o endereço existe e pertence ao usuário logado
    if endereco is None or endereco.id_usuario != session.get("id"):
        flash("Endereço não encontrado.", "danger")
        return redirect(url_for("cliente.endereco"))

    nome = (request.form.get("nome") or "").strip() or None
    logradouro = (request.form.get("logadouro") or "").strip() or None
    numero = (request.form.get("num") or "").strip() or None
    complemento = (request.form.get("compl") or "").strip()      # pode ser vazio (opcional)
    bairro = (request.form.get("bairro") or "").strip() or None
    cidade = (request.form.get("cidade") or "").strip() or None
    cep = (request.form.get("cep") or "").replace("-", "").strip() or None

    if cep is not None and not cep.isdigit():
        flash("CEP inválido.", "danger")
        return redirect(url_for("cliente.endereco"))

    if not atualizar_endereco(id_endereco, nome=nome, logradouro=logradouro, numero=numero,
                              complemento=complemento, bairro=bairro, cidade=cidade, cep=cep):
        flash("Falha ao atualizar o endereço.", "danger")
        return redirect(url_for("cliente.endereco"))

    flash("Endereço atualizado com sucesso.", "success")
    return redirect(url_for("cliente.endereco"))

@cliente_bp.post("/endereco/deletar/<int:id_endereco>")
def remover_endereco(id_endereco):
    """Remove um endereço do usuário logado.

    Garante que o endereço pertence ao usuário antes de remover.

    Args:
        id_endereco (int): identificador do endereço.

    Returns:
        Response: redirecionamento para a página de endereços.
    """
    endereco = buscar_endereco_por_id(id_endereco)

    # garante que o endereço existe e pertence ao usuário logado
    if endereco is None or endereco.id_usuario != session.get("id"):
        flash("Endereço não encontrado.", "danger")
        return redirect(url_for("cliente.endereco"))

    if not deletar_endereco(id_endereco):
        flash("Falha ao remover o endereço.", "danger")
        return redirect(url_for("cliente.endereco"))

    flash("Endereço removido com sucesso.", "success")
    return redirect(url_for("cliente.endereco"))

# ================== SERVICO ==================

@cliente_bp.get("/servico")
def home_servico():
    """Redireciona para a âncora de serviços na home page."""
    # garante que não vai existir um /servico 404

    return redirect(url_for("cliente.home") + "#servicos") 

@cliente_bp.get("/servico/<string:slug>")
def mostrar_servico(slug):
    """Exibe os cardápios disponíveis para um serviço (rota dinâmica).

    Busca o serviço pelo slug e lista seus cardápios para renderização no Jinja2.

    Args:
        slug (str): slug do serviço.

    Returns:
        str: template do serviço com a lista de cardápios.
    """
    servico = buscar_servico_por_slug(slug)
    if servico is None:
        flash("Serviço não encontrado.", "danger")
        return redirect(url_for("cliente.home_servico"))

    import json
    from pathlib import Path

    base = Path(current_app.root_path)
    with open(base / "docs" / "precos-menu.json", encoding="utf-8") as arq:
        precos = json.load(arq).get("precos", {})
    with open(base / "docs" / "imagens-menu.json", encoding="utf-8") as arq:
        imagens = json.load(arq)

    associacoes = listar_cardapios_do_servico(servico.id_servico) or []

    cardapios = []
    for associacao in associacoes:
        cardapio = buscar_cardapio_por_id(associacao.id_cardapio)
        if cardapio is None:
            continue

        slug_img, nome_preco = _CARDAPIO_POR_ID.get(cardapio.id_cardapio, (None, None))

        preco_pessoa = precos.get(nome_preco)
        if preco_pessoa is None:
            preco_pessoa = int(round(float(cardapio.preco_base) * 100))

        dados_img = imagens.get(slug_img, {}) if slug_img else {}
        arquivo = dados_img.get("arquivo")
        imagem_rel = arquivo[len("static/"):] if arquivo and arquivo.startswith("static/") else arquivo

        cardapios.append({
            "id_cardapio": cardapio.id_cardapio,
            "nome": cardapio.nome,
            "descricao": cardapio.descricao,
            "preco": preco_pessoa,
            "imagem": imagem_rel,
            "versao": dados_img.get("versao"),
        })

    return render_template("servico.html", servico=servico, cardapios=cardapios)

# ================== CARRINHO DE COMPRAS ==================
def _carrinho() -> list:
    """Retorna o carrinho da sessão, criando-o (lista vazia) se não existir."""
    return session.setdefault("carrinho", [])

def _itens_carrinho():
    """Carrega os cardápios e calcula os subtotais em centavos.

    Cruza cada item de session['carrinho'] (via id_cardapio -> nome do cardápio)
    com os preços de docs/precos-menu.json (por nome) e com as imagens de
    docs/imagens-menu.json (por slug da imagem). O subtotal é o preço por pessoa
    (centavos) multiplicado pela quantidade de convidados.

    Returns:
        tuple: itens do carrinho e total em centavos.
    """
    import json
    from pathlib import Path

    base = Path(current_app.root_path)
    with open(base / "docs" / "precos-menu.json", encoding="utf-8") as arq:
        precos = json.load(arq).get("precos", {})
    with open(base / "docs" / "imagens-menu.json", encoding="utf-8") as arq:
        imagens = json.load(arq)

    carrinho = session.get("carrinho", [])
    itens_carrinho = []
    total_centavos = 0

    for numero, item in enumerate(carrinho, start=1):
        cardapio = buscar_cardapio_por_id(item.get("id_cardapio"))
        servico = buscar_servico_por_id(item.get("id_servico"))
        if cardapio is None or servico is None or not any(
            vinculo.id_cardapio == cardapio.id_cardapio
            for vinculo in listar_cardapios_do_servico(servico.id_servico) or []
        ):
            continue

        qtd = item.get("qtd", 0)
        slug_img, nome_preco = _CARDAPIO_POR_ID.get(cardapio.id_cardapio, (None, None))

        # preço por pessoa (centavos): JSON por id->nome; fallback para preco_base do banco
        preco_pessoa = precos.get(nome_preco)
        if preco_pessoa is None:
            preco_pessoa = int(round(float(cardapio.preco_base) * 100))

        subtotal_centavos = preco_pessoa * qtd
        total_centavos += subtotal_centavos

        # imagem: id -> slug -> entrada do JSON (campo "arquivo" já vem a partir de static/)
        dados_img = imagens.get(slug_img, {}) if slug_img else {}
        arquivo = dados_img.get("arquivo")  # ex.: "static/images/menu/feijoada.jpg"
        # o template usa url_for('static', filename=...), então removemos o prefixo "static/"
        imagem_rel = arquivo[len("static/"):] if arquivo and arquivo.startswith("static/") else arquivo
        versao = dados_img.get("versao")

        itens_carrinho.append({
            "id_cardapio": item.get("id_cardapio"),
            "id_servico": item.get("id_servico"),
            "numero": numero,
            "nome": cardapio.nome,
            "descricao": cardapio.descricao,
            "imagem": imagem_rel,   # ex.: "images/menu/feijoada.jpg" (ou None)
            "versao": versao,
            "qtd": qtd,
            "subtotal": subtotal_centavos,  # centavos
            "inclui_bebidas": servico is not None and servico.slug == "bar",
        })

    return itens_carrinho, total_centavos


@cliente_bp.get("/carrinho")
def mostrar_carrinho():
    """Exibe a página de carrinho para o usuário."""
    endereco = _endereco_evento_selecionado()
    dados_endereco = _apresentar_endereco_cadastrado(endereco) if endereco else {}
    itens, total_centavos = _itens_carrinho()
    return render_template("carrinho.html", itens_carrinho=itens, total_centavos=total_centavos,
                           perfil_url=url_for("cliente.perfil"), bebidas=_catalogo_bebidas(),
                           bebidas_url=url_for("cliente.bebidas_avulsas"),
                           checkout_url=url_for("cliente.checkout"),
                           salvar_endereco_url=url_for("cliente.selecionar_endereco"),
                           login_url=url_for("auth.login") if "id" not in session else None,
                           enderecos_cadastrados=listar_enderecos_do_usuario(session["id"]) if "id" in session else [],
                           **dados_endereco)

@cliente_bp.post("/carrinho/adicionar-do-menu")
def adicionar_do_menu():
    """Adiciona o cardápio público ao carrinho com os dados do catálogo."""
    from menu_data import cardapios_do_menu

    nome = request.form.get("nome")
    qtd = request.form.get("qtd", type=int)
    if nome not in cardapios_do_menu or qtd is None or not 10 <= qtd <= 500:
        flash("Escolha um prato e informe uma quantidade de 10 a 500 pessoas.", "danger")
        return redirect(url_for("cliente.menu"))

    slug, nome_cadastrado = cardapios_do_menu[nome]
    servico = buscar_servico_por_slug(slug)
    cardapio = buscar_cardapio_por_nome(nome_cadastrado)
    if servico is None or cardapio is None or not any(
        vinculo.id_cardapio == cardapio.id_cardapio
        for vinculo in listar_cardapios_do_servico(servico.id_servico) or []
    ):
        flash("Este prato está indisponível no momento.", "danger")
        return redirect(url_for("cliente.menu"))

    item = {"id_servico": servico.id_servico, "id_cardapio": cardapio.id_cardapio, "qtd": qtd}
    carrinho = _carrinho()
    existente = next((atual for atual in carrinho if atual["id_cardapio"] == item["id_cardapio"]), None)
    if existente is None:
        if any(atual["id_servico"] == servico.id_servico for atual in carrinho):
            flash("Já existe um cardápio deste serviço no carrinho.", "danger")
            return redirect(url_for("cliente.menu", _anchor="retorno-carrinho"))
        carrinho.append(item)
    else:
        existente.update(item)
    session["carrinho"] = carrinho
    flash(f"{nome} para {qtd} pessoas está no carrinho.", "success")
    return redirect(url_for("cliente.menu", _anchor="retorno-carrinho"))

@cliente_bp.post("/carrinho/adicionar")
def adicionar():
    """Adiciona (ou atualiza a quantidade de) um cardápio no carrinho.

    Valida o serviço, o cardápio e o número de convidados (entre 10 e 500).

    Returns:
        Response: redirecionamento para a página do serviço.
    """

    slug_servico = request.form.get("slug_servico")
    id_cardapio = request.form.get("id_cardapio", type=int)
    qtd_convidados = request.form.get("qtd", type=int)


    if (not slug_servico or id_cardapio is None or qtd_convidados is None
            or qtd_convidados < 10 or qtd_convidados > 500):
        flash("Valor(es) inválido(s).", "danger")
        return redirect(url_for("cliente.mostrar_servico", slug=slug_servico) if slug_servico else url_for("cliente.menu"))

    servico = buscar_servico_por_slug(slug_servico)

    cardapio = buscar_cardapio_por_id(id_cardapio)

    if servico is None or cardapio is None or not any(
        vinculo.id_cardapio == id_cardapio
        for vinculo in listar_cardapios_do_servico(servico.id_servico) or []
    ):
        flash("Serviço ou cardápio inválidos.", "danger")
        return redirect(url_for("cliente.mostrar_servico", slug=slug_servico))

    novo = {"id_servico": servico.id_servico,
            "id_cardapio": id_cardapio,
            "qtd": qtd_convidados,
           }

    carrinho = _carrinho()

    existente = next((
        item for item in carrinho
        if item["id_cardapio"] == id_cardapio
        ), None,
    )

    if existente:
        existente["qtd"] = qtd_convidados
    else:
        # Regra: não permitir dois cardápios do mesmo serviço no carrinho.
        outro_do_servico = next((
            item for item in carrinho
            if item["id_servico"] == servico.id_servico
            and item["id_cardapio"] != id_cardapio
            ), None,
        )
        if outro_do_servico:
            flash("Já existe um cardápio deste serviço no carrinho.", "danger")
            return redirect(url_for("cliente.mostrar_servico", slug=slug_servico))
        carrinho.append(novo)

    session["carrinho"] = carrinho
    flash("Produto adicionado ao carrinho.", "success")
    return redirect(url_for("cliente.mostrar_servico", slug=slug_servico))

@cliente_bp.post("/carrinho/remover/<int:id_cardapio>/")
def remover(id_cardapio):
    """Remove um item do carrinho pelo id do cardápio.

    Args:
        id_cardapio (int): identificador do cardápio a remover.

    Returns:
        Response: redirecionamento para a página do carrinho.
    """
    carrinho = _carrinho()

    posicao = next(
        (
            indice
            for indice, item in enumerate(carrinho)
            if item["id_cardapio"] == id_cardapio
        ),
        None,
    )

    if posicao is not None:
        carrinho.pop(posicao)
        session["carrinho"] = carrinho
        flash("Item removido do carrinho.", "success")
    else:
        flash("Item não encontrado no carrinho.", "danger")

    return redirect(url_for("cliente.mostrar_carrinho"))

# ================== PERFIL DO CLIENTE ==================

@cliente_bp.get("/perfil")
def perfil():
    """Exibe a página de perfil com dados do usuário e seus endereços.

    Descriptografa e-mail e CPF para exibição.

    Returns:
        Response | str: redirecionamento ao login se não houver usuário; caso
        contrário, o template de perfil renderizado.
    """
    from security import descriptografar
    from model.usuario_model import listar_enderecos_do_usuario

    usuario = buscar_usuario_por_id(session.get("id"))
    if usuario is None:
        return redirect(url_for("auth.login"))
    pessoa = {"nome": usuario.nome,
              "email": descriptografar(usuario.email_criptografado),
              "cpf": descriptografar(usuario.cpf_criptografado)}
    campos = ("id_endereco", "nome", "logradouro", "numero", "complemento", "bairro", "cidade", "cep")
    enderecos = [{campo: getattr(endereco, campo) for campo in campos}
                 for endereco in listar_enderecos_do_usuario(usuario.id_usuario)]
    return render_template("perfil.html", pessoa=pessoa, enderecos=enderecos)

@cliente_bp.get("/perfil/dados")
def dados_perfil() -> Response:
    """Retorna, em JSON, os dados do perfil, do pedido ativo e seus detalhes.

    Inclui usuário (com e-mail/CPF descriptografados), pedido ativo, serviços e
    cardápios, bebidas e endereço, com valores monetários formatados.

    Returns:
        Response: JSON com 'usuario', 'pedido', 'servicos', 'bebidas' e 'endereco'.
    """
    from security import descriptografar
    from utils import formatar_moeda

    id_usuario = session["id"]
    usuario = buscar_usuario_por_id(id_usuario)
    if usuario is None:
        abort(404)

    pedido = next(
        (p for p in listar_pedidos_por_cliente(id_usuario)
         if p.status not in ("cancelado", "concluido")),
        None,
    )
    cardapios = buscar_cardapios_pedido(pedido.id_pedido) if pedido else []
    servicos = {
        servico.nome: [
            cardapio.nome,
            formatar_moeda(cardapio.preco_base * (item.qtd or pedido.num_convidados) * 100),
        ]
        for item in cardapios
        if (servico := buscar_servico_por_id(item.id_servico))
        and (cardapio := buscar_cardapio_por_id(item.id_cardapio))
    }

    endereco = buscar_endereco_por_id(pedido.id_endereco) if pedido else None
    bebidas = (listar_bebidas_do_pedido(pedido.id_pedido) or []) if pedido else []
    valor_total = formatar_moeda(sum(bebida.valor_total for bebida in bebidas) * 100)

    return jsonify({
        "usuario": {
            "id": usuario.id_usuario,
            "nome": usuario.nome,
            "cpf": descriptografar(usuario.cpf_criptografado),
            "email": descriptografar(usuario.email_criptografado),
        },
        "pedido": {
            "id": pedido.id_pedido,
            "status": pedido.status,
            "num_convidados": pedido.num_convidados,
            "valor_total": formatar_moeda(pedido.valor_total * 100),
            "data_evento": pedido.data_evento.isoformat() if pedido.data_evento else None,
            "hora_inicio": pedido.hora_inicio.isoformat() if pedido.hora_inicio else None,
            "hora_fim": pedido.hora_fim.isoformat() if pedido.hora_fim else None,
            "observacao": pedido.observacao,
        } if pedido else None,
        "servicos": servicos,
        "bebidas": {
            "itens": [
                {
                    "nome": buscar_bebida_por_id(b.id_bebida).nome,
                    "qtd": b.qtd,
                    "valor_un": b.valor_total / b.qtd,
                }
                for b in (bebidas or [])
            ],
            "valor_total": valor_total,
        },
        "endereco": {
            "nome": endereco.nome,
            "logradouro": endereco.logradouro,
            "numero": endereco.numero,
            "complemento": endereco.complemento,
            "bairro": endereco.bairro,
            "cidade": endereco.cidade,
            "cep": endereco.cep,
        } if endereco else None,
    })

@cliente_bp.post("/perfil/atualizar")
def atualizar_perfil():
    """Atualiza os dados cadastrais (nome, e-mail, CPF, senha) do usuário logado.

    Valida a sessão, o CPF e a força da senha quando informados.

    Returns:
        Response: redirecionamento ao login (sessão expirada) ou ao perfil.
    """
    from security import validar_senha_forte

    id_usuario = session.get("id")
    if not id_usuario:
        flash("Sessão expirada. Faça login novamente.", "danger")
        return redirect(url_for("auth.login"))  # ajuste para o nome real da sua rota de login

    nome = (request.form.get("nome") or "").strip() or None
    email = (request.form.get("email") or "").strip() or None
    cpf = (request.form.get("cpf") or "").replace(".", "").replace("-", "").strip() or None
    nova_senha = (request.form.get("senha") or "").strip() or None

    # valida CPF (apenas dígitos e 11 posições) quando enviado
    if cpf is not None and (not cpf.isdigit() or len(cpf) != 11):
        flash("CPF inválido.", "danger")
        return redirect(url_for("cliente.perfil"))  # ajuste p/ sua rota de perfil

    # valida força da senha quando enviada
    if nova_senha is not None and not validar_senha_forte(nova_senha):
        flash("A nova senha não atende aos requisitos de segurança.", "danger")
        return redirect(url_for("cliente.perfil"))

    resultado = atualizar_usuario(
        id_usuario,
        nome=nome,
        email=email,
        cpf=cpf,
        nova_senha=nova_senha,
    )

    if resultado is False:
        flash("Não foi possível atualizar os dados.", "danger")
        return redirect(url_for("cliente.perfil"))

    flash("Dados atualizados com sucesso.", "success")
    return redirect(url_for("cliente.perfil"))




def home():
    """Renderiza a home page."""
    return render_template("home.html")


def menu():
    """Renderiza a página de menu com as categorias de cardápio."""
    from menu_data import categorias
    return render_template("menu.html", categorias=categorias)
