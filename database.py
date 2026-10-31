from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import DeclarativeBase

from seeds import *

#classe base: Não contém nada, pois utiliza o padrão do Python
class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)

# ADMIN INICIAL CADASTRO
def criar_admin():
<<<<<<< Updated upstream
=======
    from seeds import iniciar_admin
>>>>>>> Stashed changes
    admin = iniciar_admin()
    db.session.add(admin)

# CRIAÇÃO DE CARGOS
def criar_cargos():
<<<<<<< Updated upstream
=======
    from seeds import iniciar_cargos
>>>>>>> Stashed changes
    cargos = iniciar_cargos()
    db.session.add_all(cargos)

# CRIAÇÃO DE ESTOQUE
def criar_estoque():
<<<<<<< Updated upstream

=======
    from seeds import (
        iniciar_servicos,
        iniciar_bancadas,
        iniciar_cardapios,
        iniciar_pratos,
        iniciar_ingredientes,
        iniciar_lotes,
        iniciar_ficha_tecnica,
        iniciar_ficha_tecnica_bebida,
        iniciar_servico_bancada,
        iniciar_servico_cardapio,
        iniciar_prato_cardapio
    )
>>>>>>> Stashed changes
    # CRIAÇÃO DE SERVICOS
    servicos = iniciar_servicos()
    db.session.add_all(servicos)

<<<<<<< Updated upstream
    # CRIAÇÃO DE BANCADAS 
=======
    # CRIAÇÃO DE BANCADAS
>>>>>>> Stashed changes
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

    # Inicializa a ficha tecnica dos ingredientes
    fichas_tecnicas = iniciar_ficha_tecnica()
    db.session.add_all(fichas_tecnicas)

     # Inicializa a ficha tecnica das bebidas
    fichas_tecnicas_bebidas = iniciar_ficha_tecnica_bebida()
    db.session.add_all(fichas_tecnicas_bebidas)

    # Inicializa a associacao de servicoBancada
    servico_bancada = iniciar_servico_bancada()
    db.session.add_all(servico_bancada)

    # Inicializa a associacao de servicoCardapio
    servico_cardapio= iniciar_servico_cardapio()
    db.session.add_all(servico_cardapio)

    # Inicializa a associacao de pratocardapio
    prato_cardapio= iniciar_prato_cardapio()
    db.session.add_all(prato_cardapio)
<<<<<<< Updated upstream
    
    
=======


>>>>>>> Stashed changes

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
<<<<<<< Updated upstream
        except:
=======
        except SQLAlchemyError:
>>>>>>> Stashed changes
            db.session.rollback()

