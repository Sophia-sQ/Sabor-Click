"""Modelos e operações de bancadas, serviços, cardápios e suas associações."""

from database import db, Base
from model.usuario_model import registrar_log
from slugify import slugify



class Bancada(db.Model):
    """Bancada de produção (estação de trabalho)."""
    __tablename__ = "bancada"

    id_bancada = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nome = db.Column(db.String(60), nullable=False)
    descricao = db.Column(db.Text, nullable=False)
    
    def __init__(self, nome: str, descricao: str):
        self.nome = nome
        self.descricao = descricao

class Servico(db.Model):
    """Serviço oferecido; gera o slug automaticamente a partir do nome."""
        
    __tablename__ = "servico"

    id_servico = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nome = db.Column(db.String(60), unique=True, nullable=False)
    descricao = db.Column(db.Text, nullable=False)
    slug = db.Column(db.String(120), nullable=False, unique=True)

    # É executada cada vez que a classe é instanciada
    def __init__(self, nome: str, descricao: str, slug: str = None, **kwargs):
        self.nome = nome
        self.descricao = descricao
        self.slug = slug or slugify(nome)
        # mantém compatibilidade com qualquer outro campo passado via kwargs
        for chave, valor in kwargs.items():
            setattr(self, chave, valor)

class ServicoBancada(db.Model):
    """Associação entre serviço e bancada."""
    __tablename__ = "servico_bancada"

    id_servico = db.Column(db.Integer, db.ForeignKey("servico.id_servico"), primary_key=True)
    id_bancada = db.Column(db.Integer, db.ForeignKey("bancada.id_bancada"), primary_key=True)

    def __init__(self, id_servico: int, id_bancada: int):
        self.id_servico = id_servico
        self.id_bancada = id_bancada

class Cardapio(db.Model):
    """Cardápio com nome, descrição e preço-base (em centavos)."""
    __tablename__ = "cardapio"

    id_cardapio = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nome = db.Column(db.String(60), nullable=False)
    descricao = db.Column(db.Text, nullable=False)
    # preço por pessoa em CENTAVOS (ex.: 14990 = R$ 149,90). Use utils.formatar_moeda
    # para exibir em Real.
    preco_base = db.Column(db.Integer, nullable=False)
    # slug usado para resolver a imagem do cardápio em docs/imagens-menu.json.
    # É a fonte de verdade para cardápios novos (id >= 19, fora de
    # _CARDAPIO_POR_ID); os 18 cardápios seed continuam resolvíveis via fallback
    # pelo dicionário _CARDAPIO_POR_ID no controller do cliente.
    imagem_slug = db.Column(db.String(120), nullable=True)

    __table_args__ = (
        db.CheckConstraint("preco_base >= 0", name="ck_cardapio_preco"),
    )

class ServicoCardapio(db.Model):
    """Associação entre serviço e cardápio (cardápios compartilhados entre serviços)."""
    __tablename__ = "servico_cardapio"

    id_servico = db.Column(db.Integer, db.ForeignKey("servico.id_servico"), primary_key=True)
    id_cardapio = db.Column(db.Integer, db.ForeignKey("cardapio.id_cardapio"), primary_key=True)

    def __init__(self, id_servico: int, id_cardapio: int):
        self.id_servico = id_servico
        self.id_cardapio = id_cardapio

"""==================CRUD BANCADA============="""
def criar_bancada(nome: str, descricao: str) -> int:
    """Cria uma bancada e retorna seu id.

    Args:
        nome (str): nome da bancada.
        descricao (str): descrição da bancada.

    Returns:
        int: id da bancada criada.
    """
    nova_bancada = Bancada(nome=nome, descricao=descricao)
    db.session.add(nova_bancada)
    db.session.commit()
    registrar_log("CRIACAO BANCADA", "Usuário criou nova bancada")
    return nova_bancada.id_bancada

def buscar_bancada_por_id(id_bancada) -> Bancada | None:
    """Busca uma bancada pelo id. Retorna None se não existir."""
    bancada = db.session.get(Bancada, id_bancada)
    if bancada:
        return bancada
    return None

def buscar_bancada_por_nome(nome_bancada) -> Bancada | None:
    """Busca uma bancada pelo nome exato. Retorna None se não existir."""
    bancada = db.session.execute(
            db.select(Bancada).where(Bancada.nome == nome_bancada),
    ).scalar_one_or_none()

    if bancada:
        return bancada
    return None

def listar_bancadas() -> list[Bancada] | None:
    """Lista todas as bancadas; None se não houver nenhuma."""
    bancadas = db.session.execute(db.select(Bancada)).scalars().all()
    if bancadas:
        return bancadas
    return None

def atualizar_bancada(id_bancada, id_usuario: int, nome=None, descricao=None) -> bool:
    """Atualiza os dados de uma bancada (campos None não são alterados).

    Args:
        id_bancada: identificador da bancada.
        id_usuario (int): usuário responsável (para o log).
        nome (str | None, optional): novo nome.
        descricao (str | None, optional): nova descrição.

    Returns:
        bool: True se atualizada; False se a bancada não existir.
    """
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

def deletar_bancada(id_bancada, id_usuario: int) -> bool:
    """Remove uma bancada pelo id. Retorna False se não existir."""
    bancada = db.session.get(Bancada, id_bancada)
    if not bancada:
        return False
    db.session.delete(bancada)
    db.session.commit()
    registrar_log(id_usuario,"DELETAR BANCADA", "Usuário deletou bancada")

    return True

"""==============CRUD SERVICO======"""
def criar_servico(nome, descricao) -> int:
    """Cria um serviço e retorna seu id.

    Args:
        nome: nome do serviço.
        descricao: descrição do serviço.

    Returns:
        int: id do serviço criado.
    """
    novo_servico = Servico(nome=nome, descricao=descricao)
    db.session.add(novo_servico)
    db.session.commit()
    registrar_log("CRIACAO SERVICO", "Usuário criou novo servico")

    return novo_servico.id_servico

def buscar_servico_por_id(id_servico) -> Servico | None:
    """Busca um serviço pelo id. Retorna None se não existir."""
    servico = db.session.get(Servico, id_servico)
    if servico:
        return servico
    return None

def buscar_servico_por_nome(nome_servico) -> Servico | None:
    """Busca um serviço pelo nome exato. Retorna None se não existir."""
    servico = db.session.execute(
            db.select(Servico).where(Servico.nome == nome_servico),
    ).scalar_one_or_none()

    if servico:
        return servico
    return None

def buscar_servico_por_slug(slug_servico: str) -> Servico | None:
    """Busca um serviço pelo slug. Retorna None se não existir."""
    servico = db.session.execute(
        db.select(Servico).where(Servico.slug == slug_servico),
    ).scalar_one_or_none()

    if servico:
        return servico
    return None

def listar_servicos() -> list[Servico] | None:
    """Lista todos os serviços; None se não houver nenhum."""
    servicos = db.session.execute(db.select(Servico)).scalars().all()
    if servicos:
        return servicos
    return None

def buscar_servicos(busca: str = "") -> list:
    """Busca serviços por nome (correspondência parcial).

    Args:
        busca (str, optional): termo de busca. Padrão: "".

    Returns:
        list: serviços encontrados, ordenados por nome (vazia se não houver).
    """
    stmt = db.select(Servico)
    termo = busca.strip()
    if termo:
        stmt = stmt.where(Servico.nome.like(f"%{termo}%"))
    stmt = stmt.order_by(Servico.nome)
    return db.session.execute(stmt).scalars().all()

def atualizar_servico(id_servico, id_usuario: int, nome=None, descricao=None) -> bool:
    """Atualiza os dados de um serviço (campos None não são alterados).

    Args:
        id_servico: identificador do serviço.
        id_usuario (int): usuário responsável (para o log).
        nome (str | None, optional): novo nome.
        descricao (str | None, optional): nova descrição.

    Returns:
        bool: True se atualizado; False se o serviço não existir.
    """
    servico = db.session.get(Servico, id_servico)
    if not servico:
        return False
    if nome:
        servico.nome = nome
    if descricao:
        servico.descricao = descricao
    db.session.commit()
    registrar_log("ATUALIZACAO SERVICO", "Usuário atulizou o servico")

    return True

def deletar_servico(id_servico) -> bool:
    """Remove um serviço pelo id. Retorna False se não existir."""
    servico = db.session.get(Servico, id_servico)
    if not servico:
        return False
    db.session.delete(servico)
    db.session.commit()
    registrar_log("DELETAR SERVICO", "Usuário deletou servico")

    return True



"""===============CRUD CARDÁPIO========="""
def criar_cardapio(nome, descricao, preco_base, imagem_slug=None) -> int:
    """Cria um cardápio e retorna seu id.

    Args:
        nome: nome do cardápio.
        descricao: descrição do cardápio.
        preco_base: preço-base do cardápio.
        imagem_slug (str | None, optional): slug da imagem em
            docs/imagens-menu.json; None quando o cardápio é criado sem imagem.

    Returns:
        int: id do cardápio criado.
    """

    novo_cardapio = Cardapio(nome=nome, descricao=descricao, preco_base=preco_base, imagem_slug=imagem_slug)
    db.session.add(novo_cardapio)
    db.session.commit()
    registrar_log("CRIACAO CARDAPIO", "Usuário criou novo cardapio")

    return novo_cardapio.id_cardapio

def buscar_cardapio_por_id(id_cardapio) -> Cardapio | None:
    """Busca um cardápio pelo id. Retorna None se não existir."""
    cardapio = db.session.get(Cardapio, id_cardapio)
    if cardapio:
        return cardapio
    return None

def buscar_cardapio_por_nome(nome_cardapio) -> Cardapio | None:
    """Busca um cardápio pelo nome exato. Retorna None se não existir."""
    cardapio = db.session.execute(
            db.select(Cardapio).where(Cardapio.nome == nome_cardapio),
    ).scalar_one_or_none()

    if cardapio:
        return cardapio
    return None

def listar_cardapios() -> list[Cardapio] | None:
    """Lista todos os cardápios; None se não houver nenhum."""
    cardapios = db.session.execute(db.select(Cardapio)).scalars().all()
    if cardapios:
        return cardapios
    return None

def atualizar_cardapio(id_cardapio, id_usuario: int, nome=None, descricao=None, preco_base=None, imagem_slug=None) -> bool:
    """Atualiza os dados de um cardápio (campos None não são alterados).

    Args:
        id_cardapio: identificador do cardápio.
        id_usuario (int): usuário responsável (para o log).
        nome (str | None, optional): novo nome.
        descricao (str | None, optional): nova descrição.
        preco_base (optional): novo preço-base.
        imagem_slug (str | None, optional): novo slug de imagem; só é alterado
            quando fornecido (não-None), seguindo o padrão dos demais campos.

    Returns:
        bool: True se atualizado; False se o cardápio não existir.
    """
    cardapio = db.session.get(Cardapio, id_cardapio)
    if not cardapio:
        return False
    if nome:
        cardapio.nome = nome
    if descricao:
        cardapio.descricao = descricao
    if preco_base is not None:
        cardapio.preco_base = preco_base
    if imagem_slug is not None:
        cardapio.imagem_slug = imagem_slug
    db.session.commit()
    registrar_log(id_usuario,"ATUALIZACAO CARDAPIO", "Usuário atualizou cardapio")

    return True

def deletar_cardapio(id_cardapio, id_usuario: int) -> bool:
    """Remove um cardápio pelo id. Retorna False se não existir."""
    cardapio = db.session.get(Cardapio, id_cardapio)
    if not cardapio:
        return False
    db.session.delete(cardapio)
    db.session.commit()
    registrar_log(id_usuario,"DELETAR CARDAPIO", "Usuário deletou cardapio")

    return True



"""============= CRUD - SERVIÇO / BANCADA (Tabela de Associação) ============"""

def associar_servico_bancada(id_servico, id_bancada, id_usuario: int) -> bool:
    """Associa uma bancada a um serviço.

    Args:
        id_servico: identificador do serviço.
        id_bancada: identificador da bancada.
        id_usuario (int): usuário responsável (para o log).

    Returns:
        bool: True se associados; False se a associação já existir.
    """
    associacao = db.session.get(ServicoBancada, (id_servico, id_bancada))
    if associacao:
        return False
    nova_associacao = ServicoBancada(id_servico=id_servico, id_bancada=id_bancada)
    db.session.add(nova_associacao)
    db.session.commit()
    registrar_log(id_usuario,"ASSOCIACAO SERVICO_BANCADA", "Usuário associou uma bancada a um servico")

    return True



def desassociar_servico_bancada(id_servico: int, id_bancada: int, id_usuario: int) -> bool:
    """Desfaz a associação entre uma bancada e um serviço.

    Args:
        id_servico (int): identificador do serviço.
        id_bancada (int): identificador da bancada.
        id_usuario (int): usuário responsável (para o log).

    Returns:
        bool: True se desassociados; False se a associação não existir.
    """
    associacao = db.session.get(ServicoBancada, (id_servico, id_bancada))
    if not associacao:
        return False
    db.session.delete(associacao)
    db.session.commit()
    registrar_log(id_usuario,"DESASSOCIACAO SERVICO_BANCADA", "Usuário desassociou uma bancada a um servico")

    return True

def listar_bancadas_do_servico(id_servico: int) -> list | None:
    """Lista as bancadas associadas a um serviço; None se não houver."""
    bancadas = db.session.execute(
        db.select(Bancada)
        .join(ServicoBancada, Bancada.id_bancada == ServicoBancada.id_bancada)
        .where(ServicoBancada.id_servico == id_servico),
    ).scalars().all()
    if bancadas:
        return bancadas
    return None


"""=====CRUD SERVIÇO / CARDÁPIO (Tabela de Associação)======"""

def associar_servico_cardapio(id_servico, id_cardapio, descricao=None, id_usuario=int) -> bool:
    """Associa um cardápio a um serviço.

    Args:
        id_servico: identificador do serviço.
        id_cardapio: identificador do cardápio.
        descricao (optional): descrição da associação.
        id_usuario (int): usuário responsável (para o log).

    Returns:
        bool: True se associados; False se a associação já existir.
    """

    associacao = db.session.get(ServicoCardapio, (id_servico, id_cardapio))
    if associacao:
        return False
    nova_associacao = ServicoCardapio(id_servico=id_servico, id_cardapio=id_cardapio,descricao=descricao)
    db.session.add(nova_associacao)
    db.session.commit()
    registrar_log(id_usuario,"ASSOCIACAO SERVICO_CARDAPIO", "Usuário associou um cardapio a um servico")

    return True

def desassociar_servico_cardapio(id_servico, id_cardapio, id_usuario: int) -> bool:
    """Desfaz a associação entre um cardápio e um serviço.

    Args:
        id_servico: identificador do serviço.
        id_cardapio: identificador do cardápio.
        id_usuario (int): usuário responsável (para o log).

    Returns:
        bool: True se desassociados; False se a associação não existir.
    """
    associacao = db.session.get(ServicoCardapio, (id_servico, id_cardapio))
    if not associacao:
        return False
    db.session.delete(associacao)
    db.session.commit()
    registrar_log(id_usuario,"DESASSOCIACAO SERVICO_CARDAPIO", "Usuário desassociou um cardapio a um servico")

    return True

def listar_cardapios_do_servico(id_servico: int) -> list | None:
    """Retorna as associações de cardápio de um serviço; None se não houver."""
    cardapios = db.session.execute(
            db.select(ServicoCardapio).where(
        ServicoCardapio.id_servico == id_servico,
        )).scalars().all()

    if cardapios:
        return cardapios
    return None

