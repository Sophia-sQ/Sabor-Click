"""Inicialização do SQLAlchemy e carga inicial (seeds) do banco de dados."""

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import inspect, text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import DeclarativeBase

class Base(DeclarativeBase):
    """Classe base declarativa do SQLAlchemy para todos os modelos."""
    
    pass

db = SQLAlchemy(model_class=Base)

# ADMIN INICIAL CADASTRO
def criar_admin() -> None:
    """Adiciona o usuário administrador inicial à sessão do banco.

    Não realiza commit; a persistência é feita por quem chama a função.
    """
    
    from seeds import iniciar_admin
    admin = iniciar_admin()
    if admin is not None:
        db.session.add(admin)

# CRIAÇÃO DE CARGOS
def criar_cargos() -> None:
    """Adiciona os cargos (níveis de permissão) iniciais à sessão do banco.

    Não realiza commit; a persistência é feita por quem chama a função.
    """
    
    from seeds import iniciar_cargos
    cargos = iniciar_cargos()
    db.session.add_all(cargos)

# CRIAÇÃO DE ESTOQUE
def criar_estoque() -> None:
    """Adiciona à sessão os dados iniciais de estoque e seus vínculos.

    Inclui serviços, bancadas, cardápios, pratos, ingredientes, lotes, fichas
    técnicas (de pratos e de bebidas) e as associações serviço-bancada,
    serviço-cardápio e prato-cardápio. Não realiza commit.
    """
    
    from seeds import (
        iniciar_servicos,
        iniciar_bancadas,
        iniciar_cardapios,
        iniciar_bebidas,
        iniciar_pratos,
        iniciar_ingredientes,
        iniciar_lotes,
        iniciar_ficha_tecnica,
        iniciar_ficha_tecnica_bebida,
        iniciar_servico_bancada,
        iniciar_servico_cardapio,
        iniciar_prato_cardapio,
        iniciar_bebida_cardapio
    )
    # CRIAÇÃO DE SERVICOS
    servicos = iniciar_servicos()
    db.session.add_all(servicos)

    # CRIAÇÃO DE BANCADAS
    bancadas = iniciar_bancadas()
    db.session.add_all(bancadas)

    # CRIAÇÃO DE CARDAPIO
    cardapios = iniciar_cardapios()
    db.session.add_all(cardapios)

    db.session.add_all(iniciar_bebidas())

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
    
    bebida_cardapio= iniciar_bebida_cardapio()
    db.session.add_all(bebida_cardapio)

    # Inicializa o banco

def init_app(app) -> None:
    """Inicializa o banco de dados na aplicação Flask.

    Vincula o SQLAlchemy ao app, cria as tabelas inexistentes e executa a carga
    inicial de cargos, administrador e estoque dentro do contexto da aplicação.
    Em caso de erro no commit, desfaz a transação (rollback).

    Args:
        app (Flask): instância da aplicação Flask a ser configurada.
    """
    
    db.init_app(app)
    # Cria automaticamente todas as tabelas no arquivo do banco se elas não existirem
    with app.app_context():
        db.create_all()
        if db.engine.dialect.name == "sqlite":
            from triggers import criar_trigger_baixa_estoque
            criar_trigger_baixa_estoque()
        
    @app.cli.command("seed")
    def seed_command():
        """Popula o banco de dados com os dados iniciais."""
        
        from click import secho
        
        criar_cargos()
        criar_admin()
        criar_estoque()
        try:
            db.session.commit()
            secho("Success", fg="green", bold=True)
        except SQLAlchemyError as e:
            db.session.rollback()
            secho(f"FAIL {e}", fg="red", bold=True)        
