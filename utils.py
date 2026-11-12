"""Funções utilitárias de formatação de nomes, valores monetários e datas."""

import re
import unicodedata
from calendar import monthrange
from datetime import date, datetime, timedelta, time
from decimal import ROUND_HALF_UP, Decimal, InvalidOperation
from zoneinfo import ZoneInfo

from dateutil.relativedelta import relativedelta

from decimal import Decimal, InvalidOperation, ROUND_HALF_UP

# ==================== FUNÇÕES DE FORMATAÇÃO DE NOMES ====================
def formatar_nome(nome_completo: str) -> str:
    """Ajusta a formatação de um nome removendo '_' e normlizando capitalização.

    Args:
        nome_completo (str): nome ou expressão a ser formatado.

    Returns:
        str: nome formatado.
    """

    nome_formatado = nome_completo.strip().replace("_", " ").lower()
    return nome_formatado

def gerar_slug(texto: str) -> str:
    """Gera um slug a partir de um texto usando apenas a biblioteca padrão.

    Normaliza acentos (NFKD + remoção de não-ASCII), passa para minúsculo,
    troca qualquer caractere fora de [a-z0-9] por hífen, colapsa hífens
    repetidos e remove hífens das pontas. Não depende do pacote 'slugify'.

    Args:
        texto (str): texto de origem (ex.: nome do cardápio).

    Returns:
        str: slug no formato 'texto-exemplo' (pode ser vazio se não houver
            caracteres aproveitáveis).
    """
    normalizado = unicodedata.normalize("NFKD", texto)
    ascii_texto = normalizado.encode("ascii", "ignore").decode("ascii")
    ascii_texto = ascii_texto.lower()
    ascii_texto = re.sub(r"[^a-z0-9]+", "-", ascii_texto)
    ascii_texto = re.sub(r"-{2,}", "-", ascii_texto)
    return ascii_texto.strip("-")

def slug_unico(base_slug: str, slugs_existentes: set[str]) -> str:
    """Garante que um slug seja único em relação a um conjunto existente.

    Se o slug-base já estiver em uso, acrescenta sufixos numéricos ('-2',
    '-3', ...) até encontrar um slug livre, evitando sobrescrever entradas
    como 'feijoada'.

    Args:
        base_slug (str): slug desejado (saída de gerar_slug).
        slugs_existentes (set[str]): slugs já em uso.

    Returns:
        str: slug único que não pertence a slugs_existentes.
    """
    if base_slug not in slugs_existentes:
        return base_slug

    contador = 2
    while f"{base_slug}-{contador}" in slugs_existentes:
        contador += 1
    return f"{base_slug}-{contador}"

def formatar_nome_proprio(nome_completo: str) -> str:
    """Ajusta a capitalização de um nome próprio mantendo conectivos em minúscula.

    Converte a primeira letra de cada palavra para maiúscula (Title Case), mas
    mantém artigos, preposições e conjunções comuns do português (ex.: 'de',
    'da', 'e') em minúsculas, exceto quando são a primeira palavra do nome.

    Args:
        nome_completo (str): nome ou expressão a ser formatado.

    Returns:
        str: nome formatado com as devidas maiúsculas e minúsculas.
    """
    
    # Lista de palavras que devem permanecer em minúscula no meio do nome
    conectivos = ["de", "da", "do", "das", "dos", "e", "em", "por", "com", "o", "a", "os", "as"]

    # Divide o nome em palavras individuais
    palavras = nome_completo.strip().replace("_", " ").split()
    nome_formatado = []

    for i, palavra in enumerate(palavras):
        palavra_lower = palavra.lower()

        # A primeira palavra do nome SEMPRE começa com maiúscula.
        # As demais só começam com maiúscula se não forem conectivos.
        if i == 0 or palavra_lower not in conectivos:
            nome_formatado.append(palavra.capitalize())
        else:
            nome_formatado.append(palavra_lower)
    # Junta as palavras novamente em uma única string
    return " ".join(nome_formatado)

def nome_exibicao(nome: str) -> str:
    """Formata, apenas para exibição, um nome normalizado vindo do banco.

    Usado como filtro Jinja ('nome_exibicao'). Reaproveita a lógica de
    formatar_nome_proprio (Title Case com conectivos em minúscula) para
    transformar nomes gravados em minúsculas/sem acento (ex.: 'feijoada
    completa') em uma forma apresentável (ex.: 'Feijoada completa'). Não muta o
    nome armazenado; apenas retorna a string formatada. Como os nomes do banco
    não têm acento, a saída também não terá -- comportamento aceito.

    Args:
        nome (str): nome normalizado do banco.

    Returns:
        str: nome formatado para exibição.
    """
    return formatar_nome_proprio(nome or "")

# ==================== FUNÇÕES DE FORMATAÇÃO MONETÁRIA ====================
def moeda_para_centavos(valor) -> int:
    """Converte um valor monetário (texto ou número) em centavos (inteiro).

    Aceita formatos com 'R$', espaços, ponto de milhar e vírgula decimal.

    Args:
        valor: valor monetário a converter (ex.: "R$ 1.234,56").

    Returns:
        int: valor correspondente em centavos.

    Raises:
        ValueError: se o valor informado não for um número monetário válido.
    """
    
    texto = str(valor).strip().replace("R$", "").replace(" ", "")
    if "," in texto:
        texto = texto.replace(".", "").replace(",", ".")
    try:
        return int((Decimal(texto) * 100).quantize(Decimal(1), rounding=ROUND_HALF_UP))
    except InvalidOperation as erro:
        raise ValueError("Valor monetário inválido") from erro

def formatar_moeda(centavos) -> str:
    """Formata um valor em centavos como moeda brasileira (Real).

    Args:
        centavos: valor em centavos a ser formatado.

    Returns:
        str: valor formatado no padrão brasileiro (ex.: "R$ 1.234,56").
    """
    valor = Decimal(int(centavos)) / 100
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

# ==================== FUNÇÕES DE DATA E HORA ====================
def calcular_periodo(meses_antes: int) -> int:
    """Calcula o dia equivalente em um mês anterior ao atual.

    Quando hoje é o último dia do mês, retorna o último dia do mês de
    referência; caso contrário, retorna o dia de hoje.

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
    """Retorna a data e hora atuais no fuso de São Paulo."""

    return datetime.now(ZoneInfo("America/Sao_Paulo"))

def mes_passado() -> datetime:
    """Retorna a data e hora de um mês atrás, no fuso de São Paulo."""

    return datetime.now(ZoneInfo("America/Sao_Paulo")) - relativedelta(months=1)

def semana_passada(num_semanas: int) -> tuple[date, date]:
    """Retorna o primeiro e o último dia de uma semana anterior.

    Considera a semana de segunda-feira a domingo.

    Args:
        num_semanas (int): quantas semanas antes da atual (1 = semana passada,
            2 = retrasada, etc.).

    Returns:
        tuple[date, date]: data inicial (segunda-feira) e data final (domingo).

    Raises:
        ValueError: se num_semanas for menor que 1.
    """
    if num_semanas < 1:
        raise ValueError("num_semanas deve ser maior ou igual a 1")

    data_hoje = hoje().date()

    inicio_semana_atual = data_hoje - timedelta(days=data_hoje.weekday())

    inicio_semana_passada = inicio_semana_atual - timedelta(weeks=num_semanas)

    fim_semana_passada = inicio_semana_passada + timedelta(days=6)
    return (inicio_semana_passada, fim_semana_passada)

def ultimos_30_dias() -> datetime:
    """Retorna a data e hora de exatamente 30 dias atrás."""
    trita_dias_atras = hoje() - timedelta(days=30)

    return trita_dias_atras

def para_data(dia: int, mes: int, ano: int) -> date:
    """Monta um objeto de data a partir de dia, mês e ano.

    Args:
        dia (int): dia da data.
        mes (int): mês da data.
        ano (int): ano da data.

    Returns:
        date: data correspondente aos valores informados.
    """
    return datetime(ano, mes, dia).date()

def string_para_data(data: str) -> date:
    """Converte uma string 'AAAA-MM-DD' em um objeto date."""
    return datetime.strptime(data, "%Y-%m-%d").date()

def string_para_hora(hora: str) -> time:
    """Converte uma string 'HH:MM' em um objeto time."""
    return  datetime.strptime(hora, "%H:%M").time()
