from datetime import datetime
from zoneinfo import ZoneInfo

from flask import Blueprint, render_template, request, session

from model.pedido_model import atualizar_pedido, buscar_pedido_por_id
from model.usuario_model import buscar_usuario_por_id, registrar_log
from services import enviar_email_nao_responda
from triggers import criar_trigger_baixa_estoque

chefe_bp = Blueprint("chefe", __name__, url_prefix="/pedido")

@chefe_bp.route("/aceitar", methods=["POST"])
def aceitar_pedido():
    dados=request.get_json(silent=True)
    pedido=buscar_pedido_por_id(dados["id"])
    data_confirma=datetime.now(ZoneInfo("America/Sao_Paulo"))
    atualizar_pedido(pedido.id_pedido, "confirmado", data_confirma, session.get("id"))
    chefe=buscar_usuario_por_id(session.get("id"))
    registrar_log("ACEITOU PEDIDO.", f"Em {data_confirma}, o chefe {chefe.nome} aceitou o pedido {pedido.id_pedido}.")
    data_confirma=data_confirma.astimezone(ZoneInfo("America/Sao_Paulo"))
    criar_trigger_baixa_estoque()


    cliente=buscar_usuario_por_id(pedido.id_cliente)
    enviar_email_nao_responda("Seu pedido foi aceito.", cliente.email, "Seu pedido foi aceito.",
    render_template("email_pedido.html", cliente.nome, pedido.id, pedido.status, data_confirma, data_confirma.strftime("%Y")))

    return render_template("pagina de pedidos.html")

@chefe_bp.route("/atualizar", methods=["GET", "POST"])
def atualizar_status():
    #TODO: adicionar tratamento para quando status nao se encaixa na enum
    if request.method == "GET":
        return render_template("pagina de pedidos.html")

    dados=request.get_json(silent=True)
    pedido=buscar_pedido_por_id(dados["id"])
    data_confirma=datetime.now(ZoneInfo("America/Sao_Paulo"))
    atualizar_pedido(pedido.id_pedido, dados["status"], data_confirma, session.get("id"))
    chefe=buscar_usuario_por_id(session.get("id"))
    registrar_log("ACEITOU PEDIDO.", f"Em {data_confirma}, o chefe {chefe.nome} atualizou o pedido {pedido.id_pedido} para '{dados['status']}'.")
    data_confirma=data_confirma.astimezone(ZoneInfo("America/Sao_Paulo"))

    cliente=buscar_usuario_por_id(pedido.id_cliente)
    enviar_email_nao_responda("Seu pedido foi atualizado.", cliente.email, f"Seu pedido está {dados['status']}.",
    render_template("email_pedido.html", cliente.nome, pedido.id, pedido.status, data_confirma, data_confirma.strftime("%Y")))

    return render_template("pagina de pedidos.html")
