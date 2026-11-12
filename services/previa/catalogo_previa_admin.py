"""Gerenciamento persistido do catálogo da prévia local."""
import hashlib
import json
from pathlib import Path
from decimal import Decimal, InvalidOperation
from threading import RLock
from urllib.parse import urlsplit
from uuid import uuid4
from flask import abort, request, render_template, redirect, url_for
from jinja2 import Environment, FileSystemLoader

RAIZ = Path(__file__).resolve().parents[2]
ARQUIVO = RAIZ / 'instance' / 'catalogo-previa.json'
UPLOADS = RAIZ / 'static' / 'images' / 'catalogo'
LOCK = RLock()
ENV = Environment(loader=FileSystemLoader(str(RAIZ / 'templates')))
SERVICOS_CATALOGO = {
    'buffet': ('Buffet para eventos', 'quentes'),
    'chef-em-casa': ('Chef em casa', 'quentes'),
    'mesa-de-salgados': ('Salgados para eventos', 'salgados'),
    'bar': ('Bebidas', 'bebidas'),
}

def ler():
    dados = json.loads(ARQUIVO.read_text(encoding='utf-8')) if ARQUIVO.exists() else {}
    for tipo in ('cardapio', 'bebidas'):
        dados.setdefault(tipo, [])
    dados.setdefault('alteracoes', {'cardapio': {}, 'bebidas': {}})
    dados.setdefault('removidos', {'cardapio': [], 'bebidas': []})
    return dados

def salvar(dados):
    ARQUIVO.parent.mkdir(exist_ok=True)
    temporario = ARQUIVO.with_suffix('.tmp')
    temporario.write_text(json.dumps(dados, ensure_ascii=False, indent=2), encoding='utf-8')
    temporario.replace(ARQUIVO)

def base(tipo):
    if tipo == 'bebidas':
        from services.bebidas_data import catalogo_previa
        return catalogo_previa()
    from services.menu_data import categorias
    fotos = ENV.get_template('componentes/fotos_menu.html').module.fotos_menu
    precos = ENV.get_template('componentes/precos_menu.html').module.precos_menu
    resultado = []
    for categoria in categorias:
        for nome, descricao, _, _ in categoria['itens']:
            foto = fotos[nome]
            imagem = 'images/menu/' + foto['imagem'] + '.' + foto.get('extensao', 'jpg')
            resultado.append(dict(id='menu-'+hashlib.sha256(nome.encode()).hexdigest()[:16], nome=nome, descricao=descricao, categoria=categoria['id'], preco=precos.get(nome, 0)/100, imagem=imagem))
    return resultado

def listar(tipo):
    dados = ler()
    itens = [dict(i, **dados['alteracoes'][tipo].get(i['id'], {})) for i in base(tipo)+dados[tipo] if i['id'] not in dados['removidos'][tipo]]
    if tipo == 'cardapio':
        for item in itens:
            item.setdefault('servicos', [
                slug for slug, (_, categoria) in SERVICOS_CATALOGO.items() if categoria == item['categoria']
            ])
    return itens

def bebidas_publicas():
    return listar('bebidas')

def menu_publico():
    """Monta as seções do menu da prévia no mesmo formato que templates/menu.html espera.

    O template (reescrito para o menu público do banco) itera dicts com
    'id_cardapio', 'nome', 'descricao', 'preco' (centavos), 'imagem' (relativo a
    static/) e 'versao'. A prévia continua lendo do catálogo local (JSON +
    base()), convertendo o preço de reais para centavos e reaproveitando a
    imagem relativa que já é gerada em base()/CMS.
    """
    from services.menu_data import categorias
    itens_por_categoria = {}
    for item in listar('cardapio'):
        itens_por_categoria.setdefault(item['categoria'], []).append({
            'id_cardapio': item['id'],
            'nome': item['nome'],
            'descricao': item['descricao'],
            'preco': round(float(item.get('preco') or 0) * 100),  # reais -> centavos
            'imagem': item.get('imagem'),
            'versao': None,
        })
    return [dict(c, itens=itens_por_categoria.get(c['id'], [])) for c in categorias]

def imagem_url(imagem):
    return imagem if imagem.startswith(('https://','http://')) else url_for('static', filename=imagem)

def receber_imagem(anterior):
    arquivo = request.files.get('imagem_arquivo')
    link = request.form.get('imagem_link', '').strip()
    if arquivo and arquivo.filename and link:
        raise ValueError('Escolha um arquivo ou um link, em vez dos dois.')
    if arquivo and arquivo.filename:
        conteudo = arquivo.read(5 * 1024 * 1024 + 1)
        if len(conteudo) > 5 * 1024 * 1024:
            raise ValueError('A imagem deve ter no máximo 5 MB.')
        if conteudo.startswith(b'\x89PNG\r\n\x1a\n'):
            extensao = 'png'
        elif conteudo.startswith(b'\xff\xd8\xff'):
            extensao = 'jpg'
        elif conteudo.startswith(b'RIFF') and conteudo[8:12] == b'WEBP':
            extensao = 'webp'
        else:
            raise ValueError('Envie uma imagem PNG, JPG ou WebP válida.')
        UPLOADS.mkdir(parents=True, exist_ok=True)
        nome = uuid4().hex + '.' + extensao
        (UPLOADS / nome).write_bytes(conteudo)
        return 'images/catalogo/' + nome
    if link:
        try:
            partes = urlsplit(link)
            if partes.scheme not in {'http','https'} or not partes.hostname or partes.username or partes.password or len(link)>2000:
                raise ValueError()
        except ValueError:
            raise ValueError('Informe um link de imagem válido, começando com https:// ou http://.')
        return link
    return anterior

def registrar(app):
    app.jinja_env.globals['imagem_catalogo_url'] = imagem_url
    app.config['MAX_CONTENT_LENGTH'] = 6 * 1024 * 1024

    @app.route('/painel/<tipo>', methods=['GET', 'POST'])
    def catalogo_admin(tipo):
        if tipo not in {'cardapio','bebidas'}:
            abort(404)
        from services.menu_data import categorias
        opcoes = [(c['id'],c['nome']) for c in categorias] if tipo=='cardapio' else [('Sem álcool','Sem álcool'),('Com álcool','Com álcool')]
        itens = listar(tipo)
        identificador = request.form.get('id', '') if request.method=='POST' else request.args.get('editar', '')
        atual = next((i for i in itens if i['id']==identificador), None)
        if identificador and not atual:
            abort(404)
        erro = None
        servicos = request.form.getlist('servicos')
        if request.method=='POST':
            origem=request.headers.get('Origin')
            if origem and origem.rstrip('/')!=request.host_url.rstrip('/'):
                abort(403)
            acao = request.form.get('acao', 'salvar')
            if acao == 'remover':
                if not atual:
                    abort(400)
                with LOCK:
                    dados=ler()
                    dados['removidos'][tipo].append(atual['id'])
                    salvar(dados)
                return redirect(url_for('catalogo_admin',tipo=tipo,gerenciar='1',salvo='removido'))
            try:
                nome=request.form.get('nome','').strip()
                descricao=request.form.get('descricao','').strip()
                categoria=request.form.get('categoria','')
                try:
                    preco=Decimal(request.form.get('preco','').replace(',','.'))
                    if not preco.is_finite() or preco<0 or preco>1000000:
                        raise InvalidOperation()
                except InvalidOperation:
                    raise ValueError('Informe um preço válido, igual ou maior que zero.')
                if not nome or len(nome)>100 or not descricao or len(descricao)>1000 or categoria not in dict(opcoes):
                    raise ValueError('Preencha nome, categoria e descrição.')
                registro=dict(id=atual['id'] if atual else 'local-'+uuid4().hex,nome=nome,descricao=descricao,categoria=categoria,preco=float(preco.quantize(Decimal('.01'))))
                if tipo == 'cardapio':
                    if not servicos or any(slug not in SERVICOS_CATALOGO for slug in servicos):
                        raise ValueError('Selecione pelo menos um serviço para o cardápio.')
                    registro['servicos'] = list(dict.fromkeys(servicos))
                if tipo=='bebidas':
                    try:
                        volume=int(request.form.get('volume_ml','0'))
                        if not 1<=volume<=100000:
                            raise ValueError()
                    except ValueError:
                        raise ValueError('Informe um volume de 1 a 100.000 ml.')
                    registro['volume_ml']=volume
                with LOCK:
                    if any(i['nome'].casefold()==nome.casefold() and i['id']!=registro['id'] for i in listar(tipo)):
                        raise ValueError('Já existe uma opção com esse nome.')
                    padrao='images/home-bebidas.jpg' if tipo=='bebidas' else 'images/menu-quentes.png'
                    registro['imagem']=receber_imagem(atual['imagem'] if atual else padrao)
                    dados=ler()
                    if atual:
                        dados['alteracoes'][tipo][registro['id']]=registro
                    else:
                        dados[tipo].append(registro)
                    salvar(dados)
                return redirect(url_for('catalogo_admin',tipo=tipo,salvo='editado' if atual else 'adicionado'))
            except ValueError as ex:
                erro=str(ex)
        valores=dict(atual or {})
        if request.method=='POST':
            valores.update(request.form)
            valores['servicos'] = [slug for slug in servicos if slug in SERVICOS_CATALOGO]
        return render_template('previas/catalogo_admin.html',tipo=tipo,itens=itens,opcoes=opcoes,erro=erro,atual=atual,valores=valores,servicos_catalogo=SERVICOS_CATALOGO,salvo=request.args.get('salvo'),gerenciar=request.args.get('gerenciar')=='1')
