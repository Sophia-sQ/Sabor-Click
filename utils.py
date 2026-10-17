from os import environ as env





from datetime import datetime
from zoneinfo import ZoneInfo
from calendar import monthrange
from dateutil.relativedelta import relativedelta

from decimal import Decimal, InvalidOperation, ROUND_HALF_UP

#interação com cliente


#formatação monetária
def moeda_para_centavos(valor):
    """Pega um valor monetário e o transforma em centavos."""
    
    texto = str(valor).strip().replace("R$", "").replace(" ", "")
    if "," in texto:
        texto = texto.replace(".", "").replace(",", ".")
    try:
        return int((Decimal(texto) * 100).quantize(Decimal("1"), rounding=ROUND_HALF_UP))
    except InvalidOperation as erro:
        raise ValueError("Valor monetário inválido") from erro

def formatar_moeda(centavos):
    """Pega um valor em centavos e retorna formatado como Real."""
    
    valor = Decimal(int(centavos)) / 100
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

def calcular_periodo(meses_antes: int) -> int:
    """Calcula o dia equivalente em um mês qualquer.

    Args:
        meses_antes (int): quantos meses antes da data de hoje.

    Returns:
        int: dia equivalente naquele mês.
    """

    hoje = datetime.now(ZoneInfo("America/Sao_Paulo"))
    
    # True se hoje for o último dia do mês
    ultimo_dia_mes = (int(hoje.day) == monthrange(int(hoje.year), int(hoje.month))[1])
    
    dia = hoje.day
    
    if ultimo_dia_mes:
        dia_mes_passado = hoje - relativedelta(months=meses_antes)
        dia = monthrange(int(dia_mes_passado.year), int(dia_mes_passado.month))[1]
    
    return dia

def hoje() -> datetime:
    """Retorna a data de hoje.

    Returns:
        datetime: data de hoje.
    """
    return datetime.now(ZoneInfo("America/Sao_Paulo"))

def mes_passado() -> datetime:
    """Retorna mes e ano passado.

    Returns:
        datetime: data de hoje.
    """
    return datetime.now(ZoneInfo("America/Sao_Paulo")) - relativedelta(months=1)