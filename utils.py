<<<<<<< Updated upstream
from zoneinfo import ZoneInfo
from calendar import monthrange
from datetime import datetime, timedelta, date
=======
from calendar import monthrange
from datetime import date, datetime, timedelta
from decimal import ROUND_HALF_UP, Decimal, InvalidOperation
from zoneinfo import ZoneInfo

>>>>>>> Stashed changes
from dateutil.relativedelta import relativedelta

from decimal import Decimal, InvalidOperation, ROUND_HALF_UP

#nomes
def formatar_nome(nome_completo: str) -> str:
    """Ajusta a capitalização de um nome próprio mantendo conectivos em minúscula.

    Converte a primeira letra de cada palavra para maiúscula (Title Case), 
    mas ignora artigos, preposições e conjunções comuns no idioma português 
    (ex: 'de', 'da', 'e'), mantendo-os em letras minúsculas, exceto se 
    forem a primeira palavra do nome.

    Args:
        nome_completo (str): O nome ou expressão que será formatado.

    Returns:
        str: O nome formatado com as devidas maiúsculas e minúsculas.
<<<<<<< Updated upstream
    """
    
    # Lista de palavras que devem permanecer em minúscula no meio do nome
    conectivos = ["de", "da", "do", "das", "dos", "e", "em", "por", "com", "o", "a", "os", "as"]
    
    # Divide o nome em palavras individuais
    palavras = nome_completo.strip().replace("_", " ").split()
    nome_formatado = []
    
    for i, palavra in enumerate(palavras):
        palavra_lower = palavra.lower()
        
=======

    """
    # Lista de palavras que devem permanecer em minúscula no meio do nome
    conectivos = ["de", "da", "do", "das", "dos", "e", "em", "por", "com", "o", "a", "os", "as"]

    # Divide o nome em palavras individuais
    palavras = nome_completo.strip().replace("_", " ").split()
    nome_formatado = []

    for i, palavra in enumerate(palavras):
        palavra_lower = palavra.lower()

>>>>>>> Stashed changes
        # A primeira palavra do nome SEMPRE começa com maiúscula.
        # As demais só começam com maiúscula se não forem conectivos.
        if i == 0 or palavra_lower not in conectivos:
            nome_formatado.append(palavra.capitalize())
        else:
            nome_formatado.append(palavra_lower)
<<<<<<< Updated upstream
            
=======

>>>>>>> Stashed changes
    # Junta as palavras novamente em uma única string
    return " ".join(nome_formatado)


#formatação monetária
def moeda_para_centavos(valor):
    """Pega um valor monetário e o transforma em centavos."""
<<<<<<< Updated upstream
    
=======
>>>>>>> Stashed changes
    texto = str(valor).strip().replace("R$", "").replace(" ", "")
    if "," in texto:
        texto = texto.replace(".", "").replace(",", ".")
    try:
<<<<<<< Updated upstream
        return int((Decimal(texto) * 100).quantize(Decimal("1"), rounding=ROUND_HALF_UP))
=======
        return int((Decimal(texto) * 100).quantize(Decimal(1), rounding=ROUND_HALF_UP))
>>>>>>> Stashed changes
    except InvalidOperation as erro:
        raise ValueError("Valor monetário inválido") from erro

def formatar_moeda(centavos):
    """Pega um valor em centavos e retorna formatado como Real."""
<<<<<<< Updated upstream
    
=======
>>>>>>> Stashed changes
    valor = Decimal(int(centavos)) / 100
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

def calcular_periodo(meses_antes: int) -> int:
    """Calcula o dia equivalente em um mês qualquer.

    Args:
        meses_antes (int): quantos meses antes da data de hoje.

    Returns:
        int: dia equivalente naquele mês.
<<<<<<< Updated upstream
    """

    hoje = datetime.now(ZoneInfo("America/Sao_Paulo"))
    
    # True se hoje for o último dia do mês
    ultimo_dia_mes = (int(hoje.day) == monthrange(int(hoje.year), int(hoje.month))[1])
    
    dia = hoje.day
    
    if ultimo_dia_mes:
        dia_mes_passado = hoje - relativedelta(months=meses_antes)
        dia = monthrange(int(dia_mes_passado.year), int(dia_mes_passado.month))[1]
    
=======

    """
    hoje = datetime.now(ZoneInfo("America/Sao_Paulo"))

    # True se hoje for o último dia do mês
    ultimo_dia_mes = (int(hoje.day) == monthrange(int(hoje.year), int(hoje.month))[1])

    dia = hoje.day

    if ultimo_dia_mes:
        dia_mes_passado = hoje - relativedelta(months=meses_antes)
        dia = monthrange(int(dia_mes_passado.year), int(dia_mes_passado.month))[1]

>>>>>>> Stashed changes
    return dia

def hoje() -> datetime:
    """Retorna a data de hoje.

    Returns:
        datetime: data de hoje.
<<<<<<< Updated upstream
=======

>>>>>>> Stashed changes
    """
    return datetime.now(ZoneInfo("America/Sao_Paulo"))

def mes_passado() -> datetime:
    """Retorna mes e ano passado.

    Returns:
        datetime: data de hoje.
<<<<<<< Updated upstream
=======

>>>>>>> Stashed changes
    """
    return datetime.now(ZoneInfo("America/Sao_Paulo")) - relativedelta(months=1)

def semana_passada(num_semanas: int) -> tuple[date, date]:
    """Retorna o primeiro e o último dia de uma semana anterior.

    Considera a semana de segunda-feira a domingo.

    Args:
        num_semanas (int): Quantas semanas antes da atual.
            1 representa a semana passada, 2 a retrasada, etc.

    Returns:
        tuple[date, date]: Data inicial (segunda-feira) e
        data final (domingo).

    Raises:
        ValueError: Se num_semanas for menor que 1.
<<<<<<< Updated upstream
=======

>>>>>>> Stashed changes
    """
    if num_semanas < 1:
        raise ValueError("num_semanas deve ser maior ou igual a 1")

    data_hoje = hoje().date()

    inicio_semana_atual = data_hoje - timedelta(days=data_hoje.weekday())

    inicio_semana_passada = inicio_semana_atual - timedelta(weeks=num_semanas)

    fim_semana_passada = inicio_semana_passada + timedelta(days=6)
<<<<<<< Updated upstream
    
=======

>>>>>>> Stashed changes
    return (inicio_semana_passada, fim_semana_passada)

def ultimos_30_dias():
    """Calcula a data de exatamente 30 dias atrás.

    Returns:
        datetime: data de exatamente 30 dias atrás.
<<<<<<< Updated upstream
    """
    
=======

    """
>>>>>>> Stashed changes
    trita_dias_atras = hoje() - timedelta(days=30)

    return trita_dias_atras

def para_data(dia: int, mes: int, ano: int) -> datetime:
    """_summary_

    Args:
        dia (int): dia da data.
        mes (int): mês da data.
        ano (int): ano da data.

    Returns:
        datetime: data em formato YY/MM/DD.
<<<<<<< Updated upstream
    """
    
=======

    """
>>>>>>> Stashed changes
    return datetime(ano, mes, dia).date()

def string_para_data(data:str):
    return datetime.strptime(data, "%Y-%m-%d").date()

def string_para_hora(hora:str):
<<<<<<< Updated upstream
    return  datetime.strptime(hora, "%H:%M").time()
=======
    return  datetime.strptime(hora, "%H:%M").time()
>>>>>>> Stashed changes
