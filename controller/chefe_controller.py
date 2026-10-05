from flask import Blueprint, request, session
from datetime import datetime

from model.pedido_model import buscar_pedido_por_id, atualizar_pedido
from model.usuario_model import registrar_log, buscar_usuario_por_id
from utils import enviar_email_nao_responda

chefe_bp = Blueprint("chefe", __name__, url_prefix='/pedido')

@chefe_bp.route('aceita', methods=['POST'])
def aceitar_pedido():
    dados=request.get_json()
    pedido=buscar_pedido_por_id("""TODO: CHAVE CORRETA""")
    data_confirma=datetime.now(datetime.timezone.utc)
    atualizar_pedido(pedido.id_pedido, "em preparo", data_confirma, session.get("id"))
    chefe=buscar_usuario_por_id(session.get('id'))
    registrar_log(session.get("id"), 'ACEITOU PEDIDO.', f"Em {data_confirma}, o chefe {chefe.nome} aceitou o pedido {pedido.id_pedido}.")
    
    # TODO:trigger para baixa de estoque
    
    cliente=buscar_usuario_por_id(pedido.id_cliente)
    # TODO: nao esquecer de descriptografar o email
    enviar_email_nao_responda("Seu pedido foi aceito.", cliente.email, "Seu pedido for aceito e esta em preparo.")