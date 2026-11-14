"""Serviço de upload de imagem de cardápio e sincronização do JSON de imagens.

Contrato deste módulo:

- Extensões aceitas: jpg, jpeg, png, webp (comparação case-insensitive).
- Tamanho máximo do arquivo: 5 MB (5 * 1024 * 1024 bytes).
- Slug: gerado a partir do nome do cardápio (utils.gerar_slug) e tornado único
  (utils.slug_unico) contra os slugs já presentes no JSON e contra os nomes de
  arquivo já existentes na pasta de destino, evitando sobrescrever imagens.
- Formato do campo 'arquivo' no JSON: 'static/images/menu/<slug>.<ext>', o mesmo
  padrão consumido pelas páginas do cliente (que removem o prefixo 'static/').
- Versão: hash SHA-256 do conteúdo do arquivo, truncado em 10 caracteres
  hexadecimais (mesmo tamanho dos 'versao' já existentes no JSON).

A imagem é gravada em static/images/menu/ e docs/imagens-menu.json é atualizado
de forma atômica (arquivo temporário + os.replace), preservando ensure_ascii=False
e indentação de 2 espaços.
"""

import hashlib
import json
import os
import tempfile

from flask import current_app
from werkzeug.utils import secure_filename

# Extensões de imagem aceitas no upload (comparadas em minúsculo).
EXTENSOES_PERMITIDAS = {"jpg", "jpeg", "png", "webp"}

# Tamanho máximo permitido para o arquivo enviado (5 MB).
TAMANHO_MAX_BYTES = 5 * 1024 * 1024

# Caminho relativo (dentro de static/) da pasta das imagens de cardápio.
PASTA_MENU_REL = "images/menu"


def _pasta_menu_abs() -> str:
    """Retorna o caminho absoluto da pasta static/images/menu/ da aplicação."""
    return os.path.join(current_app.root_path, "static", *PASTA_MENU_REL.split("/"))


def _caminho_json() -> str:
    """Retorna o caminho absoluto de docs/imagens-menu.json da aplicação."""
    return os.path.join(current_app.root_path, "docs", "imagens-menu.json")


def extensao_valida(nome_arquivo: str) -> bool:
    """Verifica se a extensão do arquivo enviado é permitida.

    Usa werkzeug.utils.secure_filename para sanitizar o nome antes de extrair
    a extensão e compara (case-insensitive) com EXTENSOES_PERMITIDAS.

    Args:
        nome_arquivo (str): nome original do arquivo enviado.

    Returns:
        bool: True se a extensão for aceita; False caso contrário.
    """
    seguro = secure_filename(nome_arquivo or "")
    if "." not in seguro:
        return False
    extensao = seguro.rsplit(".", 1)[1].lower()
    return extensao in EXTENSOES_PERMITIDAS


def salvar_imagem_cardapio(arquivo_storage, nome_cardapio: str) -> str:
    """Salva a imagem enviada e sincroniza docs/imagens-menu.json.

    Valida o arquivo (não vazio, extensão permitida, tamanho <= 5 MB), gera um
    slug único, grava os bytes em static/images/menu/<slug>.<ext> e insere/
    atualiza a entrada correspondente no JSON de imagens de forma atômica.

    Args:
        arquivo_storage: objeto FileStorage vindo de request.files.
        nome_cardapio (str): nome do cardápio, usado como base do slug e título.

    Returns:
        str: o slug gravado (para persistir em Cardapio.imagem_slug).

    Raises:
        ValueError: se o arquivo estiver vazio, tiver extensão não suportada ou
            exceder o tamanho máximo permitido.
    """
    slug, _ = _gravar_imagem(arquivo_storage, nome_cardapio, slug_atual=None)
    return slug


def atualizar_imagem_cardapio(arquivo_storage, nome_cardapio: str, slug_atual: str | None) -> str:
    """Grava uma nova imagem de cardápio mantendo o JSON consistente.

    Quando ``slug_atual`` é informado, a nova imagem sobrescreve a entrada e o
    arquivo daquele slug (mantendo o mesmo slug, apenas trocando a extensão caso
    o novo arquivo tenha outra). Quando ``slug_atual`` é None, comporta-se como
    uma criação (gera um slug novo e único). Reaproveita a mesma validação de
    salvar_imagem_cardapio (extensão, 5 MB) e a escrita atômica do JSON.

    Args:
        arquivo_storage: objeto FileStorage vindo de request.files.
        nome_cardapio (str): nome do cardápio (base do slug novo e título).
        slug_atual (str | None): slug já existente a ser atualizado, ou None.

    Returns:
        str: o slug gravado (igual a ``slug_atual`` quando este foi informado).

    Raises:
        ValueError: mesmas condições de salvar_imagem_cardapio.
    """
    slug, _ = _gravar_imagem(arquivo_storage, nome_cardapio, slug_atual=slug_atual)
    return slug


def remover_imagem_cardapio(slug: str) -> None:
    """Remove a entrada de ``slug`` de docs/imagens-menu.json (soft hide).

    Esconde a imagem dos clientes retirando a chave do JSON de forma atômica. É
    um no-op quando o slug não está presente e não falha se o arquivo de imagem
    não existir (mantém o foco em manter o JSON consistente). O arquivo físico é
    removido quando encontrado, mas sua ausência é tolerada.

    Args:
        slug (str): slug cujo registro deve ser removido do JSON.
    """
    if not slug:
        return

    caminho_json = _caminho_json()
    try:
        with open(caminho_json, encoding="utf-8") as arq:
            imagens = json.load(arq)
    except FileNotFoundError:
        return

    if slug not in imagens:
        return

    imagens.pop(slug, None)
    _escrever_json_atomico(caminho_json, imagens)

    # Remove o arquivo físico se existir (não obrigatório para esconder do cliente).
    pasta_destino = _pasta_menu_abs()
    if os.path.isdir(pasta_destino):
        for existente in os.listdir(pasta_destino):
            if os.path.splitext(existente)[0] == slug:
                try:
                    os.remove(os.path.join(pasta_destino, existente))
                except OSError:
                    pass


def _gravar_imagem(arquivo_storage, nome_cardapio: str, slug_atual: str | None) -> tuple[str, str]:
    """Valida e grava a imagem + entrada no JSON (lógica comum a criar/atualizar).

    Returns:
        tuple[str, str]: (slug gravado, nome do arquivo gravado).
    """
    if arquivo_storage is None or not getattr(arquivo_storage, "filename", ""):
        raise ValueError("Nenhum arquivo de imagem foi enviado.")

    nome_original = arquivo_storage.filename
    if not extensao_valida(nome_original):
        raise ValueError("Formato de imagem não suportado.")

    # Lê os bytes uma única vez e reutiliza (não depende de stream.seek).
    conteudo = arquivo_storage.read()
    if len(conteudo) > TAMANHO_MAX_BYTES:
        raise ValueError("A imagem excede o tamanho máximo de 5 MB.")

    extensao = secure_filename(nome_original).rsplit(".", 1)[1].lower()

    caminho_json = _caminho_json()
    with open(caminho_json, encoding="utf-8") as arq:
        imagens = json.load(arq)

    pasta_destino = _pasta_menu_abs()
    os.makedirs(pasta_destino, exist_ok=True)

    if slug_atual:
        # Atualização: mantém o mesmo slug; remove arquivos antigos do slug para
        # não deixar extensões órfãs quando a nova imagem tiver outro formato.
        slug = slug_atual
        for existente in os.listdir(pasta_destino):
            if os.path.splitext(existente)[0] == slug:
                try:
                    os.remove(os.path.join(pasta_destino, existente))
                except OSError:
                    pass
    else:
        # Criação: slug novo e único (contra o JSON e os arquivos existentes).
        slugs_existentes = set(imagens.keys())
        for existente in os.listdir(pasta_destino):
            slugs_existentes.add(os.path.splitext(existente)[0])

        from utils import gerar_slug, slug_unico

        base = gerar_slug(nome_cardapio) or "cardapio"
        slug = slug_unico(base, slugs_existentes)

    nome_arquivo = f"{slug}.{extensao}"
    caminho_imagem = os.path.join(pasta_destino, nome_arquivo)
    with open(caminho_imagem, "wb") as destino:
        destino.write(conteudo)

    versao = hashlib.sha256(conteudo).hexdigest()[:10]

    imagens[slug] = {
        "arquivo": f"static/images/menu/{nome_arquivo}",
        "titulo": nome_cardapio,
        "fonte": "",
        "autor": "Upload Sabor & Click",
        "licenca": "Uso próprio",
        "licenca_url": "",
        "original": "",
        "alteracoes": "Imagem enviada pelo admin via upload.",
        "versao": versao,
    }

    _escrever_json_atomico(caminho_json, imagens)

    return slug, nome_arquivo


def _escrever_json_atomico(caminho_json: str, imagens: dict) -> None:
    """Escreve o dicionário de imagens no JSON de forma atômica.

    Grava em um arquivo temporário no mesmo diretório e, em seguida, usa
    os.replace para substituir o arquivo final, preservando ensure_ascii=False,
    indentação de 2 espaços e a quebra de linha final.

    Args:
        caminho_json (str): caminho absoluto do docs/imagens-menu.json.
        imagens (dict): conteúdo completo a ser gravado.
    """
    diretorio = os.path.dirname(caminho_json)
    temporario = tempfile.NamedTemporaryFile(
        mode="w",
        encoding="utf-8",
        dir=diretorio,
        delete=False,
        suffix=".tmp",
    )
    try:
        with temporario as arq:
            json.dump(imagens, arq, ensure_ascii=False, indent=2)
            arq.write("\n")
        os.replace(temporario.name, caminho_json)
    except BaseException:
        if os.path.exists(temporario.name):
            os.remove(temporario.name)
        raise
