from datetime import datetime
from zoneinfo import ZoneInfo

from flask import Blueprint, render_template, request, session, jsonify, flash, redirect, url_for, abort

from model.ficha_model import listar_ficha_tecnica_por_bebida, listar_ficha_tecnica_por_prato, listar_pratos_por_cardapio
from model.pedido_model import (buscar_cardapios_pedido, listar_bebidas_do_pedido, buscar_bebida_por_id, 
                                atualizar_pedido, buscar_pedido_por_id, listar_pedido_por_status, 
                                buscar_pedido_por_chefe)
from model.servico_model import buscar_cardapio_por_id
from model.usuario_model import buscar_usuario_por_id, registrar_log

from services import enviar_email_nao_responda
from triggers import criar_trigger_baixa_estoque

chefe_bp = Blueprint("chefe", __name__, url_prefix="/pedido")

@chefe_bp.get('/cozinha')
def pedidos():
    pedidos = listar_pedido_por_status("aguardando")
    return render_template("cozinha.html", pedidos)

@chefe_bp.route("/aceitar", methods=["POST"])
def aceitar_pedido():
    dados=request.get_json(silent=True)
    pedido=buscar_pedido_por_id(dados["id"])
    data_confirma=datetime.now(ZoneInfo("America/Sao_Paulo"))
    
    em_andamento = buscar_pedido_por_chefe(session.get('id'), "aguardando") != None
    
    if em_andamento:
        flash("Finalize o pedido atual antes de aceitar outro", "danger")
        return redirect(url_for("""TODO:pagina do pedido"""))
    atualizar_pedido(pedido.id_pedido, "confirmado", data_confirma, session.get("id"))
    chefe=buscar_usuario_por_id(session.get("id"))
    registrar_log("ACEITOU PEDIDO.", f"Em {data_confirma}, o chefe {chefe.nome} aceitou o pedido {pedido.id_pedido}.")
    data_confirma=data_confirma.astimezone(ZoneInfo("America/Sao_Paulo"))
    criar_trigger_baixa_estoque()


    cliente=buscar_usuario_por_id(pedido.id_cliente)
    enviar_email_nao_responda("Seu pedido foi aceito.", cliente.email, "Seu pedido foi aceito.",
    render_template("email_pedido.html", cliente.nome, pedido.id, pedido.status, data_confirma, data_confirma.strftime("%Y")))

    return render_template("pagina do pedido.html")

@chefe_bp.route("/atualizar", methods=["GET", "POST"])
def atualizar_status():
    if request.method == "GET":
        return render_template("pagina de pedidos.html")

    dados=request.get_json(silent=True)
    pedido=buscar_pedido_por_id(dados["id"])
    
    from model.pedido_model import Pedido
    valores_aceitos = list(Pedido.status.type.enums)
    
    if dados["status"] not in valores_aceitos:
        flash("Valor de status inválido.", "danger")
        return redirect(url_for(request.endpoint))
    
    data_confirma=datetime.now(ZoneInfo("America/Sao_Paulo"))
    
    try:
        atualizar_pedido(pedido.id_pedido, dados["status"], data_confirma, session.get("id"))
    except:
        flash("Insira valores válidos.", "danger")
        return redirect(url_for(request.endpoint))
    
    chefe=buscar_usuario_por_id(session.get("id"))
    
    if not chefe:
        return abort(400)
    
    registrar_log("ACEITOU PEDIDO.", f"Em {data_confirma}, o chefe {chefe.nome} atualizou o pedido {pedido.id_pedido} para '{dados['status']}'.")
    data_confirma=datetime.astimezone(ZoneInfo("America/Sao_Paulo"))

    cliente=buscar_usuario_por_id(pedido.id_cliente)
    enviar_email_nao_responda("Seu pedido recebeu uma atualização.", cliente.email, f"Seu pedido está {dados['status']}.",
    render_template("email_pedido.html", cliente.nome, pedido.id, pedido.status, data_confirma, data_confirma.strftime("%Y")))

    return render_template("pagina de pedidos.html")

@chefe_bp.get("/preparo")
def enviar_preparo():
    """Retorna, em JSON, a ficha de preparo completa de um pedido.

    Inclui os cardápios do pedido com seus pratos (e as fichas técnicas de
    cada prato) e as bebidas do pedido (avulsas ou vindas do cardápio), cada
    uma com sua ficha técnica.
    """
    from model.servico_model import Cardapio
    from model.ficha_model import buscar_ingrediente_por_id, buscar_prato_por_id

    pedido = buscar_pedido_por_chefe(session["id"])
    if not pedido:
        return jsonify({"erro": "Nenhum pedido em preparo."}), 404

    # -------- funções internas --------
    def _ficha_prato(id_prato):
        """Lista a ficha técnica de um prato já com o nome/unidade do ingrediente."""
        itens = listar_ficha_tecnica_por_prato(id_prato) or []
        ficha = []
        for item in itens:
            ingrediente = buscar_ingrediente_por_id(item.id_ingrediente)
            ficha.append({
                "id_ingrediente": item.id_ingrediente,
                "nome": ingrediente.nome if ingrediente else None,
                "unidade": ingrediente.unidade if ingrediente else None,
                "qtd_necessaria": item.qtd_necessaria,
            })
        return ficha

    def _ficha_bebida(id_bebida):
        """Lista a ficha técnica de uma bebida já com o nome/unidade do ingrediente."""
        itens = listar_ficha_tecnica_por_bebida(id_bebida) or []
        ficha = []
        for item in itens:
            ingrediente = buscar_ingrediente_por_id(item.id_ingrediente)
            ficha.append({
                "id_ingrediente": item.id_ingrediente,
                "ingrediente": ingrediente.nome if ingrediente else None,
                "unidade": ingrediente.unidade if ingrediente else None,
                "qtd_necessaria": float(item.qtd_necessaria),
            })
        return ficha

    # -------- CARDÁPIOS DO PEDIDO (com pratos e suas fichas técnicas) --------
    cardapios_resposta = []
    for vinculo in buscar_cardapios_pedido(pedido.id_pedido) or []:
        cardapio = buscar_cardapio_por_id(vinculo.id_cardapio)

        pratos_resposta = []
        for pc in listar_pratos_por_cardapio(vinculo.id_cardapio) or []:
            prato = buscar_prato_por_id(pc.id_prato)
            pratos_resposta.append({
                "id_prato": pc.id_prato,
                "nome": prato.nome if prato else None,
                "tipo_prato": prato.tipo_prato if prato else None,
                "tempo_preparo": prato.tempo_preparo if prato else None,
                "requer_pre_preparo": prato.requer_pre_preparo if prato else None,
                "qtd": pc.qtd,
                "descricao": pc.descricao,
                "ficha_tecnica": _ficha_prato(pc.id_prato),
            })

        cardapios_resposta.append({
            "id_cardapio": vinculo.id_cardapio,
            "id_servico": vinculo.id_servico,
            "nome": cardapio.nome if cardapio else None,
            "descricao": cardapio.descricao if cardapio else None,
            "pratos": pratos_resposta,
        })

    # -------- BEBIDAS DO PEDIDO (avulsas) com suas fichas técnicas --------
    bebidas_resposta = []
    for item in listar_bebidas_do_pedido(pedido.id_pedido) or []:
        bebida = buscar_bebida_por_id(item.id_bebida)
        bebidas_resposta.append({
            "id_bebida": item.id_bebida,
            "nome": bebida.nome if bebida else None,
            "descricao": bebida.descricao if bebida else None,
            "qtd": item.qtd,
            "ficha_tecnica": _ficha_bebida(item.id_bebida),
        })

    return jsonify({
        "id_pedido": pedido.id_pedido,
        "status": pedido.status,
        "num_convidados": pedido.num_convidados,
        "observacao": pedido.observacao,
        "cardapios": cardapios_resposta,
        "bebidas": bebidas_resposta,
    })
