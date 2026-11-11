"""Formatação do catálogo avulso, separado dos coquetéis do Bar."""
from pathlib import Path
import ast
import sqlite3
import unicodedata


def normalizar(nome):
    return ''.join(c for c in unicodedata.normalize('NFD', nome.replace('_', ' ')) if unicodedata.category(c) != 'Mn').lower().strip()


def nomes_avulsos():
    # Lê os dados sem importar seeds.py e sua inicialização do banco.
    arvore = ast.parse((Path(__file__).parent / 'seeds.py').read_text(encoding='utf-8-sig'))
    for node in arvore.body:
        if isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and t.id == 'lista_bebida' for t in node.targets):
            nomes = []
            for item in node.value.elts:
                # A lista atual tem uma vírgula ausente entre o uísque e o primeiro drink.
                valor = item.func if isinstance(item, ast.Call) else item
                dados = ast.literal_eval(valor)
                if len(dados) != 3:
                    break
                nomes.append(dados[0])
            return nomes
    return []


def volumes_avulsos():
    """Volumes por porção da ficha cadastrada no projeto, em mililitros."""
    arvore = ast.parse((Path(__file__).parent / 'seeds.py').read_text(encoding='utf-8-sig'))
    for node in arvore.body:
        if isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and t.id == 'ficha_bebidas' for t in node.targets):
            volumes = {}
            for item in node.value.elts:
                if not isinstance(item, ast.Tuple):
                    break
                nome, ingrediente, quantidade = ast.literal_eval(item)
                if normalizar(nome) != normalizar(ingrediente):
                    break
                volumes[normalizar(nome)] = quantidade
            return volumes
    return {}


def formatar_bebidas(registros):
    permitidos = {normalizar(n) for n in nomes_avulsos()}
    volumes = volumes_avulsos()
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


def catalogo_previa():
    caminho = Path(__file__).parent / 'instance' / 'banco.db'
    if caminho.exists():
        with sqlite3.connect(caminho.as_uri() + '?mode=ro', uri=True) as conexao:
            tabela = conexao.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name='bebida'").fetchone()
            if tabela:
                rows = conexao.execute('SELECT id_bebida, nome, descricao, valor_unitario FROM bebida ORDER BY nome').fetchall()
                return formatar_bebidas([dict(id=r[0], nome=r[1], descricao=r[2], preco=r[3]) for r in rows])
    # Sem tabela local: os nomes vêm do cadastro, sem adivinhar a unidade dos preços.
    return formatar_bebidas([dict(id='previa-' + normalizar(n).replace(' ', '-'), nome=n, preco=None) for n in nomes_avulsos()])
