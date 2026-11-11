"""Execute a prévia administrativa com: python previa_admin.py."""
import os
from secrets import token_hex
from flask import Flask, redirect, render_template, url_for, request, session
from catalogo_previa_admin import registrar, menu_publico, listar, bebidas_publicas
from endereco_evento import apresentar_endereco_evento, validar_endereco_evento

app = Flask(__name__)
app.config['TEMPLATES_AUTO_RELOAD'] = True
app.secret_key = token_hex(32)
registrar(app)

@app.context_processor
def dados_endereco_evento():
    endereco = session.get("endereco_evento_previa")
    return apresentar_endereco_evento(endereco) if endereco else {}

@app.post("/carrinho/endereco")
def selecionar_endereco():
    if not request.is_json:
        return {"erro": "Envie os dados do endereço em JSON."}, 415
    try:
        endereco = validar_endereco_evento(request.get_json(silent=True))
    except ValueError as erro:
        return {"erro": str(erro)}, 400
    session["endereco_evento_previa"] = endereco
    return apresentar_endereco_evento(endereco)

@app.get("/checkout")
def checkout():
    if not session.get("endereco_evento_previa"):
        return redirect(url_for("menu_admin_retorno", _anchor="endereco-evento"))
    return render_template("previas/checkout.html", carrinho_url=url_for("menu_admin_retorno"))

@app.get('/', endpoint='cliente.home')
def home():
    return render_template('home.html', servicos_na_previa=True)

@app.get('/admin')
def admin():
    return render_template('previas/admin.html')

@app.get('/menu', endpoint='cliente.menu')
def menu():
    return render_template('menu.html', categorias=menu_publico(), adicionais_menu=listar('cardapio'),
                           carrinho_url=url_for('menu_admin_retorno'), perfil_url=url_for('auth.login'))

@app.get('/bebidas')
def bebidas():
    return render_template('bebidas.html', bebidas=bebidas_publicas(), carrinho_url=url_for('menu_admin_retorno'))

@app.get('/carrinho', endpoint='menu_admin_retorno')
def carrinho():
    exemplo = request.args.get('exemplo', '')
    itens = []
    if exemplo in {'sem-bebidas', 'com-bar'}:
        bar = exemplo == 'com-bar'
        itens = [dict(numero=1, nome='Bar' if bar else 'Buffet para eventos',
                      descricao='Serviço ilustrativo para visualizar o carrinho.',
                      imagem='home-bebidas.jpg' if bar else 'home-buffet.jpg',
                      subtotal=350, inclui_bebidas=bar)]
    return render_template('carrinho.html', itens_carrinho=itens,
                           perfil_url=url_for('auth.login'), bebidas=bebidas_publicas(),
                           checkout_url=url_for('checkout'),
                           bebidas_url=url_for('bebidas', exemplo=exemplo))

@app.get('/previas/')
def indice():
    return redirect(url_for('admin'))

@app.get('/pedidos')
def pedidos():
    return render_template('previas/pedidos.html')

@app.get('/cozinha')
@app.get('/previas/cozinha.html')
def cozinha():
    return render_template('previas/cozinha.html')

@app.get('/estoque')
def estoque():
    return render_template('previas/estoque.html')

@app.get('/painel/funcionarios')
def funcionarios():
    return render_template('previas/funcionarios.html')

@app.get('/login', endpoint='auth.login')
def login():
    return render_template('login.html')

@app.get('/cadastro', endpoint='auth.cadastro')
def cadastro():
    return render_template('cadastro.html')

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=int(os.environ.get('PREVIEW_PORT', '8080')), debug=False)
