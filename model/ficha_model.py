"""Modelos e operações de pratos, ingredientes, lotes e fichas técnicas."""

from datetime import datetime, timezone
from database import db
from model.usuario_model import registrar_log

class Prato(db.Model):
    """Prato do cardápio, com tipo, tempo de preparo e necessidade de pré-preparo."""
    __tablename__ = "prato"

    id_prato = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nome = db.Column(db.String(60), nullable=False)
    descricao = db.Column(db.Text, nullable=False)
    tipo_prato = db.Column(
        db.Enum("entrada", "acompanhamento", "prato principal", "sobremesa", name="tipo_prato"),
        nullable=False,
    )
    tempo_preparo = db.Column(db.Integer, nullable=False)
    requer_pre_preparo = db.Column(db.Boolean, default=False, nullable=False)



class PratoCardapio(db.Model):
    """Associação entre prato e cardápio, com quantidade e descrição."""
    __tablename__ = "prato_cardapio"
    id_prato = db.Column(db.Integer, db.ForeignKey("prato.id_prato"), primary_key=True)
    id_cardapio = db.Column(db.Integer, db.ForeignKey("cardapio.id_cardapio"), primary_key=True)

    qtd = db.Column(db.Integer, nullable=False)
    descricao = db.Column(db.Text, nullable=True)

    def __init__(self, id_prato: int, id_cardapio: int, qtd: int,
                 descricao: str = None):
        self.id_prato = id_prato
        self.id_cardapio = id_cardapio
        self.qtd = qtd
        self.descricao = descricao



class Ingrediente(db.Model):
    """Ingrediente de estoque, com unidade e quantidades atual e mínima."""
    __tablename__ = "ingrediente"

    id_ingrediente = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nome = db.Column(db.String(60), nullable=False)
    unidade = db.Column(db.String(10), nullable=False)  # ex: kg, g, ml, un
    qtd = db.Column(db.Numeric(10, 3), default=0.0, nullable=False)
    qtd_min = db.Column(db.Numeric(10, 3), default=0.0, nullable=False)

    __table_args__ = (
        db.CheckConstraint("qtd >= 0 AND qtd_min >= 0", name="ck_ingrediente_qtd"),
    )

    def __init__(self, nome: str, unidade: str, qtd=0.0, qtd_min=0.0):
        self.nome = nome
        self.unidade = unidade
        self.qtd = qtd
        self.qtd_min = qtd_min



class FichaTecnica(db.Model):
    """Ficha técnica: ingrediente e quantidade necessária por prato."""

    __tablename__ = "ficha_tecnica"

    id_prato = db.Column(db.Integer, db.ForeignKey("prato.id_prato"), primary_key=True)
    id_ingrediente = db.Column(db.Integer, db.ForeignKey("ingrediente.id_ingrediente"), primary_key=True)

    qtd_necessaria = db.Column(db.Integer, nullable=False)

    __table_args__ = (
        db.CheckConstraint("qtd_necessaria > 0", name="ck_ficha_qtd"),
    )

class FichaTecnica_bebida(db.Model):
    """Ficha técnica: ingrediente e quantidade necessária por bebida."""
    __tablename__ = "ficha_tecnica_bebida"

    id_bebida = db.Column(db.Integer, db.ForeignKey("bebida.id_bebida"), primary_key=True)
    id_ingrediente = db.Column(db.Integer, db.ForeignKey("ingrediente.id_ingrediente"), primary_key=True)
    qtd_necessaria = db.Column(db.Integer, nullable=False)

    __table_args__ = (
        db.CheckConstraint("qtd_necessaria > 0", name="ck_ficha_bebida_qtd"),
    )

class Lote(db.Model):
    """Lote de um ingrediente, com datas de recebimento/validade e quantidade."""

    __tablename__ = "lote"

    id_lote = db.Column(db.Integer, primary_key=True, autoincrement=True)
    num_lote = db.Column(db.String(60), nullable=False)
    marca = db.Column(db.String(60), nullable=False)
    data_recebimento = db.Column(db.DateTime, nullable=False)
    data_validade = db.Column(db.Date, nullable=True)  # Opcional
    qtd_inicial = db.Column(db.Numeric(10, 3), nullable=False)

   # Ou ingrediente ou bebida
    id_ingrediente = db.Column(db.Integer, db.ForeignKey("ingrediente.id_ingrediente"), nullable=True)
    #id_bebida = db.Column(db.Integer, db.ForeignKey("bebida.id_bebida"), nullable=True)

    #__table_args__ = (
    #   # UM dos campos seja NOT NULL
    #    db.CheckConstraint("(id_ingrediente IS NULL) <> (id_bebida IS NULL)", name="ck_lote_item"),
    #)

    def __init__(self, num_lote: str, marca: str, data_recebimento,
                 qtd_inicial, id_ingrediente: int = None, data_validade=None):
        self.num_lote = num_lote
        self.marca = marca
        self.data_recebimento = data_recebimento
        self.data_validade = data_validade
        self.qtd_inicial = qtd_inicial
        self.id_ingrediente = id_ingrediente

"""==================CRUD PRATO============="""
def criar_prato(nome: str, descricao: str, tipo_prato: str, tempo_preparo: int, requer_pre_preparo: bool = False) -> int:
    """Cria um prato e retorna seu id.

    Args:
        nome (str): nome do prato.
        descricao (str): descrição do prato.
        tipo_prato (str): tipo (entrada, acompanhamento, prato principal, sobremesa).
        tempo_preparo (int): tempo de preparo em minutos.
        requer_pre_preparo (bool, optional): se exige pré-preparo. Padrão: False.

    Returns:
        int: id do prato criado.
    """
    novo_prato = Prato(nome=nome,descricao=descricao,tipo_prato=tipo_prato,tempo_preparo=tempo_preparo,requer_pre_preparo=requer_pre_preparo,
    )
    db.session.add(novo_prato)
    db.session.commit()
    registrar_log("CRIACAO PRATO", f"Usuário criou o prato {novo_prato.nome}")
    return novo_prato.id_prato


def buscar_prato_por_id(id_prato: int) -> Prato | None:
    """Busca um prato pelo id. Retorna None se não existir."""
    prato = db.session.get(Prato, id_prato)
    if prato:
        return prato
    return None

def buscar_prato_por_nome(nome_prato: str) -> Prato | None:
    """Busca um prato pelo nome exato. Retorna None se não existir."""
    prato = db.session.execute(
        db.session.select(Prato).where(Prato.nome == nome_prato),
    ).scalar_one_or_none()

    if prato:
        return prato
    return None

def listar_pratos() -> list[Prato] | None:
    """Lista todos os pratos; None se não houver nenhum."""
    pratos = db.session.execute(db.select(Prato)).scalars().all()
    if pratos:
        return pratos
    return None

def buscar_pratos(busca: str = "") -> list:
    """Busca pratos por nome (correspondência parcial).

    Args:
        busca (str, optional): termo de busca. Padrão: "".

    Returns:
        list: pratos encontrados, ordenados por nome (vazia se não houver).
    """
    stmt = db.select(Prato)
    termo = busca.strip()
    if termo:
        stmt = stmt.where(Prato.nome.like(f"%{termo}%"))
    stmt = stmt.order_by(Prato.nome)
    return db.session.execute(stmt).scalars().all()


def atualizar_prato(id_prato: int, nome=None, descricao=None, tipo_prato=None, requer_pre_preparo=None, tempo_preparo=None) -> bool:
    """Atualiza os dados de um prato (campos None não são alterados).

    Args:
        id_prato (int): identificador do prato.
        nome (str | None, optional): novo nome.
        descricao (str | None, optional): nova descrição.
        tipo_prato (str | None, optional): novo tipo.
        requer_pre_preparo (bool | None, optional): nova flag de pré-preparo.
        tempo_preparo (int | None, optional): novo tempo de preparo.

    Returns:
        bool: True se atualizado; False se o prato não existir.
    """
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
    registrar_log("ATUALIZACAO PRATO", f"Usuário atualizou o prato {id_prato}")
    return True


def deletar_prato(id_prato: int) -> bool:
    """Remove um prato pelo id. Retorna False se não existir."""
    prato = db.session.get(Prato, id_prato)
    if not prato:
        return False
    db.session.delete(prato)
    db.session.commit()
    registrar_log("DELETAR PRATO", f"Usuário deletou o prato {id_prato}")
    return True


"""==================CRUD PRATO CARDAPIO============="""

def associar_prato_cardapio(id_prato: int, id_cardapio: int, qtd: int, descricao: str | None = None) -> tuple[int, int]:
    """Associa um prato a um cardápio.

    Args:
        id_prato (int): identificador do prato.
        id_cardapio (int): identificador do cardápio.
        qtd (int): quantidade do prato no cardápio.
        descricao (str | None, optional): descrição da associação.

    Returns:
        tuple[int, int]: par (id_prato, id_cardapio) associado.
    """
    novo_item = PratoCardapio(id_prato=id_prato,id_cardapio=id_cardapio,qtd=qtd,descricao=descricao,
    )
    db.session.add(novo_item)
    db.session.commit()
    registrar_log("CRIACAO PRATO_CARDAPIO", f"Usuário associou o prato {id_prato} ao cardápio {id_cardapio}")
    return (id_prato, id_cardapio)

def buscar_prato_cardapio(id_prato: int, id_cardapio: int) -> PratoCardapio | None:
    """Busca o vínculo prato-cardápio pela chave composta. None se não existir."""
    item = db.session.get(PratoCardapio, (id_prato, id_cardapio))
    if item:
        return item
    return None

def listar_pratos_por_cardapio(id_cardapio: int) -> list[PratoCardapio] | None:
    """Lista os vínculos de prato de um cardápio; None se não houver."""
    from seeds import cardapios_bebidas
    from model.servico_model import buscar_cardapio_por_id
    from model.pedido_model import BebidaCardapio
    
    cardapios_bebidas = [tupla[0] for tupla in cardapios_bebidas]

    if buscar_cardapio_por_id(id_cardapio) in cardapios_bebidas:
        stmt = db.select(BebidaCardapio).where(BebidaCardapio.id_cardapio == id_cardapio)
    else:
        stmt = db.select(PratoCardapio).where(PratoCardapio.id_cardapio == id_cardapio)
    
    itens = db.session.execute(stmt).scalars().all()
    if itens:
        return itens
    return None


def atualizar_prato_cardapio(id_prato: int, id_cardapio: int, qtd=None, descricao=None) -> bool:
    """Atualiza quantidade/descrição do prato no cardápio (None não altera).

    Args:
        id_prato (int): identificador do prato.
        id_cardapio (int): identificador do cardápio.
        qtd (int | None, optional): nova quantidade.
        descricao (str | None, optional): nova descrição.

    Returns:
        bool: True se atualizado; False se o vínculo não existir.
    """
    item = db.session.get(PratoCardapio, (id_prato, id_cardapio))
    if not item:
        return False
    if qtd is not None:
        item.qtd = qtd
    if descricao is not None:
        item.descricao = descricao

    db.session.commit()
    registrar_log("ATUALIZACAO PRATO_CARDAPIO", f"Usuário atualizou vínculo do prato {id_prato} no cardápio {id_cardapio}")
    return True

def deletar_prato_cardapio(id_prato: int, id_cardapio: int) -> bool:
    """Remove a associação entre prato e cardápio. False se não existir."""
    item = db.session.get(PratoCardapio, (id_prato, id_cardapio))
    if not item:
        return False
    db.session.delete(item)
    db.session.commit()
    registrar_log("DELETAR PRATO_CARDAPIO", f"Usuário desvinculou o prato {id_prato} do cardápio {id_cardapio}")
    return True


"""==================CRUD INGREDIENTE============="""

def criar_ingrediente(nome: str, unidade: str, qtd: float = 0.0, qtd_min: float = 0.0) -> int:
    """Cria um ingrediente e retorna seu id.

    Args:
        nome (str): nome do ingrediente.
        unidade (str): unidade de medida (ex.: kg, g, ml, un).
        qtd (float, optional): quantidade inicial em estoque. Padrão: 0.0.
        qtd_min (float, optional): quantidade mínima de alerta. Padrão: 0.0.

    Returns:
        int: id do ingrediente criado.
    """
    novo_ingrediente = Ingrediente(nome=nome,unidade=unidade,qtd=qtd,qtd_min=qtd_min,
    )
    db.session.add(novo_ingrediente)
    db.session.commit()
    registrar_log("CADASTRO INGREDIENTE", f"Usuário cadastrou o ingrediente {novo_ingrediente.nome}")
    return novo_ingrediente.id_ingrediente


def buscar_ingrediente_por_id(id_ingrediente: int) -> Ingrediente | None:
    """Busca um ingrediente pelo id. Retorna None se não existir."""
    ingrediente = db.session.get(Ingrediente, id_ingrediente)
    if ingrediente:
        return ingrediente
    return None

def buscar_ingrediente_por_nome(nome_ingrediente: str) -> Ingrediente | None:
    """Busca um ingrediente pelo nome exato. Retorna None se não existir."""
    ingrediente = db.session.execute(
        db.session.select(Ingrediente).where(Ingrediente.nome == nome_ingrediente),
    ).scalar_one_or_none()

    if ingrediente:
        return ingrediente
    return None


def listar_ingredientes() -> list[Ingrediente] | None:
    """Lista todos os ingredientes; None se não houver nenhum."""
    ingredientes = db.session.execute(db.select(Ingrediente)).scalars().all()
    if ingredientes:
        return ingredientes
    return None

def buscar_ingredientes(busca: str = "") -> list:
    """Busca ingredientes por nome (correspondência parcial).

    Args:
        busca (str, optional): termo de busca. Padrão: "".

    Returns:
        list: ingredientes encontrados, ordenados por nome (vazia se não houver).
    """
    stmt = db.select(Ingrediente)
    termo = busca.strip()
    if termo:
        stmt = stmt.where(Ingrediente.nome.like(f"%{termo}%"))
    stmt = stmt.order_by(Ingrediente.nome)
    return db.session.execute(stmt).scalars().all()


def atualizar_ingrediente(id_ingrediente: int, nome=None, unidade=None, qtd=None, qtd_min=None) -> bool:
    """Atualiza os dados de um ingrediente (campos None não são alterados).

    Args:
        id_ingrediente (int): identificador do ingrediente.
        nome (str | None, optional): novo nome.
        unidade (str | None, optional): nova unidade.
        qtd (float | None, optional): nova quantidade.
        qtd_min (float | None, optional): nova quantidade mínima.

    Returns:
        bool: True se atualizado; False se o ingrediente não existir.
    """

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
    registrar_log("ATUALIZACAO INGREDIENTE", f"Usuário atualizou o ingrediente {id_ingrediente}")
    return True


def deletar_ingrediente(id_ingrediente: int) -> bool:
    """Remove um ingrediente pelo id. Retorna False se não existir."""
    ingrediente = db.session.get(Ingrediente, id_ingrediente)
    if not ingrediente:
        return False
    db.session.delete(ingrediente)
    db.session.commit()
    registrar_log("DELETAR INGREDIENTE", f"Usuário deletou o ingrediente {id_ingrediente}")
    return True


"""==================CRUD FICHA TECNICA============="""

def criar_ficha_tecnica(id_prato: int, id_ingrediente: int, qtd_necessaria: float) -> tuple[int, int]:
    """Vincula um ingrediente à ficha técnica de um prato.

    Args:
        id_prato (int): identificador do prato.
        id_ingrediente (int): identificador do ingrediente.
        qtd_necessaria (float): quantidade necessária por porção/base.

    Returns:
        tuple[int, int]: par (id_prato, id_ingrediente) criado.
    """
    nova_ficha = FichaTecnica(id_prato=id_prato,id_ingrediente=id_ingrediente,qtd_necessaria=qtd_necessaria,
    )
    db.session.add(nova_ficha)
    db.session.commit()
    registrar_log("CRIACAO FICHA_TECNICA", f"Usuário adicionou o ingrediente {id_ingrediente} à ficha técnica do prato {id_prato}")
    return (id_prato, id_ingrediente)


def buscar_ficha_tecnica_item(id_prato: int, id_ingrediente: int) -> FichaTecnica | None:
    """Busca um item da ficha técnica pela chave composta. None se não existir."""
    ficha = db.session.get(FichaTecnica, (id_prato, id_ingrediente))
    if ficha:
        return ficha
    return None


def listar_ficha_tecnica_por_prato(id_prato: int) -> list[FichaTecnica] | None:
    """Lista os ingredientes da ficha técnica de um prato; None se não houver."""
    ficha = db.select(FichaTecnica).where(FichaTecnica.id_prato == id_prato)
    fichas = db.session.execute(ficha).scalars().all()
    if fichas:
        return fichas
    return None


def atualizar_ficha_tecnica(id_prato: int, id_ingrediente: int, qtd_necessaria: float, id_usuario: int | None = None) -> bool:
    """Atualiza a quantidade necessária de um item da ficha técnica do prato.

    Args:
        id_prato (int): identificador do prato.
        id_ingrediente (int): identificador do ingrediente.
        qtd_necessaria (float): nova quantidade necessária.
        id_usuario (int | None, optional): usuário responsável (para o log).

    Returns:
        bool: True se atualizado; False se o item não existir.
    """
    ficha = db.session.get(FichaTecnica, (id_prato, id_ingrediente))
    if not ficha:
        return False
    ficha.qtd_necessaria = qtd_necessaria
    db.session.commit()
    if id_usuario:
        registrar_log(id_usuario, "ATUALIZACAO FICHA_TECNICA", f"Usuário atualizou ficha técnica do prato {id_prato}")
    return True


def deletar_ficha_tecnica(id_prato: int, id_ingrediente: int) -> bool:
    """Remove um ingrediente da ficha técnica do prato. False se não existir."""
    ficha = db.session.get(FichaTecnica, (id_prato, id_ingrediente))
    if not ficha:
        return False
    db.session.delete(ficha)
    db.session.commit()
    registrar_log("DELETAR FICHA_TECNICA", f"Usuário removeu ingrediente {id_ingrediente} da ficha técnica do prato {id_prato}")
    return True


"""==================CRUD LOTE============="""

def criar_lote(num_lote: str, marca: str, data_recebimento: datetime, qtd_inicial: float, id_ingrediente: int | None = None, id_bebida: int | None = None, data_validade=None) -> int:
    """Cria um lote vinculado a um ingrediente e soma sua quantidade ao estoque.

    Args:
        num_lote (str): número do lote.
        marca (str): marca do produto.
        data_recebimento (datetime): data de recebimento.
        qtd_inicial (float): quantidade inicial do lote.
        id_ingrediente (int | None, optional): ingrediente vinculado.
        id_bebida (int | None, optional): bebida vinculada.
        data_validade (date | None, optional): data de validade (opcional).

    Returns:
        int: id do lote criado.
    """
    novo_lote = Lote(
        num_lote=num_lote,
        marca=marca,
        data_recebimento=data_recebimento,
        data_validade=data_validade,
        qtd_inicial=qtd_inicial,
        id_ingrediente=id_ingrediente,
        id_bebida=id_bebida,
    )

    db.session.add(novo_lote)

    # NOVO: soma a quantidade do lote ao estoque do ingrediente
    if id_ingrediente is not None:
        ingrediente = db.session.get(Ingrediente, id_ingrediente)

        if ingrediente:
            ingrediente.qtd = (ingrediente.qtd or 0) + qtd_inicial

    db.session.commit()

    registrar_log(
        "CRIACAO LOTE",
        f"Usuário criou o lote {novo_lote.num_lote}",
    )

    return novo_lote.id_lote


def buscar_lote_por_id(id_lote: int) -> Lote | None:
    """Busca um lote pelo id. Retorna None se não existir."""
    lote = db.session.get(Lote, id_lote)
    if lote:
        return lote
    return None

def buscar_lote_por_numero(num_lote: str) -> Lote | None:
    """Busca um lote pelo número. Retorna None se não existir."""
    lote = db.session.execute(
        db.session.select(Lote).where(Lote.num_lote == num_lote),
    ).scalar_one_or_none()

    if lote:
        return lote
    return None


def listar_lotes() -> list[Lote] | None:
    """Lista todos os lotes; None se não houver nenhum."""
    lotes = db.session.execute(db.select(Lote)).scalars().all()
    if lotes:
        return lotes
    return None

def buscar_lotes(busca: str = "") -> list:
    """Busca lotes por número ou marca (correspondência parcial).

    Args:
        busca (str, optional): termo de busca. Padrão: "".

    Returns:
        list: lotes encontrados, ordenados por número (vazia se não houver).
    """
    stmt = db.select(Lote)
    termo = busca.strip()
    if termo:
        padrao = f"%{termo}%"
        stmt = stmt.where(db.or_(Lote.num_lote.like(padrao), Lote.marca.like(padrao)))
    stmt = stmt.order_by(Lote.num_lote)
    return db.session.execute(stmt).scalars().all()


def atualizar_lote(id_lote: int, num_lote=None, marca=None, data_recebimento=None, data_validade=None, qtd_inicial=None, id_ingrediente=None, id_bebida=None) -> bool:
    """Atualiza os dados de um lote (campos None não são alterados).

    Args:
        id_lote (int): identificador do lote.
        num_lote (str | None, optional): novo número do lote.
        marca (str | None, optional): nova marca.
        data_recebimento (datetime | None, optional): nova data de recebimento.
        data_validade (date | None, optional): nova data de validade.
        qtd_inicial (float | None, optional): nova quantidade inicial.
        id_ingrediente (int | None, optional): novo ingrediente vinculado.
        id_bebida (int | None, optional): nova bebida vinculada.

    Returns:
        bool: True se atualizado; False se o lote não existir.
    """

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
    registrar_log("ATUALIZACAO LOTE", f"Usuário atualizou o lote {id_lote}")
    return True


def deletar_lote(id_lote: int) -> bool:
    """Remove um lote pelo id. Retorna False se não existir."""
    lote = db.session.get(Lote, id_lote)
    if not lote:
        return False
    db.session.delete(lote)
    db.session.commit()
    registrar_log("DELETAR LOTE", f"Usuário deletou o lote {id_lote}")
    return True


"""==================CRUD FICHA TECNICA BEBIDA============="""

def criar_ficha_tecnica_bebida(id_bebida: int, id_ingrediente: int, qtd_necessaria: int) -> tuple[int, int]:
    """Vincula um ingrediente à ficha técnica de uma bebida.

    Args:
        id_bebida (int): identificador da bebida.
        id_ingrediente (int): identificador do ingrediente.
        qtd_necessaria (int): quantidade necessária.

    Returns:
        tuple[int, int]: par (id_bebida, id_ingrediente) criado.
    """
    nova_ficha = FichaTecnica_bebida(
        id_bebida=id_bebida,
        id_ingrediente=id_ingrediente,
        qtd_necessaria=qtd_necessaria,
    )
    db.session.add(nova_ficha)
    db.session.commit()
    registrar_log(
        "CRIACAO FICHA_TECNICA_BEBIDA",
        f"Usuário adicionou o ingrediente {id_ingrediente} à ficha técnica da bebida {id_bebida}",
    )
    return (id_bebida, id_ingrediente)


def buscar_ficha_tecnica_bebida(id_bebida: int, id_ingrediente: int) -> FichaTecnica_bebida | None:
    """Busca um item da ficha técnica de bebida pela chave composta. None se não existir."""
    return db.session.get(FichaTecnica_bebida, (id_bebida, id_ingrediente))


def listar_ficha_tecnica_por_bebida(id_bebida: int) -> list[FichaTecnica_bebida]:
    """Lista os ingredientes da ficha técnica de uma bebida (vazia se não houver)."""
    stmt = db.select(FichaTecnica_bebida).where(FichaTecnica_bebida.id_bebida == id_bebida)
    return db.session.execute(stmt).scalars().all()


def atualizar_ficha_tecnica_bebida(id_bebida: int, id_ingrediente: int, qtd_necessaria: int) -> bool:
    """Atualiza a quantidade necessária de um ingrediente na ficha da bebida.

    Args:
        id_bebida (int): identificador da bebida.
        id_ingrediente (int): identificador do ingrediente.
        qtd_necessaria (int): nova quantidade necessária.

    Returns:
        bool: True se atualizado; False se o item não existir.
    """
    ficha = db.session.get(FichaTecnica_bebida, (id_bebida, id_ingrediente))
    if not ficha:
        return False
    ficha.qtd_necessaria = qtd_necessaria
    db.session.commit()
    registrar_log(
        "ATUALIZACAO FICHA_TECNICA_BEBIDA",
        f"Usuário atualizou a ficha técnica da bebida {id_bebida}",
    )
    return True


def deletar_ficha_tecnica_bebida(id_bebida: int, id_ingrediente: int) -> bool:
    """Remove um ingrediente da ficha técnica de uma bebida. False se não existir."""
    ficha = db.session.get(FichaTecnica_bebida, (id_bebida, id_ingrediente))
    if not ficha:
        return False
    db.session.delete(ficha)
    db.session.commit()
    registrar_log(
        "DELETAR FICHA_TECNICA_BEBIDA",
        f"Usuário removeu o ingrediente {id_ingrediente} da ficha técnica da bebida {id_bebida}",
    )
    return True
