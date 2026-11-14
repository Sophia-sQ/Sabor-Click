"""Formatação do catálogo de bebidas avulsas da página pública do cliente.

As oito bebidas avulsas seed (as que o cliente escolhe fora do serviço de Bar)
têm nome de exibição, categoria (Com/Sem álcool), volume por porção e imagem de
fallback embutidos aqui como dados puros, derivados do cadastro do projeto
(``seeds.lista_bebida`` / ``seeds.ficha_bebidas``). Isso mantém a prévia e os
seeds funcionando sem acessar o banco.

Bebidas CRIADAS pelo admin (via catálogo real) também aparecem na página do
cliente: o chamador (``controller.cliente_controller._catalogo_bebidas``) passa
``incluir_todos=True`` e, para cada registro, já resolve a imagem a partir de
``docs/imagens-bebidas.json`` (campo ``arquivo`` sem o prefixo ``static/``,
portanto COM a extensão real) no campo ``imagem_rel``, além do volume derivado
(``volume_ml``). Assim a formatação continua independente de Flask/DB, mas a
imagem resolvida tem a extensão correta e qualquer bebida ativa é exibida.
"""
import unicodedata


def normalizar(nome):
    return ''.join(c for c in unicodedata.normalize('NFD', nome.replace('_', ' ')) if unicodedata.category(c) != 'Mn').lower().strip()


# Volumes por porção da ficha cadastrada no projeto, em mililitros.
# Todas as avulsas têm 200 ml por porção, exceto gin e uísque (70 ml por dose).
VOLUMES_AVULSOS = {
    'agua com gas': 200,
    'suco de abacaxi': 200,
    'refrigerante de guarana': 200,
    'cha preto': 200,
    'agua de coco': 200,
    'suco de melancia': 200,
    'gin': 70,
    'uisque de centeio rye': 70,
}

# Conjunto das oito bebidas avulsas permitidas (chaves normalizadas).
NOMES_AVULSOS = set(VOLUMES_AVULSOS)

# Bebidas consideradas alcoólicas (categoria 'Com álcool'). Vale tanto para as
# avulsas seed quanto para novas bebidas cujo nome normalizado bata com a chave.
NOMES_ALCOOLICOS = {'gin', 'uisque de centeio rye'}

# Nomes de exibição das avulsas seed (os nomes do banco vêm normalizados).
EXIBICAO_AVULSOS = {
    'agua com gas': 'Água com gás',
    'cha preto': 'Chá preto',
    'agua de coco': 'Água de coco',
    'refrigerante de guarana': 'Refrigerante de guaraná',
    'uisque de centeio rye': 'Uísque de centeio rye',
}


def _imagem_fallback(chave):
    """Caminho de imagem por palpite de nome, usado só para as avulsas seed.

    As avulsas seed e a prévia não carregam slug de imagem; o palpite por nome
    reproduz o comportamento histórico (arquivos já versionados em
    static/images/bebidas/<nome>.<ext>).
    """
    sem_extensao = chave.replace(' ', '-')
    extensao = '.png' if chave in {'refrigerante de guarana', 'suco de abacaxi', 'agua de coco', 'cha preto'} else '.jpg'
    return 'images/bebidas/' + sem_extensao + extensao


def _nome_exibicao(chave, nome_bruto):
    """Nome apresentável para a bebida (avulsa seed ou criada pelo admin)."""
    if chave in EXIBICAO_AVULSOS:
        return EXIBICAO_AVULSOS[chave]
    # Bebidas criadas pelo admin: título em Title Case a partir do nome do banco.
    return (nome_bruto or '').replace('_', ' ').strip().title()


def formatar_bebidas(registros, incluir_todos=False):
    """Formata os registros de bebida para a página pública do cliente.

    Args:
        registros (list[dict]): cada dict com ``id``, ``nome``, ``descricao``,
            ``preco`` e, opcionalmente, ``imagem_rel`` (caminho já resolvido a
            partir de docs/imagens-bebidas.json, relativo a static/, COM
            extensão), ``volume_ml`` (volume derivado da ficha) e
            ``imagem_slug``.
        incluir_todos (bool): quando True, inclui qualquer bebida (as criadas
            pelo admin, independentemente do nome). Quando False (padrão, usado
            pela prévia), só emite as oito avulsas seed, preservando a prévia.

    Returns:
        list[dict]: itens prontos para o template bebidas.html.
    """
    resultado = []
    for item in registros:
        chave = normalizar(item['nome'])
        eh_avulsa = chave in NOMES_AVULSOS

        # Prévia/seeds: só as oito avulsas. Página do cliente (incluir_todos):
        # qualquer bebida ativa, inclusive as criadas pelo admin.
        if not eh_avulsa and not incluir_todos:
            continue

        nome = _nome_exibicao(chave, item['nome'])
        descricao = item.get('descricao') or ''
        if normalizar(descricao) == chave:
            descricao = ''

        # Imagem: a resolução a partir do JSON (imagem_rel) já vem COM a
        # extensão real; preferimos sempre que informada. Sem ela, usamos o
        # palpite por nome das avulsas seed (prévia e seeds).
        imagem = item.get('imagem_rel')
        if not imagem and eh_avulsa:
            imagem = _imagem_fallback(chave)

        # Volume: preferimos o volume derivado (volume_ml_bebida) quando o
        # chamador o informa; caso contrário usamos o volume embutido das
        # avulsas (VOLUMES_AVULSOS), mantendo a prévia e as seeds funcionando.
        volume = item.get('volume_ml')
        if volume is None and eh_avulsa:
            volume = VOLUMES_AVULSOS.get(chave)

        categoria = 'Com álcool' if chave in NOMES_ALCOOLICOS else 'Sem álcool'

        resultado.append(dict(
            id=str(item['id']), nome=nome, descricao=descricao,
            volume_ml=volume, imagem=imagem,
            preco=float(item['preco']) if item.get('preco') is not None else None,
            categoria=categoria))
    return resultado


def catalogo_previa(registros=None):
    """Formata o catálogo avulso para a prévia administrativa.

    Recebe os registros já consultados pelo chamador (lista de dicts com
    ``id``, ``nome``, ``descricao`` e ``preco``). Quando nenhum registro é
    informado, usa os nomes do cadastro embutido e mantém o comportamento
    'sem preço' (``preco=None``), sem acessar o SQLite da prévia.
    """
    if registros is None:
        registros = [dict(id='previa-' + chave.replace(' ', '-'), nome=chave, preco=None)
                     for chave in NOMES_AVULSOS]
    return formatar_bebidas(registros)
