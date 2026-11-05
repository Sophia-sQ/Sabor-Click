from flask import (
    Blueprint,
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
    buscar_bebida_por_id,
    buscar_bebidas_pedido,
    buscar_cardapios_pedido,
    criar_pedido,
    listar_pedidos_por_cliente,
)
from model.servico_model import (
    buscar_cardapio_por_id,
    buscar_servico_por_id,
    buscar_servico_por_slug,
    listar_cardapios_do_servico,
)
from model.usuario_model import (
    adicionar_endereco,
    atualizar_endereco,
    atualizar_usuario,
    buscar_enderco_por_id,
    buscar_endereco_por_id,
    buscar_usuario_por_id,
    deletar_endereco,
    registrar_log,
)
from services import enviar_email_nao_responda

cliente_bp = Blueprint("cliente", __name__, url_prefix="/home")

@cliente_bp.get("")
def pagina_inicial():
    """Redireciona para a home page."""
    return render_template("home.html")

# =========================== PEDIDO ===========================

@cliente_bp.route("/carrinho/fazer_pedido", methods=["GET", "POST"])
def fazer_pedido():
    """Registra o pedido do cliente a partir do carrinho e avisa por e-mail.

    No GET exibe a página de finalização. No POST valida os dados, calcula o
    valor total (preço base do cardápio x número de convidados, por pessoa) e
    cria o pedido com os cardápios e eventuais bebidas pedidas à parte.

    Returns:
        Response: redirecionamento para o perfil em caso de sucesso, ou de volta
        ao carrinho em caso de erro de validação.
    """
    if request.method == "GET":
        return render_template("fazer_pedido.html", enderecos=_enderecos_do_usuario())

    from decimal import Decimal, InvalidOperation
    from utils import string_para_data, string_para_hora

    carrinho = _carrinho()
    if not carrinho:
        flash("Seu carrinho está vazio.", "danger")
        return redirect(url_for("cliente.mostrar_carrinho"))

    id_endereco = request.form.get("endereco", type=int)
    observacao = request.form.get("obs")
    data_evento = request.form.get("data_evento")
    hora_inicio = request.form.get("hora_inicio")
    hora_fim = request.form.get("hora_fim")

    # O endereço precisa existir e pertencer ao cliente logado.
    endereco = buscar_endereco_por_id(id_endereco) if id_endereco else None
    if endereco is None or endereco.id_usuario != session.get("id"):
        flash("Selecione um endereço válido para a entrega.", "danger")
        return redirect(url_for("cliente.mostrar_carrinho"))

    if not data_evento or not hora_inicio or not hora_fim:
        flash("Informe data e horários do evento.", "danger")
        return redirect(url_for("cliente.mostrar_carrinho"))

    try:
        data_evento = string_para_data(data_evento)
        hora_inicio = string_para_hora(hora_inicio)
        hora_fim = string_para_hora(hora_fim)
    except (ValueError, TypeError):
        flash("Data ou horários inválidos.", "danger")
        return redirect(url_for("cliente.mostrar_carrinho"))

    # O cardápio é por pessoa: o número de convidados é a maior quantidade do
    # carrinho e precisa ser positivo.
    num_convidados = max((int(item["qtd"]) for item in carrinho), default=0)
    if num_convidados <= 0:
        flash("O número de convidados deve ser maior que zero.", "danger")
        return redirect(url_for("cliente.mostrar_carrinho"))

    # Valor total = soma (preço base do cardápio x nº de convidados).
    total = Decimal("0")
    for item in carrinho:
        cardapio = buscar_cardapio_por_id(item["id_cardapio"])
        if cardapio is None:
            flash("Um dos cardápios do carrinho não existe mais.", "danger")
            return redirect(url_for("cliente.mostrar_carrinho"))
        total += Decimal(str(cardapio.preco_base)) * int(item["qtd"])

    # Bebidas pedidas à parte (fora do Bar), enviadas como JSON opcional.
    bebidas = request.get_json(silent=True)
    if bebidas:
        try:
            for item in bebidas:
                bebida = buscar_bebida_por_id(item["id_bebida"])
                if bebida is None:
                    raise ValueError
                total += Decimal(str(bebida.valor_unitario)) * int(item["qtd"])
        except (ValueError, KeyError, TypeError, InvalidOperation):
            flash("Há uma bebida inválida no pedido.", "danger")
            return redirect(url_for("cliente.mostrar_carrinho"))

    pedido = criar_pedido(
        session.get("id"), id_endereco, num_convidados, total,
        data_evento, hora_inicio, hora_fim, carrinho, observacao, bebidas,
    )

    if pedido is None:
        flash("Não foi possível registrar o pedido. Tente novamente.", "danger")
        return redirect(url_for("cliente.mostrar_carrinho"))

    session["carrinho"] = []
    registrar_log("REALIZOU PEDIDO", f"Cliente criou o pedido {pedido.id_pedido}.")

    usuario = buscar_usuario_por_id(session.get("id"))
    try:
        corpo_html = render_template(
            "email_pedido.html",
            nome=usuario.nome,
            id=pedido.id_pedido,
            data_confirmacao=pedido.criado_em.strftime("%d/%m/%Y %H:%M"),
            ano=pedido.criado_em.strftime("%Y"),
        )
        enviar_email_nao_responda(
            "Pedido realizado",
            usuario.email_criptografado,
            f"Seu pedido {pedido.id_pedido} foi registrado e aguarda aceite.",
            corpo_html,
        )
    except Exception:  # noqa: BLE001 - envio de e-mail é best-effort
        from flask import current_app
        current_app.logger.exception("Falha ao enviar e-mail de pedido.")

    flash("Pedido realizado com sucesso!", "success")
    return redirect(url_for("cliente.perfil"))


@cliente_bp.post("/cancelar_pedido/<int:id_pedido>")
def cancelar_pedido(id_pedido: int):
    """Cancela um pedido do próprio cliente.

    Verifica que o pedido pertence ao cliente logado antes de cancelar, impedindo
    que um cliente cancele pedidos de outras pessoas via manipulação de URL.

    Args:
        id_pedido (int): identificador do pedido a cancelar.

    Returns:
        Response: redirecionamento para o perfil do cliente.
    """
    from model.pedido_model import buscar_pedido_por_id

    pedido = buscar_pedido_por_id(id_pedido)
    if pedido is None or pedido.id_cliente != session.get("id"):
        flash("Pedido não encontrado.", "danger")
        return redirect(url_for("cliente.perfil"))

    if atualizar_pedido(id_pedido, status="cancelado"):
        registrar_log("CANCELOU PEDIDO", f"Cliente cancelou o pedido {id_pedido}.")
        flash("Pedido cancelado.", "success")
    else:
        flash("Aconteceu um erro no cancelamento do pedido.", "danger")

    return redirect(url_for("cliente.perfil"))

# =========================== BEBIDA ===========================

# =========================== ENDERECO ===========================

@cliente_bp.get("/endereco")
def endereco():
    """Mostra a página com todos os endereços cadastrados pelo usuário."""
    
    return redirect(url_for("cliente.perfil") + "#enderecos")

@cliente_bp.post("/adicionar_endereco")
def novo_endereco():
    """Adiciona novo endereço ao cliente logado."""
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
    """Atualiza um endereço do usuário logado."""
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
    """Deleta um endereço do usuário logado."""
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
    """Leve o usuário para a ancora dos servicos na home page."""
    # garante que não vai existir um /servico 404

    return redirect(url_for("cliente.home") + "#servicos") 

@cliente_bp.get("/servico/<string:slug>")
def mostrar_servico(slug):
    """Rota dinamica para mostrar todos os cardápios disponiveis para um servico.
    
    Retorna o template mais os cardapios para serem acessados com o Jinja2.
    
    cardapios é uma lista de objetos do SQLAlchemy.
    """
    servico=buscar_servico_por_slug(slug)
    cardapios=listar_cardapios_do_servico(servico.id_servico)

    return render_template("servico.html", cardapios=cardapios)

# ================== CARRINHO DE COMPRAS ==================
def _carrinho() -> list:
    """Pega o carrinho da sessão, caso ele não exista, cria o carrinho."""
    return session.setdefault("carrinho", [])

def _enderecos_do_usuario() -> list:
    """Retorna os endereços do usuário logado (lista vazia se não houver)."""
    from model.usuario_model import listar_enderecos_do_usuario
    return listar_enderecos_do_usuario(session.get("id"))

@cliente_bp.get("/carrinho")
def mostrar_carrinho():
    """Exibe a página de carrinho para o usuário."""
    return render_template("carrinho.html")

@cliente_bp.post("/carrinho/adicionar")
def adicionar():
    """Adiciona um novo cardápio ao carrinho.

    Valida o serviço, o cardápio e o número de convidados (entre 10 e 500) e
    grava no carrinho o item com seu subtotal (preço base x convidados).

    Returns:
        Response: redirecionamento de volta à página do serviço.
    """
    from decimal import Decimal

    slug_servico = request.form.get("slug_servico")
    id_cardapio = request.form.get("id_cardapio", type=int)
    qtd_convidados = request.form.get("qtd", type=int)

    destino = (
        url_for("cliente.mostrar_servico", slug=slug_servico)
        if slug_servico else url_for("cliente.home_servico")
    )

    if (not slug_servico or id_cardapio is None or qtd_convidados is None
            or qtd_convidados < 10 or qtd_convidados > 500):
        flash("Valor(es) inválido(s). Informe de 10 a 500 convidados.", "danger")
        return redirect(destino)

    servico = buscar_servico_por_slug(slug_servico)
    cardapio = buscar_cardapio_por_id(id_cardapio)

    if servico is None or cardapio is None:
        flash("Serviço ou cardápio inválidos.", "danger")
        return redirect(destino)

    subtotal = float(Decimal(str(cardapio.preco_base)) * qtd_convidados)

    novo = {"id_servico": servico.id_servico,
            "id_cardapio": id_cardapio,
            "qtd": qtd_convidados,
            "subtotal": subtotal,
           }

    carrinho = _carrinho()

    existente = next((
        item for item in carrinho
        if item["id_cardapio"] == id_cardapio
        ), None,
    )

    if existente:
        existente["qtd"] = qtd_convidados
        existente["subtotal"] = subtotal
    else:
        carrinho.append(novo)

    session["carrinho"] = carrinho
    flash("Produto adicionado ao carrinho.", "success")
    return redirect(destino)

@cliente_bp.post("/carrinho/remover/<int:id_cardapio>/")
def remover(id_cardapio):
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

def _etapa_cliente(status: str) -> str:
    """Traduz o status interno do pedido para a etapa exibida ao cliente.

    O cliente acompanha o pedido em três etapas: "Recebido", "Em preparo" e
    "Entregue". Os status internos são mapeados assim:

    * ``aguardando`` / ``confirmado`` -> "Recebido"
    * ``em preparo`` -> "Em preparo"
    * ``concluido`` -> "Entregue"
    * ``cancelado`` -> "Cancelado"

    Args:
        status (str): status interno do pedido.

    Returns:
        str: etapa correspondente para exibição.
    """
    mapa = {
        "aguardando": "Recebido",
        "confirmado": "Recebido",
        "em preparo": "Em preparo",
        "concluido": "Entregue",
        "cancelado": "Cancelado",
    }
    return mapa.get(status, status)


@cliente_bp.get("/perfil/dados")
def dados_perfil():
    """Retorna, em JSON, os dados do cliente e do seu pedido ativo.

    Inclui a etapa de acompanhamento (Recebido/Em preparo/Entregue) derivada do
    status interno, o detalhamento dos serviços/cardápios e as bebidas pedidas.
    Quando não há pedido ativo, os campos de pedido vêm nulos.

    Returns:
        Response: JSON com usuário, pedido, serviços, bebidas e endereço.
    """
    from security import descriptografar
    from utils import formatar_moeda

    # usuario
    usuario = buscar_usuario_por_id(session.get("id"))
    if usuario is None:
        return jsonify({"erro": "Sessão expirada."}), 401

    cpf = descriptografar(usuario.cpf_criptografado)
    email = descriptografar(usuario.email_criptografado)

    # pedido ativo (não cancelado nem concluído)
    pedido = next(
        (p for p in listar_pedidos_por_cliente(session.get("id"))
         if p.status not in ("cancelado", "concluido")),
        None,
    )

    dados_pedido = None
    servicos = {}
    endereco = None
    bebidas_itens = []
    bebidas_total = formatar_moeda(0)

    if pedido is not None:
        # detalhamento dos serviços/cardápios do pedido
        for cp in buscar_cardapios_pedido(pedido.id_pedido):
            cardapio = buscar_cardapio_por_id(cp.id_cardapio)
            servico = buscar_servico_por_id(cp.id_servico)
            if cardapio is None or servico is None:
                continue
            servicos[servico.nome] = [
                cardapio.nome,
                formatar_moeda(cardapio.preco_base * pedido.num_convidados),
            ]

        endereco = buscar_enderco_por_id(pedido.id_endereco)

        bebidas = buscar_bebidas_pedido(pedido.id_pedido) or []
        total_bebidas = 0
        for b in bebidas:
            total_bebidas += b.valor_total
            bebida = buscar_bebida_por_id(b.id_bebida)
            bebidas_itens.append({
                "nome": bebida.nome if bebida else "Bebida",
                "qtd": b.qtd,
                "valor_un": formatar_moeda(b.valor_total / b.qtd) if b.qtd else formatar_moeda(0),
            })
        bebidas_total = formatar_moeda(total_bebidas)

        dados_pedido = {
            "id": pedido.id_pedido,
            "status": pedido.status,
            "etapa": _etapa_cliente(pedido.status),
            "num_convidados": pedido.num_convidados,
            "valor_total": formatar_moeda(pedido.valor_total),
            "data_evento": pedido.data_evento.isoformat() if pedido.data_evento else None,
            "hora_inicio": pedido.hora_inicio.isoformat() if pedido.hora_inicio else None,
            "hora_fim": pedido.hora_fim.isoformat() if pedido.hora_fim else None,
            "observacao": pedido.observacao,
        }

    return jsonify({
        "usuario": {
            "id": usuario.id_usuario,
            "nome": usuario.nome,
            "cpf": cpf,
            "email": email,
        },
        "pedido": dados_pedido,
        "servicos": servicos,
        "bebidas": {
            "itens": bebidas_itens,
            "valor_total": bebidas_total,
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
    """Atualiza os dados cadastrais (nome, email, cpf, senha) do usuário logado."""
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
    return render_template("home.html")


def menu():
    from menu_data import categorias
    return render_template("menu.html", categorias=categorias)
