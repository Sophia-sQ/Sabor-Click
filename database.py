from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase

from model.cargos import Cargo
from model.usuario_model import Usuario, NivelPermissao, criar_usuario

from seeds import *

from os import environ

#classe base: Não contém nada, pois utiliza o padrão do Python
class Base(DeclarativeBase):
    pass


db = SQLAlchemy(model_class=Base)

# ADMIN INICIAL CADASTRO
def criar_admin():
    # verifica se ja existe admin
    #email_admin = environ.get("ADMIN_EMAIL")
    admin_existente = Usuario.query.filter_by(id_permissao=Cargo.ADMIN.value).first()

    if not admin_existente:
        criar_usuario(
            cpf="00000000000",
            nome="Admin",
            email=environ.get("ADMIN_EMAIL"),
            senha=environ.get("ADMIN_PASSWORD"),
            id_permissao=Cargo.ADMIN.value
        )
        #print(f"Admin inicial criado com sucesso! (ID: {id_admin})")
    #else:
    #    print("Admin inicial já existe.")

    #admin = criar_usuario(
    #cpf="00000000000",
    #nome="Admin",
    #email="emailexemplo@gmail.com",
    #senha="senha-super-segura123",
    #id_permissao=Cargo.ADMIN
    #)        

# CRIAÇÃO DE CARGOS
def criar_cargos():
    cargos = iniciar_cargos()
    db.session.add_all(cargos)

# CRIAÇÃO DE ESTOQUE
def criar_estoque():

    # CRIAÇÃO DE SERVICOS
    servicos = iniciar_servicos()
    db.session.add_all(servicos)

    # CRIAÇÃO DE BANCADAS 
    bancadas = iniciar_bancadas()
    db.session.add_all(bancadas)

    # CRIAÇÃO DE CARDAPIO
    cardapios = iniciar_cardapios()
    db.session.add_all(cardapios)

    # CRIAÇÃO DE PRATOS
    pratos = iniciar_pratos()
    db.session.add_all(pratos)

    # CRIAÇÃO DE INGREDIENTES
    ingredientes = iniciar_ingredientes()
    db.session.add_all(ingredientes)

    # CRIAÇÃO DE LOTES
    lotes = iniciar_lotes()
    db.session.add_all(lotes)
    
    fichas_tecnicas = iniciar_ficha_tecnica()
    db.session.add_all(fichas_tecnicas)

    # Inicializa o banco

def init_app(app):
    db.init_app(app)
    
    # Cria automaticamente todas as tabelas no arquivo do banco se elas não existirem
    with app.app_context():
        db.create_all()
        criar_cargos()
        criar_admin()
        criar_estoque()
        try:
            db.session.commit()
        except:
            db.session.rollback()

