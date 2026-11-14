"""Serviço de upload de imagem de prato e sincronização do JSON de imagens.

Espelha services/imagem_bebida.py para o catálogo de pratos, reaproveitando
a validação (extensão {jpg, jpeg, png, webp}, 5 MB), o gerador de slug único
(utils.gerar_slug/slug_unico) e a escrita atômica do JSON (imagem_cardapio.
_escrever_json_atomico). Mantém o contrato DRY: só muda a pasta de destino
(static/images/pratos) e o arquivo de registro (docs/imagens-pratos.json).

Diferença em relação ao cardápio: docs/imagens-pratos.json pode não existir no
primeiro upload; neste caso ele é criado como um objeto vazio ({}). O campo
'arquivo' no JSON segue o mesmo padrão consumido pelas páginas do cliente:
'static/images/pratos/<slug>.<ext>' (o cliente remove o prefixo 'static/').
"""

import hashlib
import json
import os

from flask import current_app

from werkzeug.utils import secure_filename

from services.imagem_cardapio import (
    TAMANHO_MAX_BYTES,
    _escrever_json_atomico,
    extensao_valida,
)

# Caminho relativo (dentro de static/) da pasta das imagens de prato.
PASTA_PRATOS_REL = "images/pratos"


def _pasta_pratos_abs() -> str:
    """Retorna o caminho absoluto da pasta static/images/pratos/ da aplicação."""
    return os.path.join(current_app.root_path, "static", *PASTA_PRATOS_REL.split("/"))


def _caminho_json() -> str:
    """Retorna o caminho absoluto de docs/imagens-pratos.json da aplicação."""
    return os.path.join(current_app.root_path, "docs", "imagens-pratos.json")


def _carregar_json() -> dict:
    """Carrega docs/imagens-pratos.json, tolerando ausência (retorna {})."""
    caminho_json = _caminho_json()
    try:
        with open(caminho_json, encoding="utf-8") as arq:
            return json.load(arq)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def salvar_imagem_prato(arquivo_storage, nome_prato: str) -> str:
    """Salva a imagem enviada e sincroniza docs/imagens-pratos.json.

    Args:
        arquivo_storage: objeto FileStorage vindo de request.files.
        nome_prato (str): nome do prato (base do slug e título).

    Returns:
        str: o slug gravado (para persistir em Prato.imagem_slug).

    Raises:
        ValueError: se o arquivo estiver vazio, tiver extensão não suportada ou
            exceder o tamanho máximo permitido.
    """
    return _gravar_imagem(arquivo_storage, nome_prato, slug_atual=None)


def atualizar_imagem_prato(arquivo_storage, nome_prato: str, slug_atual: str | None) -> str:
    """Grava uma nova imagem de prato mantendo o JSON consistente.

    Quando ``slug_atual`` é informado, sobrescreve a entrada/arquivo daquele
    slug; quando None, cria um slug novo e único. Mesma validação do upload.

    Args:
        arquivo_storage: objeto FileStorage vindo de request.files.
        nome_prato (str): nome do prato (base do slug novo e título).
        slug_atual (str | None): slug existente a atualizar, ou None.

    Returns:
        str: o slug gravado (igual a ``slug_atual`` quando informado).
    """
    return _gravar_imagem(arquivo_storage, nome_prato, slug_atual=slug_atual)


def remover_imagem_prato(slug: str) -> None:
    """Remove a entrada de ``slug`` de docs/imagens-pratos.json (soft hide).

    No-op quando o slug está ausente; não falha se o arquivo físico não existir.

    Args:
        slug (str): slug cujo registro deve ser removido do JSON.
    """
    if not slug:
        return

    imagens = _carregar_json()
    if slug not in imagens:
        return

    imagens.pop(slug, None)
    _escrever_json_atomico(_caminho_json(), imagens)

    pasta_destino = _pasta_pratos_abs()
    if os.path.isdir(pasta_destino):
        for existente in os.listdir(pasta_destino):
            if os.path.splitext(existente)[0] == slug:
                try:
                    os.remove(os.path.join(pasta_destino, existente))
                except OSError:
                    pass


def _gravar_imagem(arquivo_storage, nome_prato: str, slug_atual: str | None) -> str:
    """Valida e grava a imagem + entrada no JSON (lógica comum a criar/atualizar)."""
    if arquivo_storage is None or not getattr(arquivo_storage, "filename", ""):
        raise ValueError("Nenhum arquivo de imagem foi enviado.")

    nome_original = arquivo_storage.filename
    if not extensao_valida(nome_original):
        raise ValueError("Formato de imagem não suportado.")

    conteudo = arquivo_storage.read()
    if len(conteudo) > TAMANHO_MAX_BYTES:
        raise ValueError("A imagem excede o tamanho máximo de 5 MB.")

    extensao = secure_filename(nome_original).rsplit(".", 1)[1].lower()

    imagens = _carregar_json()

    pasta_destino = _pasta_pratos_abs()
    os.makedirs(pasta_destino, exist_ok=True)

    if slug_atual:
        slug = slug_atual
        for existente in os.listdir(pasta_destino):
            if os.path.splitext(existente)[0] == slug:
                try:
                    os.remove(os.path.join(pasta_destino, existente))
                except OSError:
                    pass
    else:
        slugs_existentes = set(imagens.keys())
        for existente in os.listdir(pasta_destino):
            slugs_existentes.add(os.path.splitext(existente)[0])

        from utils import gerar_slug, slug_unico

        base = gerar_slug(nome_prato) or "prato"
        slug = slug_unico(base, slugs_existentes)

    nome_arquivo = f"{slug}.{extensao}"
    caminho_imagem = os.path.join(pasta_destino, nome_arquivo)
    with open(caminho_imagem, "wb") as destino:
        destino.write(conteudo)

    versao = hashlib.sha256(conteudo).hexdigest()[:10]

    imagens[slug] = {
        "arquivo": f"static/images/pratos/{nome_arquivo}",
        "titulo": nome_prato,
        "fonte": "",
        "autor": "Upload Sabor & Click",
        "licenca": "Uso próprio",
        "licenca_url": "",
        "original": "",
        "alteracoes": "Imagem enviada pelo admin via upload.",
        "versao": versao,
    }

    _escrever_json_atomico(_caminho_json(), imagens)

    return slug
