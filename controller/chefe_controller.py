"""Rotas do chefe: aceitar e atualizar o status de pedidos."""
from datetime import datetime
from zoneinfo import ZoneInfo

from flask import Blueprint, render_template, request, session, jsonify, flash, redirect, url_for, abort

from model.ficha_model import listar_ficha_tecnica_por_bebida, listar_ficha_tecnica_por_prato, listar_pratos_por_cardapio
from model.pedido_model import (buscar_cardapios_pedido, listar_bebidas_do_pedido, buscar_bebida_por_id, 
                                atualizar_pedido, buscar_pedido_por_id, listar_pedido_por_status, 
                                buscar_pedido_por_chefe)
from model.servico_model import buscar_cardapio_por_id
from model.usuario_model import buscar_usuario_por_id, buscar_endereco_por_id, registrar_log

from services import enviar_email_nao_responda
from triggers import criar_trigger_baixa_estoque

chefe_bp = Blueprint("chefe", __name__, url_prefix="/pedido")


def _contexto_email_pedido(pedido, data_atualizacao=None) -> dict:
    """Monta o contexto completo para o template email_pedido.html.

    Reúne todas as informações relevantes de um pedido para a notificação por
    e-mail: cliente, chefe responsável (se houver), status, datas/horário do
    evento, endereço, observação, cardápios (com serviço e nº de convidados) e
    bebidas, além do valor total formatado.

    Args:
        pedido: objeto Pedido.
        data_atualizacao (datetime | None): momento da atualização a exibir
            como "data da confirmação/atualização". Se None, usa
            pedido.confirmado_em quando disponível.

    Returns:
        dict: contexto pronto para render_template("email_pedido.html", **ctx).
    """
    from model.servico_model import buscar_servico_por_id
    from utils import formatar_moeda

    cliente = buscar_usuario_por_id(pedido.id_cliente)
    chefe = buscar_usuario_por_id(pedido.id_chefe) if pedido.id_chefe else None
    endereco = buscar_endereco_por_id(pedido.id_endereco)

    # Cardápios do pedido (com nome do serviço e nº de convidados por cardápio).
    cardapios = []
    for vinculo in buscar_cardapios_pedido(pedido.id_pedido) or []:
        cardapio = buscar_cardapio_por_id(vinculo.id_cardapio)
        servico = buscar_servico_por_id(vinculo.id_servico)
        cardapios.append({
            "nome": cardapio.nome if cardapio else None,
            "servico": servico.nome if servico else None,
            "num_convidados": vinculo.num_convidados,
            "subtotal": formatar_moeda(
                (cardapio.preco_base if cardapio else 0) * vinculo.num_convidados
            ),
        })

    # Bebidas do pedido.
    bebidas = []
    for item in listar_bebidas_do_pedido(pedido.id_pedido) or []:
        bebida = buscar_bebida_por_id(item.id_bebida)
        bebidas.append({
            "nome": bebida.nome if bebida else None,
            "qtd": item.qtd,
            "subtotal": formatar_moeda(item.valor_total),
        })

    quando = data_atualizacao or pedido.confirmado_em

    # Rótulo amigável de endereço (quando existir).
    endereco_linha = None
    if endereco:
        partes = [endereco.logradouro, endereco.numero, endereco.complemento]
        linha = ", ".join(str(p) for p in partes if p)
        cidade = " · ".join(str(p) for p in (endereco.bairro, endereco.cidade) if p)
        endereco_linha = " — ".join(p for p in (linha, cidade) if p) or None

    return {
        "nome": cliente.nome if cliente else "",
        "chefe": chefe.nome if chefe else None,
        "id": pedido.id_pedido,
        "status": pedido.status,
        "observacao": pedido.observacao,
        "valor_total": formatar_moeda(pedido.valor_total),
        "data_evento": pedido.data_evento.strftime("%d/%m/%Y") if pedido.data_evento else None,
        "hora_inicio": pedido.hora_inicio.strftime("%H:%M") if pedido.hora_inicio else None,
        "hora_fim": pedido.hora_fim.strftime("%H:%M") if pedido.hora_fim else None,
        "endereco": endereco_linha,
        "cardapios": cardapios,
        "bebidas": bebidas,
        "data_confirmacao": quando.strftime("%d/%m/%Y %H:%M") if quando else None,
        "ano": (quando or pedido.criado_em).strftime("%Y"),
    }


@chefe_bp.get('/cozinha')
def pedidos():
    """Exibe a fila da cozinha com os pedidos aguardando preparo.

    Returns:
        str: template "cozinha.html" renderizado com os pedidos aguardando.
    """
    
    pedidos = listar_pedido_por_status("aguardando")
    return render_template("cozinha.html", pedidos=pedidos)

@chefe_bp.route("/aceitar", methods=["POST"])
def aceitar_pedido():
    """Confirma um pedido, registra o log, garante a trigger e notifica o cliente.

    Lê o id do pedido do corpo JSON, atualiza o status para 'confirmado',
    registra a ação e envia e-mail de confirmação ao cliente.

    Returns:
        str: template da página de pedidos renderizado.
    """
    from model.cargos import Cargo
    
    if buscar_usuario_por_id(session['id']).id_permissao < Cargo.CHEFE.value:
        return abort(403)
        
    dados=request.get_json(silent=True)
    pedido=buscar_pedido_por_id(dados["id"])
    data_confirma=datetime.now(ZoneInfo("America/Sao_Paulo"))
    
    em_andamento = buscar_pedido_por_chefe(session.get('id'), "aguardando") != None
    
    if em_andamento:
        flash("Finalize o pedido atual antes de aceitar outro", "danger")
        return redirect(url_for("chefe.pedidos"))
    atualizar_pedido(pedido.id_pedido, "confirmado", data_confirma, session.get("id"))
    chefe=buscar_usuario_por_id(session.get("id"))
    registrar_log("ACEITOU PEDIDO.", f"Em {data_confirma}, o chefe {chefe.nome} aceitou o pedido {pedido.id_pedido}.")
    data_confirma=data_confirma.astimezone(ZoneInfo("America/Sao_Paulo"))
    criar_trigger_baixa_estoque()


    cliente=buscar_usuario_por_id(pedido.id_cliente)
    enviar_email_nao_responda(
        "Seu pedido foi aceito.",
        cliente.email,
        "Seu pedido foi aceito.",
        render_template("email_pedido.html", **_contexto_email_pedido(pedido, data_confirma)),
    )

    return render_template("pagina do pedido.html")

@chefe_bp.route("/atualizar", methods=["GET", "POST"])
def atualizar_status():
    """Atualiza o status de um pedido e notifica o cliente por e-mail.

    No GET, exibe a página de pedidos. No POST, lê id e status do corpo JSON,
    atualiza o pedido, registra o log e envia o e-mail.

    Returns:
        str: template da página de pedidos renderizado.
    """
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
    data_confirma=data_confirma.astimezone(ZoneInfo("America/Sao_Paulo"))

    cliente=buscar_usuario_por_id(pedido.id_cliente)
    enviar_email_nao_responda(
        "Seu pedido recebeu uma atualização.",
        cliente.email,
        f"Seu pedido está {dados['status']}.",
        render_template("email_pedido.html", **_contexto_email_pedido(pedido, data_confirma)),
    )

    return render_template("pagina de pedidos.html")

@chefe_bp.get("/preparo")
def enviar_preparo():
    """Retorna, em JSON, a ficha de preparo completa de um pedido.

    Inclui os cardápios do pedido com seus pratos (e as fichas técnicas de
    cada prato) e as bebidas do pedido (avulsas ou vindas do cardápio), cada
    uma com sua ficha técnica.
    """
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
            "num_convidados": vinculo.num_convidados,
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
        "observacao": pedido.observacao,
        "cardapios": cardapios_resposta,
        "bebidas": bebidas_resposta,
    })
