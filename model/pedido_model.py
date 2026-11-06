"""Modelos e operações de pedidos, bebidas e suas associações."""

from datetime import datetime
from zoneinfo import ZoneInfo

from model.usuario_model import registrar_log

from database import db
from sqlalchemy.exc import IntegrityError
from sqlalchemy import extract


# TABELAS
class Pedido(db.Model):
    """Pedido de um cliente, com status, datas, valor e vínculos de cliente/endereço/chefe."""
    __tablename__ = "pedido"

    id_pedido = db.Column(db.Integer, primary_key=True, autoincrement=True)
    observacao = db.Column(db.Text, nullable=True)  # Opcional
    status = db.Column(
        db.Enum("aguardando", "confirmado", "em preparo", "concluido", "cancelado", name="status_pedido"),default="aguardando",nullable=False)
    confirmado_em = db.Column(db.DateTime, nullable=True)
    criado_em = db.Column(db.DateTime, default=lambda: datetime.now(ZoneInfo("America/Sao_Paulo")), nullable=False)
    num_convidados = db.Column(db.Integer, nullable=False, default=1)
    valor_total = db.Column(db.Numeric(10, 2), nullable=False, default=0.00)
    data_evento = db.Column(db.Date, nullable=False)
    hora_inicio = db.Column(db.Time, nullable=False)
    hora_fim = db.Column(db.Time, nullable=False)

    id_cliente = db.Column(db.Integer, db.ForeignKey("usuario.id_usuario"), nullable=False)
    id_endereco = db.Column(db.Integer, db.ForeignKey("endereco.id_endereco"), nullable=False)
    id_chefe = db.Column(db.Integer, db.ForeignKey("usuario.id_usuario"), nullable=True)
    #id_servico = db.Column(db.Integer, db.ForeignKey("servico.id_servico"), nullable=False)
    #id_cardapio = db.Column(db.Integer, db.ForeignKey("cardapio.id_cardapio"), nullable=False)

    __table_args__ = (
        db.CheckConstraint("num_convidados > 0", name="ck_pedido_convidados"),
        db.CheckConstraint("valor_total >= 0", name="ck_pedido_valor"),
    )

class Bebida(db.Model):
    """Bebida que pode compor um pedido."""
    __tablename__ = "bebida"

    id_bebida = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nome = db.Column(db.String(60), nullable=False)
    descricao = db.Column(db.Text, nullable=False)
    valor_unitario = db.Column(db.Numeric(10, 2), nullable=False)

    __table_args__ = (
        db.CheckConstraint("valor_unitario >= 0", name="ck_bebida_valor"),
    )

class PedidoBebida(db.Model):
    """Associação entre pedido e bebida, com quantidade e valor total."""
    __tablename__ = "pedido_bebida"


    id_pedido = db.Column(db.Integer, db.ForeignKey("pedido.id_pedido"), primary_key=True)
    id_bebida = db.Column(db.Integer, db.ForeignKey("bebida.id_bebida"), primary_key=True)

    qtd = db.Column(db.Integer, nullable=False)
    valor_total = db.Column(db.Numeric(10, 2), nullable=False)

    __table_args__ = (
        db.CheckConstraint("qtd > 0", name="ck_pedido_bebida_qtd"),
    )
# Tabela de associação entre cardápio e bebida

class bebidaCardapio(db.Model):
    """Associação entre bebida e cardápio."""
    __tablename__ = "bebida_cardapio"

    id_bebida = db.Column(db.Integer, db.ForeignKey("bebida.id_servico"), primary_key=True)
    id_cardapio = db.Column(db.Integer, db.ForeignKey("cardapio.id_cardapio"), primary_key=True)

class CardapioPedido(db.Model):
    """Associação entre cardápio, pedido e serviço."""
    __tablename__ = "cardapio_pedido"

    id_cardapio = db.Column(db.Integer, db.ForeignKey("cardapio.id_cardapio"), primary_key=True)
    id_pedido = db.Column(db.Integer, db.ForeignKey("pedido.id_pedido"), primary_key=True)
    id_servico = db.Column(db.Integer, db.ForeignKey("servico.id_servico"), primary_key=True)

# ======================================================

# CRUD BEBIDA
def criar_bebida(nome: str, descricao: str, valor_unitario: float) -> Bebida:
    """Cria uma bebida e registra o log da operação.

    Args:
        nome (str): nome da bebida.
        descricao (str): descrição da bebida.
        valor_unitario (float): valor unitário.

    Returns:
        Bebida: a bebida criada.
    """
    bebida = Bebida(nome=nome, descricao=descricao, valor_unitario=valor_unitario)
    db.session.add(bebida)
    db.session.commit()
    registrar_log("CRIACAO BEBIDA", f"Usuário criou a bebida {bebida.nome}")
    return bebida

def buscar_bebida_por_id(id_bebida: int) -> Bebida | None:
    """Busca uma bebida pelo id. Retorna None se não existir."""
    return db.session.get(Bebida, id_bebida)

def buscar_bebida_por_nome(nome_bebida: str) -> Bebida | None:
    """Busca uma bebida pelo nome exato. Retorna None se não existir."""
    bebida = db.session.execute(
        db.session.select(Bebida).where(Bebida.nome == nome_bebida),
    ).scalar_one_or_none()

    if bebida:
        return bebida
    return None

def listar_bebidas() -> list[Bebida]:
    """Lista todas as bebidas cadastradas."""
    return db.session.query(Bebida).all()

def buscar_bebidas(busca: str = "") -> list:
    """Busca bebidas por nome (correspondência parcial).

    Args:
        busca (str, optional): termo de busca. Padrão: "".

    Returns:
        list: bebidas encontradas, ordenadas por nome (vazia se não houver).
    """
    stmt = db.select(Bebida)
    termo = busca.strip()
    if termo:
        stmt = stmt.where(Bebida.nome.like(f"%{termo}%"))
    stmt = stmt.order_by(Bebida.nome)
    return db.session.execute(stmt).scalars().all()


def atualizar_bebida(id_bebida: int, nome=None, descricao=None, valor_unitario=None) -> bool:
    """Atualiza os dados de uma bebida (campos None não são alterados).

    Args:
        id_bebida (int): identificador da bebida.
        nome (str | None, optional): novo nome.
        descricao (str | None, optional): nova descrição.
        valor_unitario (float | None, optional): novo valor unitário.

    Returns:
        bool: True se atualizada; False se a bebida não existir.
    """
    bebida = db.session.get(Bebida, id_bebida)

    if not bebida:
        return False

    if nome is not None:
        bebida.nome = nome
    if descricao is not None:
        bebida.descricao = descricao
    if valor_unitario is not None:
        bebida.valor_unitario = valor_unitario
    db.session.commit()
    registrar_log("ATUALIZACAO BEBIDA", f"Usuário atualizou a bebida {id_bebida}")
    return True

def deletar_bebida(id_bebida: int) -> bool:
    """Remove uma bebida pelo id. Retorna False se não existir."""
    bebida = db.session.get(Bebida, id_bebida)
    if not bebida:
        return False
    db.session.delete(bebida)
    db.session.commit()
    registrar_log("REMOCAO BEBIDA", f"Usuario deletou bebida {bebida.nome}")

    return True

def associar_bebida_cardapio(id_bebida: int, id_cardapio: int) -> tuple[int, int]:
    """Associa uma bebida a um cardápio.

    Args:
        id_bebida (int): identificador da bebida.
        id_cardapio (int): identificador do cardápio.

    Returns:
        tuple[int, int]: par (id_bebida, id_cardapio) associado.
    """
    novo_item = bebidaCardapio(id_bebida=id_bebida,id_cardapio=id_cardapio,
    )
    db.session.add(novo_item)
    db.session.commit()
    registrar_log("CRIACAO BEBIDA_CARDAPIO", f"Usuário associou a bebida {id_bebida} ao cardápio {id_cardapio}")
    return (id_bebida, id_cardapio)

# CRUD - PEDIDO
def criar_pedido(id_cliente: int, id_endereco: int, num_convidados: int, valor_total: float, data_evento: str, hora_inicio: str, hora_fim: str, cardapios: list[dict], observacao: str | None = None, bebidas: list[dict] | None = None) -> Pedido | None:
    """Cria um pedido e associa seus cardápios e bebidas (quando houver).

    Persiste o pedido, vincula os cardápios e, se fornecidas, as bebidas, e
    garante a trigger de baixa de estoque.

    Args:
        id_cliente (int): identificador do cliente.
        id_endereco (int): identificador do endereço de entrega.
        num_convidados (int): número de convidados.
        valor_total (float): valor total do pedido.
        data_evento (str): data do evento.
        hora_inicio (str): hora de início.
        hora_fim (str): hora de término.
        cardapios (list[dict]): cardápios do pedido (cada item com 'id_cardapio').
        observacao (str | None, optional): observação do pedido.
        bebidas (list[dict] | None, optional): bebidas do pedido (cada item com
            'id_bebida', 'qtd' e 'valor_unitario').

    Returns:
        Pedido | None: o pedido criado; None em caso de violação de integridade.
    """
    novo_pedido = Pedido(
        id_cliente=id_cliente,
        id_endereco=id_endereco,
        #id_servico=id_servico,
        #id_cardapio=id_cardapio,
        num_convidados=num_convidados,
        valor_total=valor_total,
        data_evento=data_evento,
        hora_inicio=hora_inicio,
        hora_fim=hora_fim,
        observacao=observacao,

    )
    db.session.add(novo_pedido)

    try:
        db.session.flush()

        for cardapio in cardapios:
            p_c = CardapioPedido(
                id_cardapio=cardapio["id_cardapio"],
                id_pedido=novo_pedido.id_pedido,
            )
            db.session.add(p_c)

        db.session.flush()
        #verifica se o pedido tem bebida, se tiver adiciona
        if bebidas:
            for item in bebidas:
                p_b = PedidoBebida(
                    id_pedido=novo_pedido.id_pedido,
                    id_bebida=item["id_bebida"],
                    qtd=item["qtd"],
                    valor_unitario=item["valor_unitario"],
                )
                db.session.add(p_b)

        from triggers import criar_trigger_baixa_estoque
        
        criar_trigger_baixa_estoque()

        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return None

    registrar_log("PEDIDO", f"Pedido {novo_pedido.id_pedido} criado.")
    return novo_pedido

def buscar_pedido_por_id(id_pedido: int) -> Pedido | None:
    """Busca um pedido pelo id. Retorna None se não existir."""
    return db.session.get(Pedido, id_pedido)

def listar_pedidos_por_cliente(id_cliente: int) -> list[Pedido]:
    """Lista todos os pedidos realizados por um cliente."""
    return db.session.query(Pedido).filter_by(id_cliente=id_cliente).all()

def listar_pedidos_periodo(ano, mes, dia, status=None) -> list[Pedido] | None:
    """Retorna os pedidos de um status até certo dia de um mês/ano específicos.

    Args:
        ano (int | str): ano de referência (deve ser numérico).
        mes (int | str): mês de referência (deve ser numérico, 1 a 12).
        dia (int | str): dia de referência (deve ser numérico, 1 a 31).
        status (str | None, optional): status para filtragem. Padrão: None.

    Returns:
        list[Pedido] | None: lista de pedidos no período (vazia se não houver);
        None se algum parâmetro for inválido.
    """
    try:
        ano=int(ano)
        mes=int(mes)
        dia=int(dia)
    except (ValueError, TypeError):
        return None

    if not 1 <= mes <= 12 or not 1 <= dia <= 31:
        return None

    return db.session.execute(
        db.select(Pedido).where(
            Pedido.status==status,
            extract("month", Pedido.data_evento) == mes,
            extract("year", Pedido.data_evento) == ano,
            extract("day", Pedido.data_evento) <= dia,
        ),
    ).scalars().all()

def listar_pedidos_entre_datas(ano, mes, dia, ano_final=None, mes_final=None, dia_final=None, status="concluido") -> list[Pedido] | None:
    """Retorna os pedidos de um status entre duas datas (inclusive).

    Quando a data final não é informada, assume a data de hoje.

    Args:
        ano (int | str): ano da data inicial.
        mes (int | str): mês da data inicial (1 a 12).
        dia (int | str): dia da data inicial.
        ano_final (int | str | None, optional): ano da data final.
        mes_final (int | str | None, optional): mês da data final.
        dia_final (int | str | None, optional): dia da data final.
        status (str, optional): status para filtragem. Padrão: "concluido".

    Returns:
        list[Pedido] | None: pedidos no intervalo (vazia se não houver); None se
        os parâmetros forem inválidos ou a data final for anterior à inicial.
    """
    from utils import hoje, para_data

    if not (ano_final or mes_final or dia_final):
        ano_final=hoje().year
        mes_final=hoje().month
        dia_final=hoje().day

    try:
        data_inicio = para_data(int(ano), int(mes), int(dia))
        data_fim = para_data(int(ano_final), int(mes_final), int(dia_final))
    except (ValueError, TypeError):
        return None

    if data_fim < data_inicio:
        return None

    return db.session.execute(
        db.select(Pedido).where(
            Pedido.status == status,
            Pedido.data_evento >= data_inicio,
            Pedido.data_evento <= data_fim,
        ),
    ).scalars().all()

def atualizar_pedido(id_pedido: int, status=None, confirmado_em=None, id_chefe=None, observacao=None, num_convidados=None, valor_total=None) -> bool | None:
    """Atualiza dados cadastrais e de status de um pedido (campos None são ignorados).

    Args:
        id_pedido (int): identificador do pedido.
        status (str | None, optional): novo status.
        confirmado_em (datetime | None, optional): data/hora de confirmação.
        id_chefe (int | None, optional): identificador do chefe responsável.
        observacao (str | None, optional): nova observação.
        num_convidados (int | None, optional): novo número de convidados.
        valor_total (float | None, optional): novo valor total.

    Returns:
        bool | None: True se atualizado; False se o pedido não existir; None em
        caso de violação de integridade.
    """
    pedido = db.session.get(Pedido, id_pedido)
    if not pedido:
        return False

    if status is not None:
        pedido.status = status
    if confirmado_em is not None:
        pedido.confirmado_em = confirmado_em
    if id_chefe is not None:
        pedido.id_chefe = id_chefe
    if observacao is not None:
        pedido.observacao = observacao
    if num_convidados is not None:
        pedido.num_convidados = num_convidados
    if valor_total is not None:
        pedido.valor_total = valor_total

    try:
        db.session.commit()
        registrar_log("ATUALIZACAO PEDIDO", f"Dados do pedido {id_pedido} atualizados.")
        return True
    except IntegrityError:
        return None


def deletar_pedido(id_pedido: int) -> bool:
    """Remove um pedido pelo id. Retorna False se não existir."""
    pedido = db.session.get(Pedido, id_pedido)
    if not pedido:
        return False

    db.session.delete(pedido)
    db.session.commit()
    registrar_log("REMOCAO PEDIDO", f"Pedido {id_pedido} removido do sistema.")
    return True



#PEDIDO_BEBIDA
def adicionar_bebida_ao_pedido(id_pedido: int, id_bebida: int, qtd: int, valor_unitario: float) -> bool:
    """Adiciona uma bebida a um pedido ou soma a quantidade, se já existir.

    Args:
        id_pedido (int): identificador do pedido.
        id_bebida (int): identificador da bebida.
        qtd (int): quantidade a adicionar.
        valor_unitario (float): valor unitário da bebida.

    Returns:
        bool: True se adicionada/atualizada; False se o pedido ou a bebida não
        existirem.
    """
    pedido = db.session.get(Pedido, id_pedido)
    bebida = db.session.get(Bebida, id_bebida)
    if not pedido or not bebida:
        return False

    item = db.session.get(PedidoBebida, (id_pedido, id_bebida))
    if item:
        item.qtd += qtd
    else:
        item = PedidoBebida(
            id_pedido=id_pedido,
            id_bebida=id_bebida,
            qtd=qtd,
            valor_unitario=valor_unitario,
        )
        db.session.add(item)

    db.session.commit()
    return True

def remover_bebida_do_pedido(id_pedido: int, id_bebida: int) -> bool:
    """Remove uma bebida de um pedido. Retorna False se o vínculo não existir."""
    item = db.session.get(PedidoBebida, (id_pedido, id_bebida))
    if not item:
        return False

    db.session.delete(item)
    db.session.commit()
    return True

# CRUD CardapioPedido
def criar_cardapio_pedido(id_cardapio: int, id_pedido: int, id_servico: int) -> CardapioPedido | None:
    """Relaciona um cardápio a um pedido (e serviço).

    Args:
        id_cardapio (int): identificador do cardápio.
        id_pedido (int): identificador do pedido.
        id_servico (int): identificador do serviço.

    Returns:
        CardapioPedido | None: a associação criada; None em caso de violação de
        integridade.
    """

    cardapio_pedido=CardapioPedido(id_cardapio, id_pedido, id_servico)

    db.session.add(cardapio_pedido)

    try:
        db.session.commit(cardapio_pedido)
        return cardapio_pedido
    except IntegrityError:
        db.session.rollback()
        return None

def buscar_cardapios_pedido(id_pedido: int) -> list[CardapioPedido]:
    """Retorna todas as associações cardápio-pedido de um pedido."""
    """Retorna todos os cardápios relacionados a um pedido."""
    return db.session.execute(
        db.select(CardapioPedido).where(
    CardapioPedido.id_pedido == id_pedido,
        ),
    ).scalars().all()

def deletar_cardapios_pedido(id_pedido: int) -> bool:
    """Remove todas as associações de cardápio de um pedido.

    Args:
        id_pedido (int): identificador do pedido.

    Returns:
        bool: True se a remoção ocorreu; False em caso de violação de integridade.
    """
    try:
        db.session.execute(
            db.delete(CardapioPedido).where(
                CardapioPedido.id_pedido == id_pedido,
            ),
        )
        db.session.commit()
        return True

    except IntegrityError:
        db.session.rollback()
        return False
