from flask import Blueprint, request, render_template, session, flash, url_for, redirect

from model.usuario_model import registrar_log, buscar_usuario_por_id, adicionar_endereco
from model.pedido_model import atualizar_pedido, criar_pedido
from model.servico_model import buscar_cardapio_por_id, buscar_servico_por_slug, listar_cardapios_do_servico

from utils import enviar_email_nao_responda

cliente_bp = Blueprint("cliente", __name__, url_prefix='/home')
 
@cliente_bp.get("")
def pagina_inicial():
    """Redireciona para a home page."""
    
    return render_template("home.html") # TODO: adicionar pagina inicial

# =========================== PEDIDO ===========================

@cliente_bp.post("/carrinho/fazer_pedido")
def fazer_pedido():
    """Registra o pedido do cliente e envia um email automático."""
    
    if request.method=="GET":
        return render_template("pagina de pedido")
    
    id_endereco=request.form.get("endereco")
    observacao=request.form.get("obs")
    
    criar_pedido(session.get('id'), id_endereco, ) # FIXME
    
    
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
    

#from openpyxl import Workbook
#from openpyxl.styles import Font
#
#@cliente_bp.get("/exportar")
#def exportar():
#    wb = Workbook()
#    ws = wb.active
#    ws.title = "Compras"
#    ws.append(["Código", "Data e hora", "Responsável", "Total (R$)"])
#    for cell in ws[1]:
#        cell.font = Font(bold=True)
#    for c in compra_model.listar():
#        ws.append([c["id"], c["criada_em"], c["usuario_nome"], c["total_centavos"] / 100])
#    ws.column_dimensions["B"].width = 22
#    ws.column_dimensions["C"].width = 25
#    for cell in ws["D"][1:]:
#        cell.number_format = 'R$ #,##0.00'
#    arquivo = BytesIO()
#    wb.save(arquivo)
#    arquivo.seek(0)
#    return send_file(arquivo, as_attachment=True, download_name="compras.xlsx",
#                     mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
