from flask import Blueprint, request, render_template, session
#from model.pedido_model import ...
from model.usuario_model import registrar_log, buscar_usuario_por_id

from utils import enviar_email_nao_responda

cliente_bp = Blueprint("cliente", __name__)

@cliente_bp.route("/home", __name__)
def pagina_inicial():
    """Redireciona para a home page."""
    
    return render_template("home.html") # TODO: adicionar pagina inicial

@cliente_bp.route("/fazer_pedido", __name__)
def fazer_pedido():
    """Registra o pedido do cliente e envia um email automático."""
    
    logadouro=request.form.get("logadouro")
    numero=request.form.get("num")
    complemento=request.form.get("compl")
    bairro=request.form.get("bairro")
    cidade=request.form.get("cidade")
    cep=request.form.get("cep")
    observacao=request.form.get("obs")
    
    # adicionar funcao de criação de pedido
    
    registrar_log(session.get("id"), 'REALIZOU PEDIDO', 
    "contém ****ADICIONAR CARDAPIOS E BEBIDAS E DADOS DO PEDIDO****")
    
    enviar_email_nao_responda(f"Pedido Realizado às {"""data de criação da entidade pedido"""}",
    
    buscar_usuario_por_id(session.get("id")).email, f"contém ****ADICIONAR CARDAPIOS E BEBIDAS E DADOS DO PEDIDO****",
    f"conteudo html ***adicionar modelo de pedido")
    
@cliente_bp.route("/cancelar_pedido", __name__)
def cancelar_pedido():
    """Cancela um pedido escolhido pelo cliente."""

    id_pedido=...# buscar pedido 
    
    # adicionar funcao de criação de pedido
    
    registrar_log(session.get("id"), 'REALIZOU PEDIDO', 
    "contém ****ADICIONAR CARDAPIOS E BEBIDAS E DADOS DO PEDIDO****")
    
    enviar_email_nao_responda(f"Pedido Realizado às {"""data de criação da entidade pedido"""}",
    
    buscar_usuario_por_id(session.get("id")).email, f"contém ****ADICIONAR CARDAPIOS E BEBIDAS E DADOS DO PEDIDO****",
    f"conteudo html ***adicionar modelo de pedido")