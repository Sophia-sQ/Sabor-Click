# Contém as tabelas : Bancada, serviço e cardápio

from database import db
from model.servico_model import registrar_log
from slugify import slugify

class Bancada(db.Model):
    __tablename__ = "bancada"

    id_bancada = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nome = db.Column(db.String(60), nullable=False)
    descricao = db.Column(db.Text, nullable=False)

class Servico(db.Model):
    __tablename__ = "servico"

    id_servico = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nome = db.Column(db.String(60), unique=True, nullable=False)
    descricao = db.Column(db.Text, nullable=False)
    slug = db.Column(db.String(120), nullable=False, unique=True)

    # É executada cada vez que a classe é instanciada
    def __init__(self, **kwargs): # **kwargs recebe um dicionario (os dados da propria instancia)
        if kwargs.get("nome"):
            kwargs["slug"] = kwargs.get("slug") or slugify(kwargs["nome"])

        super().__init__(**kwargs)

# Tabela de associação entre bancada e o serviço 
class ServicoBancada(db.Model):
    __tablename__ = "servico_bancada"

    id_servico = db.Column(db.Integer, db.ForeignKey("servico.id_servico"), primary_key=True)
    id_bancada = db.Column(db.Integer, db.ForeignKey("bancada.id_bancada"), primary_key=True)

class Cardapio(db.Model):
    __tablename__ = "cardapio"

    id_cardapio = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nome = db.Column(db.String(60), nullable=False)
    descricao = db.Column(db.Text, nullable=False)
    preco_base = db.Column(db.Numeric(10, 2), nullable=False)

    __table_args__ = (
        db.CheckConstraint("preco_base >= 0", name="ck_cardapio_preco"),
    )
# Tabela de associação entre cardápio e serviço, pois existem serviços com o mesmo cardápio 

class ServicoCardapio(db.Model):
    __tablename__ = "servico_cardapio"

    id_servico = db.Column(db.Integer, db.ForeignKey("servico.id_servico"), primary_key=True)
    id_cardapio = db.Column(db.Integer, db.ForeignKey("cardapio.id_cardapio"), primary_key=True)



"""==================CRUD BANCADA============="""

def criar_bancada(nome: str, descricao: str):
    """Cria uma nova bancada"""
    nova_bancada = Bancada(nome=nome, descricao=descricao)
    db.session.add(nova_bancada)
    db.session.commit()
    registrar_log("CRIACAO BANCADA", "Usuário criou nova bancada")
    return nova_bancada.id_bancada
    

def buscar_bancada_por_id(id_bancada):
    """Busca bancada  pelo id"""
    bancada = db.session.get(Bancada, id_bancada)
    if bancada:
        return bancada
    return None

def listar_bancadas():
    """Lista todas bancadas"""
    bancadas = db.session.execute(db.select(Bancada)).scalars().all()
    if bancadas:
        return bancadas
    return None

def atualizar_bancada(id_bancada, id_usuario:int, nome=None, descricao=None):
    """Atualiza os dados da bancada """
    bancada = db.session.get(Bancada, id_bancada)
    if not bancada:
        return False
    if nome:
        bancada.nome = nome
    if descricao:
        bancada.descricao = descricao
    db.session.commit()
    registrar_log(id_usuario,"ATUALIZACAO BANCADA", "Usuário atualizou bancada")

    return True

def deletar_bancada(id_bancada, id_usuario: int):
    """Deleta bancada"""
    bancada = db.session.get(Bancada, id_bancada)
    if not bancada:
        return False
    db.session.delete(bancada)
    db.session.commit()
    registrar_log(id_usuario,"DELETAR BANCADA", "Usuário deletou bancada")

    return True

"""==============CRUD SERVICO======"""

def criar_servico(nome, descricao):
    """Cria serviço"""
    novo_servico = Servico(nome=nome, descricao=descricao)
    db.session.add(novo_servico)
    db.session.commit()
    registrar_log("CRIACAO SERVICO", "Usuário criou novo servico")

    return novo_servico.id_servico

def buscar_servico_por_id(id_servico):
    """Busca por id."""
    
    servico = db.session.get(Servico, id_servico)
    if servico:
        return servico
    return None

def buscar_servico_por_slug(slug_servico:str) -> (Servico | None):
    """Busca um servico pelo seu slug e retorna o servico, se existir."""
        
    servico = db.session.execute(
        db.select(servico).where(Servico.slug == slug_servico)
    ).scalar_one_or_none()
    
    if servico:
        return servico
    return None

def listar_servicos():
    """Lista servico"""
    servicos = db.session.execute(db.select(Servico)).scalars().all()
    if servicos:
        return servicos
    return None

def atualizar_servico(id_servico, id_usuario:int, nome=None, descricao=None):
    """Atualiza servico"""
    servico = db.session.get(Servico, id_servico)
    if not servico:
        return False
    if nome:
        servico.nome = nome
    if descricao:
        servico.descricao = descricao
    db.session.commit()
    registrar_log(id_usuario,"ATUALIZACAO SERVICO", "Usuário atulizou o servico")

    return True

def deletar_servico(id_servico, id_usuario:int):
    """Deleta servico"""
    servico = db.session.get(Servico, id_servico)
    if not servico:
        return False
    db.session.delete(servico)
    db.session.commit()
    registrar_log(id_usuario,"DELETAR SERVICO", "Usuário deletou servico")

    return True



"""===============CRUD CARDÁPIO========="""


def criar_cardapio(nome, descricao, preco_base):
    '''cria cardapio'''
    novo_cardapio = Cardapio(nome=nome, descricao=descricao, preco_base=preco_base)
    db.session.add(novo_cardapio)
    db.session.commit()
    registrar_log("CRIACAO CARDAPIO", "Usuário criou novo cardapio")

    return novo_cardapio.id_cardapio

def buscar_cardapio_por_id(id_cardapio):
    '''busca cardapio'''
    cardapio = db.session.get(Cardapio, id_cardapio)
    if cardapio:
        return cardapio
    return None

def listar_cardapios():
    '''lista cardapio'''
    cardapios = db.session.execute(db.select(Cardapio)).scalars().all()
    if cardapios:
        return cardapios
    return None

def atualizar_cardapio(id_cardapio, id_usuario: int, nome=None, descricao=None, preco_base=None):
    '''atualiza cardapio'''
    cardapio = db.session.get(Cardapio, id_cardapio)
    if not cardapio:
        return False
    if nome:
        cardapio.nome = nome
    if descricao:
        cardapio.descricao = descricao
    if preco_base is not None:
        cardapio.preco_base = preco_base
    db.session.commit()
    registrar_log(id_usuario,"ATUALIZACAO CARDAPIO", "Usuário atualizou cardapio")

    return True

def deletar_cardapio(id_cardapio, id_usuario: int):
    """Deleta cardapio"""
    cardapio = db.session.get(Cardapio, id_cardapio)
    if not cardapio:
        return False
    db.session.delete(cardapio)
    db.session.commit()
    registrar_log(id_usuario,"DELETAR CARDAPIO", "Usuário deletou cardapio")

    return True



"""============= CRUD - SERVIÇO / BANCADA (Tabela de Associação) ============"""

def associar_servico_bancada(id_servico, id_bancada, id_usuario: int):
    """Associa a bancada aos serviços. Se bancada e serviço já forem
    associados, retorna False, do contrário, retorna True."""
    
    associacao = db.session.get(ServicoBancada, (id_servico, id_bancada))
    if associacao:
        return False
    nova_associacao = ServicoBancada(id_servico=id_servico, id_bancada=id_bancada)
    db.session.add(nova_associacao)
    db.session.commit()
    registrar_log(id_usuario,"ASSOCIACAO SERVICO_BANCADA", "Usuário associou uma bancada a um servico")

    return True

def desassociar_servico_bancada(id_servico: int, id_bancada: int, id_usuario: int) -> bool:
    """desassocia a bancada dos serviços. Se bancada e serviço já não forem
        associados, retorna False, do contrário, retorna True."""
        
    associacao = db.session.get(ServicoBancada, (id_servico, id_bancada))
    if not associacao:
        return False
    db.session.delete(associacao)
    db.session.commit()
    registrar_log(id_usuario,"DESASSOCIACAO SERVICO_BANCADA", "Usuário desassociou uma bancada a um servico")

    return True

def listar_bancadas_do_servico(id_servico: int) -> (list | None):
    """Lista as bancadas que o serviço possui."""
    
    bancadas = db.session.execute(
        db.select(Bancada)
        .join(ServicoBancada, Bancada.id_bancada == ServicoBancada.id_bancada)
        .where(ServicoBancada.id_servico == id_servico)
    ).scalars().all()
    if bancadas:
        return bancadas
    return None


"""=====CRUD SERVIÇO / CARDÁPIO (Tabela de Associação)======"""

def associar_servico_cardapio(id_servico, id_cardapio, descricao=None, id_usuario= int) -> bool:
    """Associa o cardapio aos serviços. Se cardápio e serviço já estiverem
    associados, retorna False, do contrário, retorna True."""
    
    associacao = db.session.get(ServicoCardapio, (id_servico, id_cardapio))
    if associacao:
        return False
    nova_associacao = ServicoCardapio(id_servico=id_servico, id_cardapio=id_cardapio,descricao=descricao)
    db.session.add(nova_associacao)
    db.session.commit()
    registrar_log(id_usuario,"ASSOCIACAO SERVICO_CARDAPIO", "Usuário associou um cardapio a um servico")

    return True

def desassociar_servico_cardapio(id_servico, id_cardapio, id_usuario: int):
    """desassocia o cardapio aos serviços. Se cardápio e serviço já não forem
    associados, retorna False, do contrário, retorna True."""
    
    associacao = db.session.get(ServicoCardapio, (id_servico, id_cardapio))
    if not associacao:
        return False
    db.session.delete(associacao)
    db.session.commit()
    registrar_log(id_usuario,"DESASSOCIACAO SERVICO_CARDAPIO", "Usuário desassociou um cardapio a um servico")

    return True

def listar_cardapios_do_servico(id_servico: int) -> (list):
    """Retorna todos os cardápios associados a um servico."""
    
    cardapios = db.session.execute(
            db.select(ServicoCardapio).where(
        ServicoCardapio.id_servico == id_servico
        )).scalars().all()
    
    if cardapios:
        return cardapios
    return None

