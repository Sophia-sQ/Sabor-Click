"""Rotas do cliente: pedidos, endereços, serviços, carrinho e perfil."""
    
import json
from datetime import date, datetime, time
from decimal import Decimal
from zoneinfo import ZoneInfo

from flask import (
    Blueprint,
    Response,
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
    buscar_servico_por_id,
    buscar_servico_por_slug,
    listar_cardapios,
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
from services import apresentar_endereco_evento, validar_endereco_evento

cliente_bp = Blueprint("cliente", __name__, url_prefix="/home")

# Mapa id_cardapio (ordem fixa dos seeds) -> (slug da imagem em docs/imagens-menu.json,
# nome de exibição). O preço vem do banco (Cardapio.preco_base, em centavos); o
# segundo elemento da tupla é mantido apenas como referência de nome de exibição.
# Usa o id porque Cardapio.nome é gravado normalizado (minúsculo/sem acento) e não
# casa com as chaves do JSON de imagens.
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

# Seções exibidas no menu público. A categoria de cada cardápio é derivada da
# faixa de id do mapeamento fixo _CARDAPIO_POR_ID (mesma ordem dos seeds):
# ids 1-8 -> quentes, 9-15 -> salgados, 16-18 -> bebidas. O 'slug' é o serviço
# usado por adicionar_do_menu (quentes->buffet, salgados->mesa-de-salgados,
# bebidas->bar), replicando o antigo mapeamento de menu_data.
_SECOES_MENU = (
    {"id": "quentes", "nome": "Pratos quentes",
     "resumo": "Receitas que acolhem, sabores que ficam.",
     "slug": "buffet", "ids": range(1, 9)},
    {"id": "salgados", "nome": "Salgados & encontros",
     "resumo": "Para compartilhar e celebrar à sua maneira.",
     "slug": "mesa-de-salgados", "ids": range(9, 16)},
    {"id": "bebidas", "nome": "Bebidas para brindar",
     "resumo": "Do primeiro refresco ao último brinde.",
     "slug": "bar", "ids": range(16, 19)},
)

# Serviço (slug) usado ao adicionar um cardápio do menu ao carrinho, por categoria.
_SERVICO_POR_CATEGORIA = {secao["id"]: secao["slug"] for secao in _SECOES_MENU}


def _categoria_do_cardapio(id_cardapio: int) -> str | None:
    """Retorna o id da seção do menu a que o cardápio pertence (ou None)."""
    for secao in _SECOES_MENU:
        if id_cardapio in secao["ids"]:
            return secao["id"]
    return None


def _categorias_do_menu() -> list:
    """Monta as seções do menu público a partir dos cardápios do banco.

    Agrupa os cardápios nas três seções (quentes/salgados/bebidas) pela faixa
    de id, reutilizando a mesma resolução de imagem de mostrar_servico/
    _itens_carrinho (slug via _slug_imagem_do_cardapio + docs/imagens-menu.json).
    O nome continua normalizado (como no banco); o template aplica o filtro
    'nome_exibicao' para exibi-lo.

    Returns:
        list: seções com id, nome, resumo e itens (dicts com id_cardapio, nome,
            descricao, preco[centavos], imagem[relativa a static/] e versao).
    """
    import json
    from pathlib import Path

    base = Path(current_app.root_path)
    with open(base / "docs" / "imagens-menu.json", encoding="utf-8") as arq:
        imagens = json.load(arq)

    por_categoria = {secao["id"]: [] for secao in _SECOES_MENU}
    for cardapio in listar_cardapios() or []:
        categoria = _categoria_do_cardapio(cardapio.id_cardapio)
        if categoria is None:
            continue

        slug_img = _slug_imagem_do_cardapio(cardapio)
        dados_img = imagens.get(slug_img, {}) if slug_img else {}
        arquivo = dados_img.get("arquivo")
        imagem_rel = arquivo[len("static/"):] if arquivo and arquivo.startswith("static/") else arquivo

        por_categoria[categoria].append({
            "id_cardapio": cardapio.id_cardapio,
            "nome": cardapio.nome,
            "descricao": cardapio.descricao,
            "preco": cardapio.preco_base,  # centavos
            "imagem": imagem_rel,          # ex.: "images/menu/feijoada.jpg" (ou None)
            "versao": dados_img.get("versao"),
        })

    return [
        {"id": secao["id"], "nome": secao["nome"], "resumo": secao["resumo"],
         "itens": por_categoria[secao["id"]]}
        for secao in _SECOES_MENU
    ]


def _slug_imagem_do_cardapio(cardapio) -> str | None:
    """Resolve o slug de imagem de um cardápio.

    Prefere o slug persistido no banco (Cardapio.imagem_slug), fonte de verdade
    para cardápios novos (id fora de 1..18). Se não houver, faz fallback para o
    dicionário _CARDAPIO_POR_ID, que mapeia os 18 cardápios seed.

    Args:
        cardapio: objeto Cardapio.

    Returns:
        str | None: slug da imagem ou None se não houver mapeamento.
    """
    if getattr(cardapio, "imagem_slug", None):
        return cardapio.imagem_slug
    return _CARDAPIO_POR_ID.get(cardapio.id_cardapio, (None, None))[0]

@cliente_bp.get("")
def pagina_inicial():
    """Renderiza a home page."""
    return render_template("home.html")

# =========================== PEDIDO ===========================

@cliente_bp.post("/carrinho/fazer_pedido")
def fazer_pedido():
    """Registra o pedido do cliente e dispara um e-mail de confirmação."""
    from datetime import date, datetime, time
    from zoneinfo import ZoneInfo

    # --- endereço do evento ---
    endereco = _endereco_evento_selecionado()
    if endereco is None:
        flash("Escolha um endereço válido para o evento.", "danger")
        return redirect(url_for("cliente.mostrar_carrinho"))

    # --- data e horário do evento ---
    try:
        data_evento = date.fromisoformat(request.form.get("data_evento", ""))
        hora_inicio = time.fromisoformat(request.form.get("hora_inicio", ""))
        hora_fim = time.fromisoformat(request.form.get("hora_fim", ""))
        if (data_evento < datetime.now(ZoneInfo("America/Sao_Paulo")).date()
                or hora_inicio.tzinfo or hora_fim.tzinfo or hora_fim <= hora_inicio):
            raise ValueError
    except ValueError:
        flash("Informe uma data válida e um horário de término posterior ao início.", "danger")
        return redirect(url_for("cliente.mostrar_carrinho"))

    # --- carrinho (itens de cardápio) ---
    carrinho = session.get("carrinho", [])

    # --- bebidas (opcionais) ---
    # O checkout envia um campo de formulário oculto 'bebidas' com um JSON no
    # formato {"<id_bebida>": qtd}. Cada bebida é validada no servidor (catálogo
    # + quantidade) e o valor vem SEMPRE do banco (Bebida.valor_unitario), nunca
    # de um preço informado pelo cliente.
    from decimal import Decimal

    try:
        selecao_bebidas = json.loads(request.form.get("bebidas", "{}"))
    except (TypeError, ValueError):
        selecao_bebidas = {}
    if not isinstance(selecao_bebidas, dict):
        selecao_bebidas = {}

    bebidas = []
    for codigo, qtd in selecao_bebidas.items():
        try:
            bebida = buscar_bebida_por_id(int(codigo))
        except (TypeError, ValueError):
            bebida = None
        if (bebida is None or bebida.valor_unitario is None
                or isinstance(qtd, bool) or not isinstance(qtd, int)
                or not 1 <= qtd <= 99):
            flash("Confira as bebidas selecionadas antes de enviar o pedido.", "danger")
            return redirect(url_for("cliente.mostrar_carrinho"))
        bebidas.append({
            "id_bebida": bebida.id_bebida,
            "qtd": qtd,
            "valor_total": Decimal(bebida.valor_unitario) * qtd,
        })

    if not carrinho and not bebidas:
        flash("Adicione itens ao carrinho antes de confirmar.", "danger")
        return redirect(url_for("cliente.mostrar_carrinho"))

    total = sum(_subtotal_item(item) for item in carrinho)
    observacao = (request.form.get("obs", "") or "").strip()[:1000] or None

    pedido = criar_pedido(
        id_cliente=session.get("id"),
        id_endereco=endereco.id_endereco,
        valor_total=total,
        data_evento=data_evento,
        hora_inicio=hora_inicio,
        hora_fim=hora_fim,
        cardapios=carrinho,
        observacao=observacao,
        bebidas=bebidas,
    )
    if pedido is None:
        flash("Não foi possível registrar seu pedido. Tente novamente.", "danger")
        return redirect(url_for("cliente.mostrar_carrinho"))

    id_pedido = pedido.id_pedido
    session.pop("carrinho", None)

    registrar_log("REALIZOU PEDIDO",
                  f"Cliente {session.get('id')} realizou o pedido {id_pedido}.")

    try:
        cliente = buscar_usuario_por_id(session.get("id"))
        mensagem = f"Recebemos o pedido nº {id_pedido}. Ele aguarda confirmação."
        enviar_email_nao_responda("Pedido recebido", cliente.email_criptografado,
                                  mensagem, f"<p>{mensagem}</p>")
    except Exception:
        current_app.logger.exception("Falha ao enviar e-mail do pedido %s", id_pedido)

    flash("Pedido realizado com sucesso.", "success")
    return redirect(url_for("cliente.perfil"))


@cliente_bp.post("/cancelar_pedido/<int:id_pedido>")
def cancelar_pedido(id_pedido: int):
    """Cancela um pedido do cliente logado e registra a ação."""
    pedido = buscar_pedido_por_id(id_pedido)

    if pedido is None or pedido.id_cliente != session.get("id"):
        flash("Pedido não encontrado.", "danger")
        return redirect(url_for("cliente.perfil"))

    if pedido.status == "aguardando" and atualizar_pedido(id_pedido, status="cancelado"):
        registrar_log("CANCELOU PEDIDO", f"Cliente cancelou o pedido {id_pedido}.")
        flash("Pedido cancelado.", "success")
    else:
        flash("O pedido não pôde ser cancelado.", "danger")

    return redirect(url_for("cliente.perfil"))

# =========================== BEBIDA ===========================

def _catalogo_bebidas():
    from services import formatar_bebidas
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

    # Só as imagens vêm do JSON; o preço (centavos) é lido do banco (preco_base).
    base = Path(current_app.root_path)
    with open(base / "docs" / "imagens-menu.json", encoding="utf-8") as arq:
        imagens = json.load(arq)

    associacoes = listar_cardapios_do_servico(servico.id_servico) or []

    cardapios = []
    for associacao in associacoes:
        cardapio = buscar_cardapio_por_id(associacao.id_cardapio)
        if cardapio is None:
            continue

        slug_img = _slug_imagem_do_cardapio(cardapio)

        # preço por pessoa em centavos, direto do banco
        preco_pessoa = cardapio.preco_base

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

def _subtotal_item(item: dict) -> int:
    """Calcula o subtotal (em centavos) de um item do carrinho da sessão.

    Os itens de session['carrinho'] guardam apenas 'id_servico', 'id_cardapio'
    e 'qtd' (nº de convidados). O preço por pessoa (centavos) vem do banco, do
    campo preco_base do cardápio.

    Args:
        item (dict): item do carrinho da sessão.

    Returns:
        int: subtotal em centavos (0 se o cardápio não existir).
    """
    cardapio = buscar_cardapio_por_id(item.get("id_cardapio"))
    if cardapio is None:
        return 0

    # preço por pessoa em centavos, direto do banco
    return cardapio.preco_base * item.get("qtd", 0)

def _itens_carrinho():
    """Exibe a página do carrinho com os itens da sessão enriquecidos.

    Cada item de session['carrinho'] é cruzado com o preço do banco
    (Cardapio.preco_base, em centavos) e com as imagens de
    docs/imagens-menu.json (por slug da imagem). O subtotal é o preço por pessoa
    (centavos) multiplicado pela quantidade de convidados.

    Returns:
        tuple: itens do carrinho e total em centavos.
    """
    import json
    from pathlib import Path

    # Só as imagens vêm do JSON; o preço (centavos) é lido do banco (preco_base).
    base = Path(current_app.root_path)
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
        slug_img = _slug_imagem_do_cardapio(cardapio)

        # preço por pessoa em centavos, direto do banco
        preco_pessoa = cardapio.preco_base

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
    """Adiciona o cardápio público ao carrinho a partir do id do cardápio.

    O formulário do menu envia o id_cardapio (resolvido no banco). O serviço é
    escolhido de forma determinística pela categoria do cardápio (quentes->
    buffet, salgados->mesa-de-salgados, bebidas->bar), replicando o mapeamento
    que antes vinha de menu_data.
    """
    id_cardapio = request.form.get("id_cardapio", type=int)
    qtd = request.form.get("qtd", type=int)
    cardapio = buscar_cardapio_por_id(id_cardapio) if id_cardapio is not None else None
    if cardapio is None or qtd is None or not 10 <= qtd <= 500:
        flash("Escolha um prato e informe uma quantidade de 10 a 500 pessoas.", "danger")
        return redirect(url_for("cliente.menu"))

    categoria = _categoria_do_cardapio(cardapio.id_cardapio)
    slug = _SERVICO_POR_CATEGORIA.get(categoria) if categoria else None
    servico = buscar_servico_por_slug(slug) if slug else None
    if servico is None or not any(
        vinculo.id_cardapio == cardapio.id_cardapio
        for vinculo in listar_cardapios_do_servico(servico.id_servico) or []
    ):
        flash("Este prato está indisponível no momento.", "danger")
        return redirect(url_for("cliente.menu"))

    from utils import nome_exibicao

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
    flash(f"{nome_exibicao(cardapio.nome)} para {qtd} pessoas está no carrinho.", "success")
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

    # usuario
    usuario=buscar_usuario_por_id(session.get("id"))

    usuario.cpf_criptografado=descriptografar(usuario.cpf_criptografado)
    usuario.email_criptografado=descriptografar(usuario.email_criptografado)

    # pedido
    pedido=next((p for p in listar_pedidos_por_cliente(session.get("id"))
    if p.status not in ("cancelado", "concluido")), None)

    if pedido is None:
        return jsonify({
            "usuario": {
                "id": usuario.id_usuario,
                "nome": usuario.nome,
                "cpf": usuario.cpf_criptografado,
                "email": usuario.email_criptografado,
            },
            "pedido": None,
            "servicos": {},
            "bebidas": {"itens": [], "valor_total": formatar_moeda(0)},
            "endereco": None,
        })

    pedido.valor_total = formatar_moeda(pedido.valor_total)

    # detalhamento
    cardapios=buscar_cardapios_pedido(pedido.id_pedido) or []
    servicos = {
        servico.nome: [cardapio.nome, formatar_moeda(cardapio.preco_base*cardapio.num_convidados)]
        for cardapio in cardapios
        if (servico := buscar_servico_por_id(cardapio.id_servico))
    }

    endereco = buscar_endereco_por_id(pedido.id_endereco)

    bebidas=listar_bebidas_do_pedido(pedido.id_pedido) or []

    valor_total = 0
    for bebida in bebidas:
        valor_total += bebida.valor_total
    valor_total = formatar_moeda(valor_total)

    return jsonify({
        "usuario": {
            "id": usuario.id_usuario,
            "nome": usuario.nome,
            "cpf": usuario.cpf_criptografado,
            "email": usuario.email_criptografado,
        },
        "pedido": {
            "id": pedido.id_pedido,
            "status": pedido.status,
            "valor_total": pedido.valor_total,
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
                    "valor_un": b.valor_total // b.qtd,
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
    """Renderiza a página de menu com as categorias de cardápio.

    As categorias são montadas a partir do banco (Cardapio) em vez de listas
    estáticas. A categoria de cada cardápio é derivada da faixa de id do
    mapeamento fixo _CARDAPIO_POR_ID (1-8 quentes, 9-15 salgados, 16-18
    bebidas), que já é a ordem dos seeds; o nome de exibição é aplicado no
    template via filtro Jinja 'nome_exibicao'.
    """
    return render_template("menu.html", categorias=_categorias_do_menu())
