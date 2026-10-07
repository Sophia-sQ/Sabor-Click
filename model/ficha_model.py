from datetime import datetime
from database import db
from model.usuario_model import registrar_log

class Prato(db.Model):
    __tablename__ = "prato"

    id_prato = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nome = db.Column(db.String(60), nullable=False)
    descricao = db.Column(db.Text, nullable=False)
    tipo_prato = db.Column(
        db.Enum("entrada", "acompanhamento", "prato principal", "sobremesa", name="tipo_prato"),
        nullable=False
    )
    
    requer_pre_preparo = db.Column(db.Boolean, default=False, nullable=False)
    tempo_preparo = db.Column(db.Integer, nullable=False)

class PratoCardapio(db.Model):
    __tablename__ = "prato_cardapio"
    id_prato = db.Column(db.Integer, db.ForeignKey("prato.id_prato"), primary_key=True)
    id_cardapio = db.Column(db.Integer, db.ForeignKey("cardapio.id_cardapio"), primary_key=True)
    
    qtd = db.Column(db.Integer, nullable=False)
    descricao = db.Column(db.Text, nullable=True)  


class Ingrediente(db.Model):
    __tablename__ = "ingrediente"

    id_ingrediente = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nome = db.Column(db.String(60), nullable=False)
    unidade = db.Column(db.String(10), nullable=False)  # ex: kg, g, ml, un
    qtd = db.Column(db.Numeric(10, 3), default=0.0, nullable=False)
    qtd_min = db.Column(db.Numeric(10, 3), default=0.0, nullable=False)

    __table_args__ = (
        db.CheckConstraint("qtd >= 0 AND qtd_min >= 0", name="ck_ingrediente_qtd"),
    )


class FichaTecnica(db.Model):
    __tablename__ = "ficha_tecnica"

    id_prato = db.Column(db.Integer, db.ForeignKey("prato.id_prato"), primary_key=True)
    id_ingrediente = db.Column(db.Integer, db.ForeignKey("ingrediente.id_ingrediente"), primary_key=True)
    
    qtd_necessaria = db.Column(db.Numeric(10, 3), nullable=False)

    __table_args__ = (
        db.CheckConstraint("qtd_necessaria > 0", name="ck_ficha_qtd"),
    )


class Lote(db.Model):
    __tablename__ = "lote"

    id_lote = db.Column(db.Integer, primary_key=True, autoincrement=True)
    num_lote = db.Column(db.String(60), nullable=False)
    marca = db.Column(db.String(60), nullable=False)
    data_recebimento = db.Column(db.DateTime, nullable=False)
    data_validade = db.Column(db.Date, nullable=True)  # Opcional
    qtd_inicial = db.Column(db.Numeric(10, 3), nullable=False)
    
   # Ou ingrediente ou bebida
    id_ingrediente = db.Column(db.Integer, db.ForeignKey("ingrediente.id_ingrediente"), nullable=True)
    id_bebida = db.Column(db.Integer, db.ForeignKey("bebida.id_bebida"), nullable=True)

    __table_args__ = (
       # UM dos campos seja NOT NULL
        db.CheckConstraint("(id_ingrediente IS NULL) <> (id_bebida IS NULL)", name="ck_lote_item"),
    )

"""==================CRUD PRATO============="""

def criar_prato(nome: str, descricao: str, tipo_prato: str, tempo_preparo: int, requer_pre_preparo: bool = False, id_usuario: int = None):
    """Cria um novo prato"""
    novo_prato = Prato(nome=nome,descricao=descricao,tipo_prato=tipo_prato,tempo_preparo=tempo_preparo,requer_pre_preparo=requer_pre_preparo
    )
    db.session.add(novo_prato)
    db.session.commit()
    if id_usuario:
        registrar_log("CRIACAO PRATO", f"Usuário criou o prato {novo_prato.nome}")
    return novo_prato.id_prato


def buscar_prato_por_id(id_prato: int):
    """Busca prato pelo id"""
    prato = db.session.get(Prato, id_prato)
    if prato:
        return prato
    return None


def listar_pratos():
    """Lista todos os pratos"""
    pratos = db.session.execute(db.select(Prato)).scalars().all()
    if pratos:
        return pratos
    return None


def atualizar_prato(id_prato: int, id_usuario: int = None, nome=None, descricao=None, tipo_prato=None, requer_pre_preparo=None, tempo_preparo=None):
    """Atualiza os dados do prato"""
    prato = db.session.get(Prato, id_prato)
    if not prato:
        return False
    if nome is not None:
        prato.nome = nome
    if descricao is not None:
        prato.descricao = descricao
    if tipo_prato is not None:
        prato.tipo_prato = tipo_prato
    if requer_pre_preparo is not None:
        prato.requer_pre_preparo = requer_pre_preparo
    if tempo_preparo is not None:
        prato.tempo_preparo = tempo_preparo

    db.session.commit()
    if id_usuario:
        registrar_log(id_usuario, "ATUALIZACAO PRATO", f"Usuário atualizou o prato {id_prato}")
    return True


def deletar_prato(id_prato: int, id_usuario: int = None):
    """Deleta prato"""
    prato = db.session.get(Prato, id_prato)
    if not prato:
        return False
    db.session.delete(prato)
    db.session.commit()
    if id_usuario:
        registrar_log(id_usuario, "DELETAR PRATO", f"Usuário deletou o prato {id_prato}")
    return True


"""==================CRUD PRATO CARDAPIO============="""

def associar_prato_cardapio(id_prato: int, id_cardapio: int, qtd: int, descricao: str = None, id_usuario: int = None):
    """Associa um prato a um cardápio"""
    novo_item = PratoCardapio(id_prato=id_prato,id_cardapio=id_cardapio,qtd=qtd,descricao=descricao
    )
    db.session.add(novo_item)
    db.session.commit()
    if id_usuario:
        registrar_log(id_usuario, "CRIACAO PRATO_CARDAPIO", f"Usuário associou o prato {id_prato} ao cardápio {id_cardapio}")
    return (id_prato, id_cardapio)


def buscar_prato_cardapio(id_prato: int, id_cardapio: int):
    """Busca vínculo de prato em cardápio pelas chaves compostas"""
    item = db.session.get(PratoCardapio, (id_prato, id_cardapio))
    if item:
        return item
    return None


def listar_pratos_por_cardapio(id_cardapio: int):
    """Lista todos os pratos vinculados a um determinado cardápio"""
    stmt = db.select(PratoCardapio).where(PratoCardapio.id_cardapio == id_cardapio)
    itens = db.session.execute(stmt).scalars().all()
    if itens:
        return itens
    return None


def atualizar_prato_cardapio(id_prato: int, id_cardapio: int, id_usuario: int = None, qtd=None, descricao=None):
    """Atualiza quantidade ou descrição do prato no cardápio"""
    item = db.session.get(PratoCardapio, (id_prato, id_cardapio))
    if not item:
        return False
    if qtd is not None:
        item.qtd = qtd
    if descricao is not None:
        item.descricao = descricao

    db.session.commit()
    if id_usuario:
        registrar_log(id_usuario, "ATUALIZACAO PRATO_CARDAPIO", f"Usuário atualizou vínculo do prato {id_prato} no cardápio {id_cardapio}")
    return True


def deletar_prato_cardapio(id_prato: int, id_cardapio: int, id_usuario: int = None):
    """Deleta associação entre prato e cardápio"""
    item = db.session.get(PratoCardapio, (id_prato, id_cardapio))
    if not item:
        return False
    db.session.delete(item)
    db.session.commit()
    if id_usuario:
        registrar_log(id_usuario, "DELETAR PRATO_CARDAPIO", f"Usuário desvinculou o prato {id_prato} do cardápio {id_cardapio}")
    return True


"""==================CRUD INGREDIENTE============="""

def criar_ingrediente(nome: str, unidade: str, qtd: float = 0.0, qtd_min: float = 0.0, id_usuario: int = None):
    """Cria um novo ingrediente"""
    novo_ingrediente = Ingrediente(nome=nome,unidade=unidade,qtd=qtd,qtd_min=qtd_min
    )
    db.session.add(novo_ingrediente)
    db.session.commit()
    if id_usuario:
        registrar_log(id_usuario, "CADASTRO INGREDIENTE", f"Usuário cadastrou o ingrediente {novo_ingrediente.nome}")
    return novo_ingrediente.id_ingrediente


def buscar_ingrediente_por_id(id_ingrediente: int):
    """Busca ingrediente pelo id"""
    ingrediente = db.session.get(Ingrediente, id_ingrediente)
    if ingrediente:
        return ingrediente
    return None


def listar_ingredientes():
    """Lista todos os ingredientes"""
    ingredientes = db.session.execute(db.select(Ingrediente)).scalars().all()
    if ingredientes:
        return ingredientes
    return None


def atualizar_ingrediente(id_ingrediente: int, id_usuario: int = None, nome=None, unidade=None, qtd=None, qtd_min=None):
    """Atualiza dados do ingrediente"""
    ingrediente = db.session.get(Ingrediente, id_ingrediente)
    if not ingrediente:
        return False
    if nome is not None:
        ingrediente.nome = nome
    if unidade is not None:
        ingrediente.unidade = unidade
    if qtd is not None:
        ingrediente.qtd = qtd
    if qtd_min is not None:
        ingrediente.qtd_min = qtd_min

    db.session.commit()
    if id_usuario:
        registrar_log(id_usuario, "ATUALIZACAO INGREDIENTE", f"Usuário atualizou o ingrediente {id_ingrediente}")
    return True


def deletar_ingrediente(id_ingrediente: int, id_usuario: int = None):
    """Deleta ingrediente"""
    ingrediente = db.session.get(Ingrediente, id_ingrediente)
    if not ingrediente:
        return False
    db.session.delete(ingrediente)
    db.session.commit()
    if id_usuario:
        registrar_log(id_usuario, "DELETAR INGREDIENTE", f"Usuário deletou o ingrediente {id_ingrediente}")
    return True


"""==================CRUD FICHA TECNICA============="""

def criar_ficha_tecnica(id_prato: int, id_ingrediente: int, qtd_necessaria: float, id_usuario: int = None):
    """Vincula ingrediente à ficha técnica de um prato"""
    nova_ficha = FichaTecnica(id_prato=id_prato,id_ingrediente=id_ingrediente,qtd_necessaria=qtd_necessaria
    )
    db.session.add(nova_ficha)
    db.session.commit()
    if id_usuario:
        registrar_log(id_usuario, "CRIACAO FICHA_TECNICA", f"Usuário adicionou o ingrediente {id_ingrediente} à ficha técnica do prato {id_prato}")
    return (id_prato, id_ingrediente)


def buscar_ficha_tecnica_item(id_prato: int, id_ingrediente: int):
    """Busca item específico da ficha técnica"""
    ficha = db.session.get(FichaTecnica, (id_prato, id_ingrediente))
    if ficha:
        return ficha
    return None


def listar_ficha_tecnica_por_prato(id_prato: int):
    """Lista todos os ingredientes da ficha técnica de um prato"""
    ficha = db.select(FichaTecnica).where(FichaTecnica.id_prato == id_prato)
    fichas = db.session.execute(ficha).scalars().all()
    if fichas:
        return fichas
    return None


def atualizar_ficha_tecnica(id_prato: int, id_ingrediente: int, qtd_necessaria: float, id_usuario: int = None):
    """Atualiza a quantidade necessária na ficha técnica"""
    ficha = db.session.get(FichaTecnica, (id_prato, id_ingrediente))
    if not ficha:
        return False
    ficha.qtd_necessaria = qtd_necessaria
    db.session.commit()
    if id_usuario:
        registrar_log(id_usuario, "ATUALIZACAO FICHA_TECNICA", f"Usuário atualizou ficha técnica do prato {id_prato}")
    return True


def deletar_ficha_tecnica(id_prato: int, id_ingrediente: int, id_usuario: int = None):
    """Remove um ingrediente da ficha técnica do prato"""
    ficha = db.session.get(FichaTecnica, (id_prato, id_ingrediente))
    if not ficha:
        return False
    db.session.delete(ficha)
    db.session.commit()
    if id_usuario:
        registrar_log(id_usuario, "DELETAR FICHA_TECNICA", f"Usuário removeu ingrediente {id_ingrediente} da ficha técnica do prato {id_prato}")
    return True


"""==================CRUD LOTE============="""

def criar_lote(num_lote: str, marca: str, data_recebimento: datetime, qtd_inicial: float, id_ingrediente: int = None, id_bebida: int = None, data_validade=None, id_usuario: int = None):
    """Cria um novo lote (vinculado a um ingrediente OU bebida)"""
    novo_lote = Lote(num_lote=num_lote,marca=marca,data_recebimento=data_recebimento,data_validade=data_validade,qtd_inicial=qtd_inicial,id_ingrediente=id_ingrediente,id_bebida=id_bebida
    )
    db.session.add(novo_lote)
    db.session.commit()
    if id_usuario:
        registrar_log(id_usuario, "CRIACAO LOTE", f"Usuário criou o lote {novo_lote.num_lote}")
    return novo_lote.id_lote


def buscar_lote_por_id(id_lote: int):
    """Busca lote pelo id"""
    lote = db.session.get(Lote, id_lote)
    if lote:
        return lote
    return None


def listar_lotes():
    """Lista todos os lotes"""
    lotes = db.session.execute(db.select(Lote)).scalars().all()
    if lotes:
        return lotes
    return None


def atualizar_lote(id_lote: int, id_usuario: int = None, num_lote=None, marca=None, data_recebimento=None, data_validade=None, qtd_inicial=None, id_ingrediente=None, id_bebida=None):
    """Atualiza dados do lote"""
    lote = db.session.get(Lote, id_lote)
    if not lote:
        return False
    if num_lote is not None:
        lote.num_lote = num_lote
    if marca is not None:
        lote.marca = marca
    if data_recebimento is not None:
        lote.data_recebimento = data_recebimento
    if data_validade is not None:
        lote.data_validade = data_validade
    if qtd_inicial is not None:
        lote.qtd_inicial = qtd_inicial
    if id_ingrediente is not None:
        lote.id_ingrediente = id_ingrediente
    if id_bebida is not None:
        lote.id_bebida = id_bebida

    db.session.commit()
    if id_usuario:
        registrar_log(id_usuario, "ATUALIZACAO LOTE", f"Usuário atualizou o lote {id_lote}")
    return True


def deletar_lote(id_lote: int, id_usuario: int = None):
    """Deleta lote"""
    lote = db.session.get(Lote, id_lote)
    if not lote:
        return False
    db.session.delete(lote)
    db.session.commit()
    if id_usuario:
        registrar_log(id_usuario, "DELETAR LOTE", f"Usuário deletou o lote {id_lote}")
    return True    