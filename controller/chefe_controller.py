"""Controlador do chef: visualização, aceite e atualização de status de pedidos."""

from datetime import datetime
from zoneinfo import ZoneInfo

from flask import Blueprint, jsonify, render_template, request, session

from model.pedido_model import (
    aceitar_pedido_atomico,
    atualizar_status_pelo_chefe,
    buscar_pedido_por_id,
    listar_pedidos_do_chefe,
    listar_pedidos_pendentes,
)
from model.usuario_model import buscar_usuario_por_id, registrar_log
from services import enviar_email_nao_responda

chefe_bp = Blueprint("chefe", __name__, url_prefix="/pedido")


def _avisar_cliente(pedido, assunto: str, resumo: str, data_confirma: datetime) -> None:
    """Envia ao cliente um e-mail de atualização do pedido.

    Falhas no envio são silenciadas para não interromper o fluxo do chef; o
    status do pedido já foi persistido antes desta chamada.

    Args:
        pedido: instância de ``Pedido`` atualizada.
        assunto (str): assunto do e-mail.
        resumo (str): texto puro resumindo a mudança.
        data_confirma (datetime): momento da atualização.
    """
    cliente = buscar_usuario_por_id(pedido.id_cliente)
    if cliente is None:
        return

    try:
        corpo_html = render_template(
            "email_pedido.html",
            nome=cliente.nome,
            id=pedido.id_pedido,
            data_confirmacao=data_confirma.strftime("%d/%m/%Y %H:%M"),
            ano=data_confirma.strftime("%Y"),
        )
        enviar_email_nao_responda(assunto, cliente.email_criptografado, resumo, corpo_html)
    except Exception:  # noqa: BLE001 - o envio de e-mail é best-effort
        from flask import current_app
        current_app.logger.exception("Falha ao enviar e-mail de atualização de pedido.")


@chefe_bp.get("")
@chefe_bp.get("/")
def pagina_pedidos():
    """Exibe os pedidos pendentes e os pedidos do chef logado."""
    pendentes = listar_pedidos_pendentes()
    meus_pedidos = listar_pedidos_do_chefe(session.get("id"))
    return render_template("pedidos.html", pendentes=pendentes, meus_pedidos=meus_pedidos)


@chefe_bp.route("/aceitar", methods=["POST"])
def aceitar_pedido():
    """Permite que um chef assuma a responsabilidade por um pedido.

    A atribuição é atômica: se dois chefs tentarem aceitar o mesmo pedido ao
    mesmo tempo, apenas um terá sucesso. O aceite muda o status para
    ``'confirmado'``, o que dispara a baixa automática de estoque. Se o estoque
    for insuficiente, a operação é revertida e o aceite falha.

    Returns:
        Response: JSON com ``ok`` e uma ``mensagem`` descritiva, com o código
        HTTP apropriado (200, 400, 409 ou 422).
    """
    dados = request.get_json(silent=True) or {}
    id_pedido = dados.get("id")

    if id_pedido is None:
        return jsonify({"ok": False, "mensagem": "Pedido não informado."}), 400

    pedido = buscar_pedido_por_id(id_pedido)
    if pedido is None:
        return jsonify({"ok": False, "mensagem": "Pedido não encontrado."}), 404

    data_confirma = datetime.now(ZoneInfo("America/Sao_Paulo"))
    id_chefe = session.get("id")

    if not aceitar_pedido_atomico(id_pedido, id_chefe, data_confirma):
        return jsonify({
            "ok": False,
            "mensagem": "Pedido já foi aceito por outro chef ou o estoque é insuficiente.",
        }), 409

    chefe = buscar_usuario_por_id(id_chefe)
    registrar_log(
        "ACEITOU PEDIDO.",
        f"Em {data_confirma}, o chefe {chefe.nome} aceitou o pedido {id_pedido}.",
    )

    pedido = buscar_pedido_por_id(id_pedido)
    _avisar_cliente(pedido, "Seu pedido foi aceito.", "Seu pedido foi aceito.", data_confirma)

    return jsonify({"ok": True, "mensagem": "Pedido aceito com sucesso."}), 200


@chefe_bp.route("/atualizar", methods=["GET", "POST"])
def atualizar_status():
    """Atualiza o status de um pedido do chef (ex.: 'em preparo', 'concluido').

    Apenas o chef responsável pelo pedido pode alterá-lo. A mudança de status
    passa a ser refletida também na página do cliente.

    Returns:
        Response: página de pedidos (GET) ou JSON com o resultado (POST).
    """
    if request.method == "GET":
        return pagina_pedidos()

    dados = request.get_json(silent=True) or {}
    id_pedido = dados.get("id")
    novo_status = dados.get("status")

    if id_pedido is None or not novo_status:
        return jsonify({"ok": False, "mensagem": "Dados incompletos."}), 400

    id_chefe = session.get("id")

    if not atualizar_status_pelo_chefe(id_pedido, id_chefe, novo_status):
        return jsonify({
            "ok": False,
            "mensagem": "Não foi possível atualizar: pedido inexistente, status inválido "
                        "ou você não é o chef responsável.",
        }), 403

    data_confirma = datetime.now(ZoneInfo("America/Sao_Paulo"))
    chefe = buscar_usuario_por_id(id_chefe)
    registrar_log(
        "ATUALIZOU PEDIDO.",
        f"Em {data_confirma}, o chefe {chefe.nome} atualizou o pedido {id_pedido} para '{novo_status}'.",
    )

    pedido = buscar_pedido_por_id(id_pedido)
    _avisar_cliente(
        pedido,
        "Seu pedido foi atualizado.",
        f"Seu pedido está {novo_status}.",
        data_confirma,
    )

    return jsonify({"ok": True, "mensagem": "Status atualizado com sucesso."}), 200
