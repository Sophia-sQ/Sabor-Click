"""Rota administrativa de acompanhamento dos pedidos em andamento (somente leitura)."""

from . import admin_bp

from flask import render_template

from model.pedido_model import (
    listar_pedidos_em_andamento,
    buscar_cardapios_pedido,
    listar_bebidas_do_pedido,
    buscar_bebida_por_id,
)
from model.servico_model import buscar_cardapio_por_id
from model.usuario_model import buscar_usuario_por_id

# Rótulos amigáveis dos status exibidos e o modificador de cor do badge.
# Mantém o vocabulário visual das prévias (.status + .verde/.amarelo).
_ROTULO_STATUS = {
    "aguardando": "Aguardando",
    "confirmado": "Confirmado",
    "em preparo": "Em preparo",
    "concluido": "Concluído",
    "cancelado": "Cancelado",
}
_CLASSE_STATUS = {
    "confirmado": "amarelo",
    "em preparo": "amarelo",
    "concluido": "verde",
}


def _resumo_pedido_admin(pedido) -> dict:
    """Serializa um pedido em andamento para a tabela administrativa.

    Expõe apenas campos não sensíveis (sem CPF/e-mail do cliente): id, data do
    evento, resumo de itens, status (rótulo + classe de cor), total formatado e
    o nome do chef responsável (ou aviso quando ainda não há chef designado). O
    nº de convidados vem de CardapioPedido e os valores monetários (em centavos)
    são formatados por ``utils.formatar_moeda``.

    Args:
        pedido: objeto Pedido em andamento.

    Returns:
        dict: dados serializados do pedido para exibição.
    """
    from utils import formatar_moeda, nome_exibicao

    itens = []
    num_convidados = 0
    for vinculo in buscar_cardapios_pedido(pedido.id_pedido) or []:
        num_convidados += vinculo.num_convidados or 0
        cardapio = buscar_cardapio_por_id(vinculo.id_cardapio)
        if cardapio and cardapio.nome:
            itens.append(f"{vinculo.num_convidados} × {nome_exibicao(cardapio.nome)}")

    for item in listar_bebidas_do_pedido(pedido.id_pedido) or []:
        bebida = buscar_bebida_por_id(item.id_bebida)
        if bebida and bebida.nome:
            itens.append(f"{item.qtd} × {nome_exibicao(bebida.nome)}")

    chefe = buscar_usuario_por_id(pedido.id_chefe) if pedido.id_chefe else None

    return {
        "id_pedido": pedido.id_pedido,
        "data_evento": pedido.data_evento.strftime("%d/%m/%Y") if pedido.data_evento else None,
        "itens": itens,
        "num_convidados": num_convidados,
        "status": pedido.status,
        "status_rotulo": _ROTULO_STATUS.get(pedido.status, pedido.status),
        "status_classe": _CLASSE_STATUS.get(pedido.status, ""),
        "valor_total": formatar_moeda(int(round(pedido.valor_total * 100))),
        "chefe": nome_exibicao(chefe.nome) if chefe else "Aguardando chef",
    }


@admin_bp.get("/pedidos")
def pagina_pedidos():
    """Exibe todos os pedidos em andamento para o administrador.

    Página somente leitura: lista os pedidos ativos ('confirmado'/'em preparo')
    sem alterar status nem expor dados sensíveis do cliente. O acesso é restrito
    ao cargo ADMIN pelo hook ``verificar_cargo`` do blueprint admin.

    Returns:
        str: template "pedidos.html" renderizado com os pedidos em andamento.
    """
    pedidos = listar_pedidos_em_andamento()
    pedidos_dados = [_resumo_pedido_admin(pedido) for pedido in pedidos]
    return render_template("pedidos.html", pedidos=pedidos_dados)
