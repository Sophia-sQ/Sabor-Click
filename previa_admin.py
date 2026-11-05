"""Execute a prévia administrativa com: python previa_admin.py."""
import os
from flask import Flask, redirect, render_template, url_for
from catalogo_previa_admin import registrar, menu_publico, listar, bebidas_publicas

app = Flask(__name__)
app.config['TEMPLATES_AUTO_RELOAD'] = True
registrar(app)

@app.get('/', endpoint='cliente.home')
def home():
    return render_template('home.html')

@app.get('/admin')
def admin():
    return render_template('previas/admin.html')

@app.get('/menu', endpoint='cliente.menu')
def menu():
    return render_template('menu.html', categorias=menu_publico(), adicionais_menu=listar('cardapio'))

@app.get('/bebidas')
def bebidas():
    return render_template('bebidas.html', bebidas=bebidas_publicas(), carrinho_url=url_for('menu_admin_retorno'))

@app.get('/carrinho', endpoint='menu_admin_retorno')
def carrinho():
    return redirect(url_for('cliente.menu'))

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
