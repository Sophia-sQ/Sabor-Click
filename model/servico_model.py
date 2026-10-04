# Contém as tabelas : Bancada, serviço e cardápio

from database import db
from model.servico_model import registrar_log

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
    descricao = db.Column(db.Text, nullable=True)  



"""==================CRUD BANCADA============="""

def criar_bancada(nome: str, descricao: str, id_usuario: int):
    """Cria uma nova bancada"""
    nova_bancada = Bancada(nome=nome, descricao=descricao)
    db.session.add(nova_bancada)
    db.session.commit()
    registrar_log(id_usuario,"CRIACAO BANCADA", "Usuário criou nova bancada")
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

def criar_servico(nome, descricao, id_usuario: int):
    """Cria serviço"""
    novo_servico = Servico(nome=nome, descricao=descricao)
    db.session.add(novo_servico)
    db.session.commit()
    registrar_log(id_usuario,"CRIACAO SERVICO", "Usuário criou novo servico")

    return novo_servico.id_servico

def buscar_servico_por_id(id_servico):
    """Busca por id"""
    servico = db.session.get(Servico, id_servico)
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


def criar_cardapio(nome, descricao, preco_base, id_usuario: int):
    '''cria cardapio'''
    novo_cardapio = Cardapio(nome=nome, descricao=descricao, preco_base=preco_base)
    db.session.add(novo_cardapio)
    db.session.commit()
    registrar_log(id_usuario,"CRIACAO CARDAPIO", "Usuário criou novo cardapio")

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



"""=============CRUD - SERVIÇO / BANCADA (Tabela de Associação)============"""

def associar_servico_bancada(id_servico, id_bancada, id_usuario: int):
    """Associa a bancada aos serviços"""
    associacao = db.session.get(ServicoBancada, (id_servico, id_bancada))
    if associacao:
        return False
    nova_associacao = ServicoBancada(id_servico=id_servico, id_bancada=id_bancada)
    db.session.add(nova_associacao)
    db.session.commit()
    registrar_log(id_usuario,"ASSOCIACAO SERVICO_BANCADA", "Usuário associou uma bancada a um servico")

    return True

def desassociar_servico_bancada(id_servico, id_bancada, id_usuario: int):
    """Desasossia a bancada aos serviços"""
    associacao = db.session.get(ServicoBancada, (id_servico, id_bancada))
    if not associacao:
        return False
    db.session.delete(associacao)
    db.session.commit()
    registrar_log(id_usuario,"DESASSOCIACAO SERVICO_BANCADA", "Usuário desassociou uma bancada a um servico")

    return True

def listar_bancadas_do_servico(id_servico):
    """Lista as bancadas que o serviço possui"""
    bancadas = db.session.execute(
        db.select(Bancada)
        .join(ServicoBancada, Bancada.id_bancada == ServicoBancada.id_bancada)
        .where(ServicoBancada.id_servico == id_servico)
    ).scalars().all()
    if bancadas:
        return bancadas
    return None


"""=====CRUD SERVIÇO / CARDÁPIO (Tabela de Associação)======"""

def associar_servico_cardapio(id_servico, id_cardapio, descricao=None, id_usuario= int):
    """Associa o cardapio aos serviços"""
    associacao = db.session.get(ServicoCardapio, (id_servico, id_cardapio))
    if associacao:
        return False
    nova_associacao = ServicoCardapio(id_servico=id_servico, id_cardapio=id_cardapio,descricao=descricao)
    db.session.add(nova_associacao)
    db.session.commit()
    registrar_log(id_usuario,"ASSOCIACAO SERVICO_CARDAPIO", "Usuário associou um cardapio a um servico")

    return True

def desassociar_servico_cardapio(id_servico, id_cardapio, id_usuario: int):
    """desassocia o cardapio aos serviços"""
    associacao = db.session.get(ServicoCardapio, (id_servico, id_cardapio))
    if not associacao:
        return False
    db.session.delete(associacao)
    db.session.commit()
    registrar_log(id_usuario,"DESASSOCIACAO SERVICO_CARDAPIO", "Usuário desassociou um cardapio a um servico")

    return True

def listar_cardapios_do_servico(id_servico):
    """Associa lista s cardapios do serviço"""
    resultados = db.session.execute(
        db.select(Cardapio, ServicoCardapio.descricao.label("descricao_associacao"))
        .join(ServicoCardapio, Cardapio.id_cardapio == ServicoCardapio.id_cardapio)
        .where(ServicoCardapio.id_servico == id_servico)).all()
    if resultados:
        return [{"cardapio": item.Cardapio,"descricao_personalizada": item.descricao_associacao}
            
            for item in resultados
        ]
    return None