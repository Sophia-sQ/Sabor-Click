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

# CRIAÇÃO DE USUÁRIOS, PEDIDOS E DADOS RELACIONADOS
def criar_usuarios() -> None:
    """Adiciona à sessão os usuários iniciais (clientes e chefes).

    Depende dos cargos já existentes. Não realiza commit; a persistência é feita
    por quem chama a função.
    """

    from seeds import iniciar_usuarios
    db.session.add_all(iniciar_usuarios())

def criar_enderecos() -> None:
    """Adiciona à sessão os endereços dos clientes seed.

    Depende dos usuários já persistidos (FK id_usuario). Não realiza commit.
    """

    from seeds import iniciar_enderecos
    db.session.add_all(iniciar_enderecos())

def criar_pedidos() -> None:
    """Adiciona à sessão os pedidos seed e seus vínculos.

    Deve ser chamada após usuários e endereços estarem persistidos. Persiste os
    pedidos primeiro (flush) para que as associações cardápio-pedido e
    pedido-bebida consigam resolver as chaves estrangeiras. Não realiza commit.
    """

    from seeds import (
        iniciar_pedidos,
        iniciar_cardapio_pedido,
        iniciar_pedido_bebida,
    )

    pedidos = iniciar_pedidos()
    db.session.add_all(pedidos)
    # Garante que os pedidos recebam id antes de montar as associações.
    db.session.flush()

    db.session.add_all(iniciar_cardapio_pedido())
    db.session.add_all(iniciar_pedido_bebida())

def criar_logs_e_tokens() -> None:
    """Adiciona à sessão os logs de auditoria e tokens seed dos usuários.

    Depende dos usuários já persistidos (FK id_usuario). Não realiza commit.
    """

    from seeds import iniciar_logs, iniciar_tokens
    db.session.add_all(iniciar_logs())
    db.session.add_all(iniciar_tokens())

# VERIFICAÇÃO DA INICIALIZAÇÃO DO BANCO
def status_inicializacao() -> dict:
    """Verifica se os comandos 'seed' e 'dummy' já foram executados.

    A checagem é feita diretamente no banco (único estado que persiste entre as
    execuções dos comandos). Usa a existência de registros-sentinela:
      - 'seed': cria os cargos (nivel_permissao); se houver ao menos um, o seed
        já rodou.
      - 'dummy': cria os pedidos de simulação; se houver ao menos um, o dummy já
        rodou.

    Não realiza commit nem altera dados.

    Returns:
        dict: {"seed": bool, "dummy": bool} indicando se cada comando já foi
        inicializado.
    """
    from model.usuario_model import NivelPermissao
    from model.pedido_model import Pedido

    seed_ok = db.session.query(NivelPermissao.query.exists()).scalar()
    dummy_ok = db.session.query(Pedido.query.exists()).scalar()

    return {"seed": bool(seed_ok), "dummy": bool(dummy_ok)}


def init_app(app) -> None:
    """Inicializa o banco de dados na aplicação Flask.

    Vincula o SQLAlchemy ao app, cria as tabelas inexistentes e executa a carga
    inicial de cargos, administrador e estoque dentro do contexto da aplicação.
    Em caso de erro no commit, desfaz a transação (rollback).

    No modo empacotado (PyInstaller / apresentação), o banco é RECRIADO do zero
    a cada inicialização e re-populado automaticamente, garantindo um estado
    limpo e previsível em cada execução da demo.

    Args:
        app (Flask): instância da aplicação Flask a ser configurada.
    """

    from config import MODO_EMPACOTADO

    db.init_app(app)
    # Cria automaticamente todas as tabelas no arquivo do banco se elas não existirem
    with app.app_context():
        # Apresentação: começa sempre do mesmo estado, sem lixo de execuções anteriores.
        if MODO_EMPACOTADO:
            db.drop_all()
        try:
            db.create_all()
            criar_cargos()
            criar_admin()
            criar_estoque()
            db.session.commit()

            criar_usuarios()
            criar_enderecos()
            criar_pedidos()
            criar_logs_e_tokens()
            db.session.commit()
        except:
            db.session.rollback()
            
        if db.engine.dialect.name == "sqlite":
            from triggers import criar_trigger_baixa_estoque
            criar_trigger_baixa_estoque()