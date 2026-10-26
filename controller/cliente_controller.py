from flask import Blueprint, request, render_template, session, flash, url_for, redirect, jsonify

from model.usuario_model import registrar_log, buscar_usuario_por_id, adicionar_endereco, buscar_enderco_por_id, atualizar_usuario, buscar_endereco_por_id, atualizar_endereco, deletar_endereco
from model.pedido_model import atualizar_pedido, criar_pedido, listar_pedidos_por_cliente, buscar_cardapios_pedido, buscar_bebidas_pedido, buscar_bebida_por_id
from model.servico_model import buscar_cardapio_por_id, buscar_servico_por_slug, listar_cardapios_do_servico, buscar_servico_por_id

from services import enviar_email_nao_responda

cliente_bp = Blueprint("cliente", __name__, url_prefix='/home')
 
@cliente_bp.get("")
def pagina_inicial():
    """Redireciona para a home page."""
    
    return render_template("home.html") # TODO: adicionar pagina inicial

# =========================== PEDIDO ===========================

@cliente_bp.route("/carrinho/fazer_pedido", methods=['GET', "POST"])
def fazer_pedido():
    """Registra o pedido do cliente e envia um email automático."""
    if request.method=="GET":
        return render_template("pagina de pedido")
    
    from utils import string_para_data, string_para_hora
    
    id_endereco=request.form.get("endereco")
    bebidas=request.get_json(silent=True)
    observacao=request.form.get("obs")
    data_evento=request.form.get("data_evento")
    hora_inicio=request.form.get("hora_inicio")
    hora_fim=request.form.get("hora_fim")
    
    data_evento = string_para_data(data_evento)
    hora_inicio = string_para_hora(hora_inicio)
    hora_fim = string_para_hora(hora_fim)
    
    total = sum(servico["qtd"] for servico in session["carrinho"])

    
    criar_pedido(session.get('id'), id_endereco, data_evento, hora_inicio, hora_fim, session['carrinho'], total, observacao, bebidas) # FIXME
    
    
    registrar_log('REALIZOU PEDIDO', 
    "contém ****ADICIONAR CARDAPIOS E BEBIDAS E DADOS DO PEDIDO****")
    
    enviar_email_nao_responda(f"Pedido Realizado às {"""data de criação da entidade pedido"""}",
    
    buscar_usuario_por_id(session.get("id")).email, f"contém ****ADICIONAR CARDAPIOS E BEBIDAS E DADOS DO PEDIDO****",
    f"conteudo html ***adicionar modelo de pedido")
    
    
@cliente_bp.post("/cancelar_pedido")
def cancelar_pedido(id_pedido: int):
    """Cancela um pedido escolhido pelo cliente."""

    if atualizar_pedido(id_pedido, status='cancelado'): 
        registrar_log('CANCELOU PEDIDO', "Cancelou o pedido.")
    else:
        flash("Aconteceu um erro no cancelamento do pedido.", 'danger')
        return redirect(url_for('detalhes do pedido'))
        
# =========================== BEBIDA ===========================

# =========================== ENDERECO ===========================

@cliente_bp.get("/endereco")
def endereco():
    """Mostra a página com todos os endereços cadastrados pelo usuário."""
    
    return render_template('enderecos')

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
        flash("CEP inválido", 'danger')
        return redirect(url_for("cliente.endereco"))
    
    if adicionar_endereco(nome, logadouro, numero, complemento, bairro, cidade, cep) is None:
        flash("Falha no cadastro de novo endereço", 'danger')
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

    return redirect(url_for("cliente.home") + "#servicos") #TODO: verificar se a ancora é essa

@cliente_bp.get("/servico/<string:slug>")
def mostrar_servico(slug):
    """Rota dinamica para mostrar todos os cardápios disponiveis para um servico.
    
    Retorna o template mais os cardapios para serem acessados com o Jinja2.
    
    cardapios é uma lista de objetos do SQLAlchemy."""

    servico=buscar_servico_por_slug(slug)
    cardapios=listar_cardapios_do_servico(servico.id_servico)
    
    return render_template("servico.html", cardapios=cardapios)
    
# ================== CARRINHO DE COMPRAS ================== 
def _carrinho() -> list:
    """Pega o carrinho da sessão, caso ele não exista, cria o carrinho."""
    return session.setdefault("carrinho", [])

@cliente_bp.get("/carrinho")
def mostrar_carrinho():
    """Exibe a página de carrinho para o usuário."""

    return render_template("carrinho.html")

@cliente_bp.post("/carrinho/adicionar")
def adicionar():
    """Adiciona um novo cardapio ao carrinho."""
    
    slug_servico = request.form.get("slug_servico")
    id_cardapio = request.form.get("id_cardapio", type=int)
    qtd_convidados = request.form.get("qtd", type=int)
    
    
    if not slug_servico or id_cardapio is None or (qtd_convidados < 10 or qtd_convidados > 500):
        flash("Valor(es) inválido(s).", 'danger')
        return redirect(url_for('cliente.mostrar_servico'), slug=slug_servico)

    servico = buscar_servico_por_slug(slug_servico)

    cardapio = buscar_cardapio_por_id(id_cardapio)
    
    if servico is None or cardapio is None:
        flash("Serviço ou cardápio inválidos.", "danger")
        return redirect(url_for('cliente.mostrar_servico'), slug=slug_servico)
    
    novo = {'id_servico': servico.id_servico,
            'id_cardapio': id_cardapio,
            'qtd': qtd_convidados,
            "subtotal": """TODO: função de calcular os precos"""
           }
    
    carrinho = _carrinho()
    
    existente = next((
        item for item in carrinho
        if item["id_cardapio"] == id_cardapio
        ), None
    )
    
    if existente:
        existente["qtd"]=qtd_convidados
    else:
        carrinho.append(novo)
    
    session["carrinho"] = carrinho
    flash("Produto adicionado ao carrinho.", "success")
    return redirect(url_for('cliente.mostrar_servico'), slug=slug_servico)

@cliente_bp.post("/carrinho/remover/<int:id_cardapio>/")
def remover(id_cardapio):
    carrinho = _carrinho()

    posicao = next(
        (
            indice
            for indice, item in enumerate(carrinho)
            if item["id_cardapio"] == id_cardapio
        ),
        None
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
    return render_template("perfil.html") #TODO

@cliente_bp.get("/perfil/dados")
def dados_perfil():
    from security import descriptografar
    from utils import formatar_moeda
    
    # usuario
    usuario=buscar_usuario_por_id(session("id"))
    
    usuario.cpf_criptografado=descriptografar(usuario.cpf_criptografado)
    usuario.email_criptografado=descriptografar(usuario.email_criptografado)
    
    # pedido
    pedido=next((p for p in listar_pedidos_por_cliente(session("id"))
    if p.status not in ("cancelado", "concluido")), "Nenhum pedido ativo.")
    
    pedido.valor_total = formatar_moeda(pedido.valor_total)

    # detalhamento
    cardapios=buscar_cardapios_pedido(pedido.id_pedido) or []
    servicos = {
        servico.nome: [cardapio.nome, formatar_moeda(cardapio.preco_base*pedido.num_convidados)]
        for cardapio in cardapios
        if (servico := buscar_servico_por_id(cardapio.id_servico))
    }

    endereco = buscar_enderco_por_id(pedido.id_endereco)
    
    bebidas=buscar_bebidas_pedido(pedido.id_pedido) or []
    
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
            "num_convidados": pedido.num_convidados,
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
        return redirect(url_for("cliente.pagina_perfil"))  # ajuste p/ sua rota de perfil

    # valida força da senha quando enviada
    if nova_senha is not None and not validar_senha_forte(nova_senha):
        flash("A nova senha não atende aos requisitos de segurança.", "danger")
        return redirect(url_for("cliente.pagina_perfil"))

    resultado = atualizar_usuario(
        id_usuario,
        nome=nome,
        email=email,
        cpf=cpf,
        nova_senha=nova_senha,
    )

    if resultado is False:
        flash("Não foi possível atualizar os dados.", "danger")
        return redirect(url_for("cliente.pagina_perfil"))

    flash("Dados atualizados com sucesso.", "success")
    return redirect(url_for("cliente.pagina_perfil"))


