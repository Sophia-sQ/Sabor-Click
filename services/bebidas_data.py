"""Formatação do catálogo avulso, separado dos coquetéis do Bar.

As oito bebidas avulsas (as que o cliente escolhe fora do serviço de Bar) e
seus volumes por porção estão embutidos aqui como constantes de dados puros,
derivados do cadastro do projeto (``seeds.lista_bebida`` / ``seeds.ficha_bebidas``).
Isso evita simular o banco: a formatação não lê o arquivo-fonte de seeds nem
abre o SQLite diretamente, permanecendo independente da camada de modelo/DB.
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


def formatar_bebidas(registros):
    permitidos = NOMES_AVULSOS
    volumes = VOLUMES_AVULSOS
    exibicao = {'agua com gas': 'Água com gás', 'cha preto': 'Chá preto', 'agua de coco': 'Água de coco', 'refrigerante de guarana': 'Refrigerante de guaraná', 'uisque de centeio rye': 'Uísque de centeio rye'}
    resultado = []
    for item in registros:
        chave = normalizar(item['nome'])
        if chave not in permitidos:
            continue
        nome = exibicao.get(chave, item['nome'].replace('_', ' '))
        descricao = item.get('descricao') or ''
        if normalizar(descricao) == chave:
            descricao = ''
        resultado.append(dict(id=str(item['id']), nome=nome, descricao=descricao,
            volume_ml=volumes.get(chave), imagem='images/bebidas/' + chave.replace(' ', '-') + ('.png' if chave in {'refrigerante de guarana', 'suco de abacaxi', 'agua de coco', 'cha preto'} else '.jpg'),
            preco=float(item['preco']) if item.get('preco') is not None else None,
            categoria='Com álcool' if chave in {'gin', 'uisque de centeio rye'} else 'Sem álcool'))
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