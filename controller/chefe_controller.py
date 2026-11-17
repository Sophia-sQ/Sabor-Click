"""Rotas do chefe: aceitar e atualizar o status de pedidos."""
import threading
from datetime import datetime
from zoneinfo import ZoneInfo

from flask import Blueprint, render_template, request, session, jsonify, flash, redirect, url_for, abort, current_app

from model.ficha_model import listar_ficha_tecnica_por_bebida, listar_ficha_tecnica_por_prato, listar_pratos_por_cardapio
from model.pedido_model import (buscar_cardapios_pedido, listar_bebidas_do_pedido, buscar_bebida_por_id, 
                                atualizar_pedido, buscar_pedido_por_id, listar_pedido_por_status, 
                                buscar_pedido_ativo_por_chefe)
from model.servico_model import buscar_cardapio_por_id, listar_bancadas_do_servico
from model.usuario_model import buscar_usuario_por_id, buscar_endereco_por_id, registrar_log

from services import enviar_email_nao_responda

chefe_bp = Blueprint("chefe", __name__, url_prefix="/pedido")


def _enviar_email_async(app, assunto, destinatario, preheader, html):
    """Dispara o e-mail transacional numa thread separada, sem bloquear o request.

    O envio por SMTP (Flask-Mail) é lento e, feito dentro do request, adiciona
    segundos de latência às ações da cozinha. Para responder ao chef de imediato,
    o envio roda numa ``threading.Thread`` daemon. O HTML já vem renderizado do
    request (onde o app/request context existe), de modo que a thread só precisa
    abrir um ``app_context`` para que ``mail.send`` funcione.

    Falhas de envio NÃO podem derrubar a aplicação: como rodam fora do request,
    a exceção é capturada e apenas registrada no log, nunca propagada.

    Args:
        app: aplicação Flask real (``current_app._get_current_object()``).
        assunto (str): assunto do e-mail.
        destinatario (str): e-mail de destino (criptografado).
        preheader (str): corpo em texto puro / preheader.
        html (str): corpo HTML já renderizado no request.
    """
    def _alvo():
        with app.app_context():
            try:
                enviar_email_nao_responda(assunto, destinatario, preheader, html)
            except Exception as erro:  # noqa: BLE001 - envio em background não pode derrubar o app
                app.logger.exception(f"Falha ao enviar e-mail de notificação do pedido.\n {erro}")

    threading.Thread(target=_alvo, daemon=True).start()

_MSG_ABORT_ESTOQUE = "Estoque insuficiente para confirmar o pedido"


def _e_erro_de_estoque(exc: Exception) -> bool:
    """Indica se a exceção corresponde ao abort de estoque insuficiente.

    Inspeciona a mensagem da própria exceção e a de sua causa de baixo nível
    (``exc.orig``, o erro do driver sqlite3) procurando o texto do
    RAISE(ABORT) definido na trigger de baixa de estoque. Assim, apenas o
    abort de estoque gera a mensagem que menciona estoque; qualquer outra
    falha cai no tratamento genérico.

    Args:
        exc (Exception): exceção capturada ao transicionar o status do pedido.

    Returns:
        bool: True se a exceção for o abort de estoque insuficiente.
    """
    if _MSG_ABORT_ESTOQUE in str(exc):
        return True
    orig = getattr(exc, "orig", None)
    return orig is not None and _MSG_ABORT_ESTOQUE in str(orig)


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
            "subtotal": formatar_moeda(int(round(item.valor_total * 100))),
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
        "valor_total": formatar_moeda(int(round(pedido.valor_total * 100))),
        "data_evento": pedido.data_evento.strftime("%d/%m/%Y") if pedido.data_evento else None,
        "hora_inicio": pedido.hora_inicio.strftime("%H:%M") if pedido.hora_inicio else None,
        "hora_fim": pedido.hora_fim.strftime("%H:%M") if pedido.hora_fim else None,
        "endereco": endereco_linha,
        "cardapios": cardapios,
        "bebidas": bebidas,
        "data_confirmacao": quando.strftime("%d/%m/%Y %H:%M") if quando else None,
        "ano": (quando or pedido.criado_em).strftime("%Y"),
    }


def _resumo_pedido(pedido) -> dict:
    """Serializa um pedido da fila para o bloco JSON consumido pela cozinha.

    Expõe apenas os campos necessários para renderizar os cards da fila e os
    contadores, sem vazar dados sensíveis. O nº de convidados é agregado dos
    cardápios do pedido e o resumo de itens é montado a partir dos cardápios e
    bebidas vinculados.

    Args:
        pedido: objeto Pedido aguardando preparo.

    Returns:
        dict: dados serializados do pedido.
    """
    from utils import formatar_moeda

    num_convidados = 0
    itens = []
    for vinculo in buscar_cardapios_pedido(pedido.id_pedido) or []:
        num_convidados += vinculo.num_convidados or 0
        cardapio = buscar_cardapio_por_id(vinculo.id_cardapio)
        if cardapio and cardapio.nome:
            itens.append(f"{vinculo.num_convidados} × {cardapio.nome}")

    for item in listar_bebidas_do_pedido(pedido.id_pedido) or []:
        bebida = buscar_bebida_por_id(item.id_bebida)
        if bebida and bebida.nome:
            itens.append(f"{item.qtd} × {bebida.nome}")

    return {
        "id_pedido": pedido.id_pedido,
        "observacao": pedido.observacao,
        "criado_em": pedido.criado_em.strftime("%Hh%M") if pedido.criado_em else None,
        "valor_total": formatar_moeda(int(round(pedido.valor_total * 100))),
        "data_evento": pedido.data_evento.strftime("%d/%m/%Y") if pedido.data_evento else None,
        "hora_inicio": pedido.hora_inicio.strftime("%H:%M") if pedido.hora_inicio else None,
        "hora_fim": pedido.hora_fim.strftime("%H:%M") if pedido.hora_fim else None,
        "num_convidados": num_convidados,
        "itens": itens,
    }


@chefe_bp.get('/cozinha')
def pedidos():
    """Exibe a fila da cozinha com os pedidos aguardando preparo.

    Returns:
        str: template "cozinha.html" renderizado com os pedidos aguardando.
    """

    pedidos = listar_pedido_por_status("aguardando")
    pedidos_dados = [_resumo_pedido(pedido) for pedido in pedidos]
    return render_template("cozinha.html", pedidos_dados=pedidos_dados)


@chefe_bp.get("/cozinha/fila")
def fila_cozinha():
    """Devolve, em JSON, a fila de pedidos 'aguardando' da cozinha.

    Endpoint somente leitura consumido pela tela da cozinha para rebuscar a
    fila do servidor (ex.: após concluir um pedido e liberar a bancada),
    reaproveitando ``_resumo_pedido`` para não expor campos sensíveis. O hook
    de autenticação do before_request redireciona usuários não autenticados;
    o JS trata esse caso pelo guard de redirect/content-type.

    Returns:
        Response: JSON com a lista dos pedidos aguardando (campos seguros).
    """
    return jsonify([_resumo_pedido(pedido) for pedido in listar_pedido_por_status("aguardando")])


@chefe_bp.route("/aceitar", methods=["POST"])
def aceitar_pedido():
    """Confirma um pedido, registra o log e notifica o cliente.

    Lê o id do pedido do corpo JSON, atualiza o status para 'confirmado',
    registra a ação e dispara (em background) o e-mail de confirmação ao
    cliente.

    Returns:
        Response: JSON com o resultado do aceite. Em sucesso, {'ok': True, ...};
        nos caminhos de falha (sem permissão, pedido inexistente, guarda de
        pedido único, abortos de estoque) retorna JSON de erro com status 4xx.
    """
    dados = request.get_json(silent=True) or {}
    pedido = buscar_pedido_por_id(dados.get("id"))
    if not pedido:
        return jsonify({"ok": False, "erro": "Pedido não encontrado."}), 404

    # Só aceitamos pedidos que ainda estão na fila (aguardando). Isso evita
    # reaproveitar/reconfirmar um pedido já em andamento ou encerrado.
    if pedido.status != "aguardando":
        return jsonify({"ok": False, "erro": "Este pedido não está mais disponível para aceite."}), 409

    data_confirma = datetime.now(ZoneInfo("America/Sao_Paulo"))

    if buscar_pedido_ativo_por_chefe(session.get("id")) is not None:
        return jsonify({"ok": False, "erro": "Finalize o pedido atual antes de aceitar outro"}), 409
    
    try:
        atualizado = atualizar_pedido(pedido.id_pedido, "confirmado", data_confirma, session.get("id"))
    except Exception as exc:  # noqa: BLE001 - precisamos inspecionar a exceção
        if _e_erro_de_estoque(exc):
            return jsonify({"ok": False, "erro": "Não foi possível aceitar o pedido: estoque insuficiente para um ou mais ingredientes."}), 409
        return jsonify({"ok": False, "erro": "Não foi possível aceitar o pedido. Tente novamente."}), 500

    if not atualizado:
        return jsonify({"ok": False, "erro": "Pedido não encontrado."}), 404

    chefe = buscar_usuario_por_id(session.get("id"))
    registrar_log("ACEITOU PEDIDO.", f"Em {data_confirma}, o chefe {chefe.nome} aceitou o pedido {pedido.id_pedido}.")
    data_confirma = data_confirma.astimezone(ZoneInfo("America/Sao_Paulo"))

    cliente = buscar_usuario_por_id(pedido.id_cliente)
    _enviar_email_async(
        current_app._get_current_object(),
        "Seu pedido foi aceito.",
        cliente.email_criptografado,
        "Seu pedido foi aceito.",
        render_template("email_pedido.html", **_contexto_email_pedido(pedido, data_confirma)),
    )

    return jsonify({"ok": True, "id": pedido.id_pedido, "status": "confirmado"})

@chefe_bp.route("/atualizar", methods=["GET", "POST"])
def atualizar_status():
    """Atualiza o status de um pedido e notifica o cliente por e-mail.

    No GET, exibe a página de pedidos. No POST, lê id e status do corpo JSON,
    atualiza o pedido, registra o log e envia o e-mail.

    Returns:
        Response: no GET, redireciona para a tela da cozinha. No POST, retorna
        JSON com o resultado da atualização ({'ok': True, ...}) ou JSON de erro
        com status 4xx em caso de status inválido ou falha na atualização.
    """
    if request.method == "GET":
        return redirect(url_for("chefe.pedidos"))

    dados = request.get_json(silent=True) or {}
    pedido = buscar_pedido_por_id(dados.get("id"))
    if not pedido:
        return jsonify({"ok": False, "erro": "Pedido não encontrado."}), 404

    from model.pedido_model import Pedido
    valores_aceitos = list(Pedido.status.type.enums)

    novo_status = dados.get("status")
    if novo_status not in valores_aceitos:
        return jsonify({"ok": False, "erro": "Valor de status inválido."}), 400

    transicoes_validas = {"confirmado": "em preparo", "em preparo": "concluido"}
    if transicoes_validas.get(pedido.status) != novo_status:
        return jsonify({"ok": False, "erro": "Transição de status não permitida."}), 409

    data_confirma = datetime.now(ZoneInfo("America/Sao_Paulo"))

    try:
        atualizado = atualizar_pedido(pedido.id_pedido, dados["status"], data_confirma, session.get("id"))
    except Exception:  # noqa: BLE001 - falha inesperada no commit
        return jsonify({"ok": False, "erro": "Não foi possível atualizar o pedido."}), 400

    if not atualizado:
        return jsonify({"ok": False, "erro": "Não foi possível atualizar o pedido."}), 400

    chefe = buscar_usuario_por_id(session.get("id"))

    if not chefe:
        return abort(400)

    registrar_log("ACEITOU PEDIDO.", f"Em {data_confirma}, o chefe {chefe.nome} atualizou o pedido {pedido.id_pedido} para '{dados['status']}'.")
    data_confirma = data_confirma.astimezone(ZoneInfo("America/Sao_Paulo"))

    cliente = buscar_usuario_por_id(pedido.id_cliente)

    _enviar_email_async(
        current_app._get_current_object(),
        "Seu pedido recebeu uma atualização.",
        cliente.email_criptografado,
        f"Seu pedido está {dados['status']}.",
        render_template("email_pedido.html", **_contexto_email_pedido(pedido, data_confirma)),
    )

    return jsonify({"ok": True, "id": pedido.id_pedido, "status": dados["status"]})

@chefe_bp.route("/cancelar", methods=["POST"])
def cancelar_pedido():
    """Cancela o pedido ativo do chef, registra o log e notifica o cliente.

    O chef pode cancelar um pedido a qualquer momento depois de tê-lo aceitado,
    ou seja, enquanto o status for 'confirmado' ou 'em preparo'. Pedidos
    'aguardando' (ainda na fila, não aceitos) não podem ser cancelados por aqui:
    o chef precisa aceitar antes. Lê o id do pedido do corpo JSON, valida o
    estado atual no servidor (não confia no cliente), transiciona o status para
    'cancelado', registra o log e envia e-mail de cancelamento ao cliente.

    O cancelamento NÃO estorna estoque: mudar o status para 'cancelado' não
    dispara a trigger de baixa (que só reage à transição para 'confirmado'),
    então o estoque já baixado permanece baixado e nenhum tratamento especial
    é necessário aqui.

    Returns:
        Response: JSON com o resultado do cancelamento. Em sucesso,
        {'ok': True, 'id': ..., 'status': 'cancelado'}; nos caminhos de falha
        (pedido inexistente, estado não cancelável, erro no commit) retorna
        JSON de erro com status 4xx/5xx.
    """
    dados = request.get_json(silent=True) or {}
    pedido = buscar_pedido_por_id(dados.get("id"))
    if not pedido:
        return jsonify({"ok": False, "erro": "Pedido não encontrado."}), 404

    if pedido.status not in ("confirmado", "em preparo"):
        return jsonify({"ok": False, "erro": "Este pedido não pode ser cancelado."}), 409

    data_cancelamento = datetime.now(ZoneInfo("America/Sao_Paulo"))

    try:
        atualizado = atualizar_pedido(pedido.id_pedido, "cancelado", id_chefe=session.get("id"))
    except Exception:  # noqa: BLE001 - falha inesperada no commit
        return jsonify({"ok": False, "erro": "Não foi possível cancelar o pedido."}), 500

    if not atualizado:
        return jsonify({"ok": False, "erro": "Pedido não encontrado."}), 404

    chefe = buscar_usuario_por_id(session.get("id"))
    if not chefe:
        return abort(400)

    registrar_log("CANCELOU PEDIDO.", f"Em {data_cancelamento}, o chefe {chefe.nome} cancelou o pedido {pedido.id_pedido}.")
    data_cancelamento = data_cancelamento.astimezone(ZoneInfo("America/Sao_Paulo"))

    cliente = buscar_usuario_por_id(pedido.id_cliente)
    # HTML renderizado no request; envio SMTP em background para não bloquear.
    _enviar_email_async(
        current_app._get_current_object(),
        "Seu pedido foi cancelado.",
        cliente.email_criptografado,
        "Seu pedido foi cancelado.",
        render_template("email_pedido.html", **_contexto_email_pedido(pedido, data_cancelamento)),
    )

    return jsonify({"ok": True, "id": pedido.id_pedido, "status": "cancelado"})

@chefe_bp.get("/preparo")
def enviar_preparo():
    """Retorna, em JSON, a ficha de preparo completa de um pedido.

    Inclui os cardápios do pedido com seus pratos (e as fichas técnicas de
    cada prato) e as bebidas do pedido (avulsas ou vindas do cardápio), cada
    uma com sua ficha técnica.
    """
    from model.ficha_model import buscar_ingrediente_por_id, buscar_prato_por_id

    pedido = buscar_pedido_ativo_por_chefe(session["id"])
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

    ids_servico = []
    for vinculo in buscar_cardapios_pedido(pedido.id_pedido) or []:
        cardapio = buscar_cardapio_por_id(vinculo.id_cardapio)
        if vinculo.id_servico is not None and vinculo.id_servico not in ids_servico:
            ids_servico.append(vinculo.id_servico)

        pratos_resposta = []
        for pc in listar_pratos_por_cardapio(vinculo.id_cardapio) or []:
            if hasattr(pc, "id_prato"):
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
            else:
                bebida = buscar_bebida_por_id(pc.id_bebida)
                pratos_resposta.append({
                    "id_bebida": pc.id_bebida,
                    "nome": bebida.nome if bebida else None,
                    "qtd": 1,
                    "descricao": bebida.descricao if bebida else None,
                    "ficha_tecnica": _ficha_bebida(pc.id_bebida),
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

    # -------- BANCADAS DOS SERVIÇOS DO PEDIDO --------

    bancadas_resposta = []
    ids_bancada_vistos = set()
    for id_servico in ids_servico:
        for bancada in listar_bancadas_do_servico(id_servico) or []:
            if not getattr(bancada, "ativo", True):
                continue
            if bancada.id_bancada in ids_bancada_vistos:
                continue
            ids_bancada_vistos.add(bancada.id_bancada)
            bancadas_resposta.append({
                "id_bancada": bancada.id_bancada,
                "nome": bancada.nome,
                "descricao": bancada.descricao,
            })

    return jsonify({
        "id_pedido": pedido.id_pedido,
        "status": pedido.status,
        "observacao": pedido.observacao,
        "cardapios": cardapios_resposta,
        "bebidas": bebidas_resposta,
        "bancadas": bancadas_resposta,
    })
