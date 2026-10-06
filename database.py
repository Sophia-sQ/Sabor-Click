from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from model.usuario_model import criar_usuario
from model.cargos import Cargo
from model.usuario_model import Usuario, NivelPermissao, criar_usuario

from os import environ

#classe base: Não contém nada, pois utiliza o padrão do Python
class Base(DeclarativeBase):
    pass


db = SQLAlchemy(model_class=Base)



# ADMIN INICIAL CADASTRO
def criar_admin():
    # verifica se ja existe admin
    email_admin = environ.get("ADMIN_EMAIL")
    admin_existente= Usuario.query.filter_by(email=email_admin).first()

    if not admin_existente:
        id_admin = criar_usuario(
            cpf="00000000000",
            nome="Admin",
            email=environ.get("ADMIN_EMAIL"),
            senha=environ.get("ADMIN_PASSWORD"),
            id_permissao=Cargo.ADMIN._value_
        )
        print(f"Admin inicial criado com sucesso! (ID: {id_admin})")
    else:
        print("Admin inicial já existe.")

    #admin = criar_usuario(
    #cpf="00000000000",
    #nome="Admin",
    #email="emailexemplo@gmail.com",
    #senha="senha-super-segura123",
    #id_permissao=Cargo.ADMIN
    #)        

# Inicializa o banco
def init_app(app):
    db.init_app(app)
    
    # Cria automaticamente todas as tabelas no arquivo do banco se elas não existirem
    with app.app_context():
        db.create_all()
        #TODO: criar cargos
        criar_admin()

