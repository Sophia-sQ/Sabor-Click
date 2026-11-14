from datetime import date

from sqlalchemy import func

from model.pedido_model import Pedido, listar_pedidos_periodo, buscar_cardapios_pedido, listar_pedidos_entre_datas
from model.servico_model import buscar_servico_por_id

from utils import calcular_periodo, hoje, mes_passado, ultimos_30_dias, semana_passada

# ================================= funções internas =================================

def _pedidos_30_dias(status=None) -> list:
    """Retorna os pedidos de um status específico nos últimos 30 dias.

    Args:
        status (str | None, optional): status para filtragem. Padrão: None.

    Returns:
        list: lista de pedidos que se enquadram no período e status.
    """
    
    data_inicio=ultimos_30_dias()
    return listar_pedidos_entre_datas(data_inicio.year, data_inicio.month, data_inicio.day, status=status) or []

def _pedidos_mensais(status: str = "concluido") -> tuple[list, list]:
    """Retorna os pedidos do mês atual e do mês passado no mesmo período.

    Args:
        status (str, optional): status para filtragem. Padrão: "concluido".

    Returns:
        tuple[list, list]: (pedidos do mês atual, pedidos do mês passado).
    """

    
    data_hoje = hoje()
    data_mes_passado = mes_passado()
    
    pedidos_atual=listar_pedidos_periodo(data_hoje.year, data_hoje.month, data_hoje.day, status)
    pedidos_anterior=listar_pedidos_periodo(data_mes_passado.year, data_mes_passado.month, calcular_periodo(1), status)
    
    return (pedidos_atual or [], pedidos_anterior or [])

def _faturamento() -> tuple[int, int]:
    """Calcula o faturamento do mês atual e do mês anterior.

    Returns:
        tuple[int, int]: (faturamento do mês atual, faturamento do mês anterior).
    """
    
    pedidos=_pedidos_mensais()
    
    faturamento_atual=0
    faturamento_anterior=0
    
    for pedido in pedidos[0]:
        faturamento_atual+=pedido.valor_total or 0
    
    for pedido in pedidos[1]:
        faturamento_anterior+=pedido.valor_total or 0
    
    return (faturamento_atual, faturamento_anterior)

# =================================== RELATÓRIOS ======================================

def resumo_pedidos_por_dia(inicio: date, fim: date) -> list[dict]:
    """Agrupa os pedidos pela data do evento e pelo status, com datas inclusivas."""
    resultados = (
        Pedido.query.with_entities(
            Pedido.data_evento, Pedido.status, func.count(), func.sum(Pedido.valor_total)
        )
        .filter(Pedido.data_evento.between(inicio, fim))
        .group_by(Pedido.data_evento, Pedido.status)
        .order_by(Pedido.data_evento, Pedido.status)
        .all()
    )
    return [
        {
            "data": dia.isoformat(),
            "status": status,
            "quantidade": quantidade,
            "receita": str(valor) if status == "concluido" else "0",
        }
        for dia, status, quantidade, valor in resultados
    ]


def pedidos_quantidade() -> tuple[int, float | None]:
    """Conta os pedidos do mês e compara com o mesmo período do mês anterior.

    Returns:
        tuple[int, float | None]: total de pedidos e variação percentual em
        relação ao período anterior (None quando não há base de comparação).
    """
    pedidos=_pedidos_mensais()
    
    n_pedidos_atual=len(pedidos[0])
    n_pedidos_anterior=len(pedidos[1])
    
    porcentagem = (((n_pedidos_atual - n_pedidos_anterior) * 100/ n_pedidos_anterior) if n_pedidos_anterior > 0 else None)
    
    return (n_pedidos_atual, porcentagem)

def pedidos_tipo() -> dict:
    """Conta quantas vezes cada serviço foi pedido nos últimos 30 dias.

    Returns:
        dict: contagem de pedidos por serviço.
    """
    
    servicos ={
        "Chef_em_casa": 0,
        "Buffet": 0,
        "Mesa_de_salgados": 0,
        "Bar": 0
    }
    
    pedidos=_pedidos_30_dias()
    
    for pedido in pedidos:
        cardapios=buscar_cardapios_pedido(pedido.id_pedido)
        if not cardapios:
            continue
        for cardapio in cardapios:
            servico=buscar_servico_por_id(cardapio.id_servico)
            if servico is None:
                continue
            # servico [nome do servico] += 1
            if servico.nome in servicos:
                servicos[servico.nome]+=1

    return servicos

def pedidos_status() -> dict:
    """Conta quantos pedidos do mês existem em cada status.

    Returns:
        dict: contagem de pedidos por status.
    """
    status ={
        "aguardando": 0,
        "confirmado": 0, 
        "em preparo": 0, 
        "concluido": 0,
        "cancelado": 0
    }

    pedidos=_pedidos_mensais(None)[0]
    
    for pedido in pedidos:
        if pedido.status in status:
            status[pedido.status]+=1
        
    return status

def faturamento_periodo() -> tuple[int, float | None]:
    """Soma o faturamento do mês e compara com o mesmo período do mês anterior.

    Returns:
        tuple[int, float | None]: faturamento total e variação percentual em
        relação ao período anterior (None quando não há base de comparação).
    """
    
    valor=_faturamento()
    
    porcentagem = (((valor[0] - valor[1]) * 100 / valor[1]) if valor[1] > 0 else None)
    
    return (valor[0], porcentagem)

def ticket_medio_periodo() -> tuple[int, float]:
    """Calcula o ticket médio do mês e compara com o mês anterior.

    Returns:
        tuple[int, float]: ticket médio atual e variação percentual em relação
        ao período anterior.
    """
    
    # valores monetários
    valores = _faturamento()
        
    faturamento_atual=valores[0]
    faturamento_anterior=valores[1]
    
    # numero de pedidos
    pedidos = _pedidos_mensais()
    
    total_pedidos_atual = len(pedidos[0])
    total_pedidos_anterior = len(pedidos[1])
    
    # calculo da média
    if total_pedidos_atual <= 0:
        return(0, 0)
    
    media_atual = (faturamento_atual/total_pedidos_atual)
    
    if total_pedidos_anterior <= 0:
        return(media_atual, 0)
    
    media_anterior = (faturamento_anterior/total_pedidos_anterior)
    
    porcentagem = (((media_atual - media_anterior) * 100/ media_anterior) if media_anterior > 0 else 0)
    
    return (media_atual, porcentagem)

def faturamento_semanal() -> dict:
    """Calcula o faturamento de cada uma das últimas 6 semanas.

    Returns:
        dict: faturamento por semana (chaves 'S1' a 'S6').
    """
    
    semanas = {
        'S1': 0,
        'S2': 0,
        'S3': 0,
        'S4': 0,
        'S5': 0,
        'S6': 0,
    }
    for i in range(1, 7):
        data_inicio, data_fim=semana_passada(i)
        pedidos = listar_pedidos_entre_datas(data_inicio.year, data_inicio.month, data_inicio.day,
                                             data_fim.year, data_fim.month, data_fim.day) or []
        for pedido in pedidos:
            semanas['S'+str(i)]+=pedido.valor_total or 0
    
    return semanas
