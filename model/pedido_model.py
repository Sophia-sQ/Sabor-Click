# Contém a tabela: Pedido
from datetime import datetime
from decimal import Decimal
from zoneinfo import ZoneInfo

from model.usuario_model import registrar_log

from database import db
from sqlalchemy.exc import DatabaseError, IntegrityError, OperationalError
from sqlalchemy import extract


# TABELAS
class Pedido(db.Model):
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
    __tablename__ = "bebida"

    id_bebida = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nome = db.Column(db.String(60), nullable=False)
    descricao = db.Column(db.Text, nullable=False)
    valor_unitario = db.Column(db.Numeric(10, 2), nullable=False)

    __table_args__ = (
        db.CheckConstraint("valor_unitario >= 0", name="ck_bebida_valor"),
    )

class PedidoBebida(db.Model):
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
    __tablename__ = "bebida_cardapio"

    id_bebida = db.Column(db.Integer, db.ForeignKey("bebida.id_bebida"), primary_key=True)
    id_cardapio = db.Column(db.Integer, db.ForeignKey("cardapio.id_cardapio"), primary_key=True)

class CardapioPedido(db.Model):
    __tablename__ = "cardapio_pedido"

    id_cardapio = db.Column(db.Integer, db.ForeignKey("cardapio.id_cardapio"), primary_key=True)
    id_pedido = db.Column(db.Integer, db.ForeignKey("pedido.id_pedido"), primary_key=True)
    id_servico = db.Column(db.Integer, db.ForeignKey("servico.id_servico"), primary_key=True)

# ======================================================

# CRUD BEBIDA
def criar_bebida(nome: str, descricao: str, valor_unitario: float):
    """Cria a bebida"""
    bebida = Bebida(nome=nome, descricao=descricao, valor_unitario=valor_unitario)
    db.session.add(bebida)
    db.session.commit()
    registrar_log("CRIACAO BEBIDA", f"Usuário criou a bebida {bebida.nome}")
    return bebida

def buscar_bebida_por_id(id_bebida: int) :
    """Busca a bebidada pelo id"""
    return db.session.get(Bebida, id_bebida)

def buscar_bebida_por_nome(nome_bebida: str):
    """Busca bebida pelo nome"""
    bebida = db.session.execute(
        db.session.select(Bebida).where(Bebida.nome == nome_bebida),
    ).scalar_one_or_none()

    if bebida:
        return bebida
    return None

def listar_bebidas():
    """Lista as bebidas disponíveis"""
    return db.session.query(Bebida).all()

def buscar_bebidas(busca: str = "") -> list:
    """Busca bebidas por nome (correspondência parcial).

    Retorna lista vazia quando não há resultados.
    """
    stmt = db.select(Bebida)
    termo = busca.strip()
    if termo:
        stmt = stmt.where(Bebida.nome.like(f"%{termo}%"))
    stmt = stmt.order_by(Bebida.nome)
    return db.session.execute(stmt).scalars().all()


def atualizar_bebida(id_bebida: int, nome: str | None = None, descricao: str | None = None, valor_unitario: float | None = None):
    """Atualiza os dados da bebida"""
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

def deletar_bebida(id_bebida: int):
    """Deleta a bebida"""
    bebida = db.session.get(Bebida, id_bebida)
    if not bebida:
        return False
    db.session.delete(bebida)
    db.session.commit()
    registrar_log("REMOCAO BEBIDA", f"Usuario deletou bebida {bebida.nome}")

    return True

def associar_bebida_cardapio(id_bebida: int, id_cardapio: int):
    """Associa uma bebida a um cardápio"""
    novo_item = bebidaCardapio(id_bebida=id_bebida,id_cardapio=id_cardapio,
    )
    db.session.add(novo_item)
    db.session.commit()
    registrar_log("CRIACAO BEBIDA_CARDAPIO", f"Usuário associou a bebida {id_bebida} ao cardápio {id_cardapio}")
    return (id_bebida, id_cardapio)

# CRUD - PEDIDO
def criar_pedido(id_cliente: int, id_endereco: int , num_convidados: int, valor_total: float, data_evento: str, hora_inicio: str, hora_fim: str, cardapios: list[dict], observacao: str | None = None, bebidas: list[dict] | None = None) -> (Pedido | None):
    """Cria um pedido associando cardápios e bebidas a ele (caso tenha)."""
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
                id_servico=cardapio["id_servico"],
            )
            db.session.add(p_c)

        db.session.flush()
        #verifica se o pedido tem bebida, se tiver adiciona
        if bebidas:
            for item in bebidas:
                qtd = int(item["qtd"])
                valor_unitario = Decimal(str(item["valor_unitario"]))
                p_b = PedidoBebida(
                    id_pedido=novo_pedido.id_pedido,
                    id_bebida=item["id_bebida"],
                    qtd=qtd,
                    valor_total=valor_unitario * qtd,
                )
                db.session.add(p_b)

        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return None

    registrar_log("PEDIDO", f"Pedido {novo_pedido.id_pedido} criado.")
    return novo_pedido

def buscar_pedido_por_id(id_pedido: int):
    """Busca pedido."""
    return db.session.get(Pedido, id_pedido)

def listar_pedidos_por_cliente(id_cliente: int) :
    """Lista os pedidos realizados pelo cliente."""
    return db.session.query(Pedido).filter_by(id_cliente=id_cliente).all()

def listar_pedidos_pendentes() -> list[Pedido]:
    """Lista os pedidos aguardando aceite por um chef.

    Retorna os pedidos com status ``'aguardando'`` e sem chef responsável,
    ordenados do mais antigo para o mais recente (ordem de chegada).

    Returns:
        list[Pedido]: pedidos pendentes de aceite. Lista vazia se não houver.
    """
    return db.session.execute(
        db.select(Pedido)
        .where(Pedido.status == "aguardando", Pedido.id_chefe.is_(None))
        .order_by(Pedido.criado_em.asc()),
    ).scalars().all()

def listar_pedidos_do_chefe(id_chefe: int) -> list[Pedido]:
    """Lista os pedidos sob responsabilidade de um chef.

    Args:
        id_chefe (int): identificador do chef responsável.

    Returns:
        list[Pedido]: pedidos atribuídos ao chef, dos mais recentes aos mais
        antigos. Lista vazia se não houver.
    """
    return db.session.execute(
        db.select(Pedido)
        .where(Pedido.id_chefe == id_chefe)
        .order_by(Pedido.criado_em.desc()),
    ).scalars().all()

def listar_pedidos_periodo(ano:int|str, mes:int|str, dia:int|str, status=None) -> list[Pedido] | None:
    """Retorna todos os pedidos concluidos até certo dia de mês e ano específicos.

    Args:
        ano (int | str): Ano de referencia. Deve ser um dígito. 
        mes (int | str): Mês de referencia. Deve ser um dígito. 
        dia (int | str): Dia de referencia. Deve ser um dígito. 

    Returns:
        list[Pedido] | None: Retorna uma lista vazia caso não existam pedidos no periodo ou None se um dos parâmetros não for dígito. Do contrário, retorna uma lista de objetos Pedido.
    """
    try:
        ano=int(ano)
        mes=int(mes)
        dia=int(dia)
    except (ValueError, TypeError):
        return None

    if not 1 <= mes <= 12 or not 1 <= dia <= 31:
        return None

    filtros = [
        extract("month", Pedido.data_evento) == mes,
        extract("year", Pedido.data_evento) == ano,
        extract("day", Pedido.data_evento) <= dia,
    ]
    # Só filtra por status quando um status foi informado; status=None significa
    # "todos os status" (evita gerar status IS NULL, que nunca casa com nada).
    if status is not None:
        filtros.append(Pedido.status == status)

    return db.session.execute(
        db.select(Pedido).where(*filtros),
    ).scalars().all()

def listar_pedidos_entre_datas(ano:int|str, mes:int|str, dia:int|str, ano_final:int | str | None = None, mes_final:int | str | None = None, dia_final:int | str | None = None, status="concluido") -> list[Pedido] | None:
    """Retorna os pedidos concluídos entre duas datas, Caso data final seja None, considera como sendo a data de hoje.

    Args:
        ano (int | str): Ano da data inicial.
        mes (int | str): Mês da data inicial, de 1 a 12.
        dia (int | str): Dia da data inicial.
        ano_final (int | str, optional): Ano da data final.
        mes_final (int | str, optional): Mês da data final.
        dia_final (int | str, optional): Dia da data final.

    Returns:
        list[Pedido] | None:
            Retorna uma lista de objetos Pedido cujo status é
            'concluido' e cuja data_evento está entre as datas
            inicial e final, inclusive.

            Retorna uma lista vazia se nenhum pedido for encontrado
            e None se os parâmetros forem inválidos ou se a data
            final for anterior à data inicial.

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

    filtros = [
        Pedido.data_evento >= data_inicio,
        Pedido.data_evento <= data_fim,
    ]
    if status is not None:
        filtros.append(Pedido.status == status)

    return db.session.execute(
        db.select(Pedido).where(*filtros),
    ).scalars().all()

def atualizar_pedido(
    id_pedido: int,
    status: str | None = None,
    confirmado_em: datetime | None = None,
    id_chefe: int | None = None,
    observacao: str | None = None,
    num_convidados: int | None = None,
    valor_total: float | None = None):
    """Atualiza dados cadastrais e de status do pedido"""
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


def aceitar_pedido_atomico(id_pedido: int, id_chefe: int, confirmado_em: datetime) -> bool:
    """Atribui um pedido a um chef de forma atômica (resolve concorrência).

    Executa um ``UPDATE`` condicional que só tem efeito quando o pedido ainda
    está ``aguardando`` e sem chef responsável (``id_chefe IS NULL``). Dessa
    forma, se dois chefs tentarem aceitar o mesmo pedido simultaneamente, apenas
    o primeiro ``UPDATE`` afeta uma linha; o segundo não altera nada. A mudança
    de ``status`` para ``'confirmado'`` é o gatilho da baixa de estoque, e como
    a transição só ocorre uma vez, não há risco de baixa dupla.

    Args:
        id_pedido (int): identificador do pedido a ser aceito.
        id_chefe (int): identificador do chef que está aceitando.
        confirmado_em (datetime): momento da confirmação.

    Returns:
        bool: ``True`` se este chef assumiu o pedido; ``False`` se o pedido não
        existe, já foi aceito por outro chef, ou se a baixa de estoque foi
        abortada por falta de ingredientes (a transação é revertida).
    """
    resultado = db.session.execute(
        db.update(Pedido)
        .where(
            Pedido.id_pedido == id_pedido,
            Pedido.id_chefe.is_(None),
            Pedido.status == "aguardando",
        )
        .values(
            status="confirmado",
            id_chefe=id_chefe,
            confirmado_em=confirmado_em,
        ),
    )

    if resultado.rowcount == 0:
        db.session.rollback()
        return False

    try:
        # O commit dispara a trigger de baixa de estoque; se o estoque for
        # insuficiente, a trigger aborta e levanta um erro aqui.
        db.session.commit()
    except (IntegrityError, OperationalError, DatabaseError):
        db.session.rollback()
        return False

    return True


def atualizar_status_pelo_chefe(id_pedido: int, id_chefe: int, status: str) -> bool:
    """Atualiza o status de um pedido, garantindo que o chef seja o responsável.

    Só permite a alteração quando o pedido pertence ao chef informado
    (``id_chefe`` igual ao responsável). Isso impede que um chef altere pedidos
    de outro chef via chamadas diretas de URL.

    Args:
        id_pedido (int): identificador do pedido.
        id_chefe (int): identificador do chef responsável que faz a alteração.
        status (str): novo status, dentro dos valores válidos de ``status_pedido``.

    Returns:
        bool: ``True`` se o status foi atualizado; ``False`` se o pedido não
        existe, o chef não é o responsável, ou o status é inválido.
    """
    status_validos = {"aguardando", "confirmado", "em preparo", "concluido", "cancelado"}
    if status not in status_validos:
        return False

    pedido = db.session.get(Pedido, id_pedido)
    if not pedido or pedido.id_chefe != id_chefe:
        return False

    pedido.status = status

    try:
        db.session.commit()
        registrar_log("ATUALIZACAO PEDIDO", f"Status do pedido {id_pedido} alterado para '{status}'.")
        return True
    except IntegrityError:
        db.session.rollback()
        return False


def deletar_pedido(id_pedido: int):
    """Deleta pedido"""
    pedido = db.session.get(Pedido, id_pedido)
    if not pedido:
        return False

    db.session.delete(pedido)
    db.session.commit()
    registrar_log("REMOCAO PEDIDO", f"Pedido {id_pedido} removido do sistema.")
    return True



#PEDIDO_BEBIDA
def adicionar_bebida_ao_pedido(id_pedido: int, id_bebida: int, qtd: int, valor_unitario: float) -> bool:
    """Adiciona (ou incrementa) uma bebida em um pedido.

    Quando a bebida já consta no pedido, soma a quantidade e recalcula o valor
    total do item; caso contrário, cria uma nova linha em ``pedido_bebida``.

    Args:
        id_pedido (int): identificador do pedido.
        id_bebida (int): identificador da bebida.
        qtd (int): quantidade de unidades a adicionar.
        valor_unitario (float): valor unitário da bebida.

    Returns:
        bool: ``True`` em caso de sucesso; ``False`` se o pedido ou a bebida
        não existirem.
    """
    pedido = db.session.get(Pedido, id_pedido)
    bebida = db.session.get(Bebida, id_bebida)
    if not pedido or not bebida:
        return False

    qtd = int(qtd)
    valor_unitario = Decimal(str(valor_unitario))

    item = db.session.get(PedidoBebida, (id_pedido, id_bebida))
    if item:
        item.qtd += qtd
        item.valor_total = valor_unitario * item.qtd
    else:
        item = PedidoBebida(
            id_pedido=id_pedido,
            id_bebida=id_bebida,
            qtd=qtd,
            valor_total=valor_unitario * qtd,
        )
        db.session.add(item)

    db.session.commit()
    return True

def remover_bebida_do_pedido(id_pedido: int, id_bebida: int) -> bool:
    """Remove uma bebida de um pedido.

    Args:
        id_pedido (int): identificador do pedido.
        id_bebida (int): identificador da bebida a remover.

    Returns:
        bool: ``True`` se o item existia e foi removido; ``False`` caso contrário.
    """
    item = db.session.get(PedidoBebida, (id_pedido, id_bebida))
    if not item:
        return False

    db.session.delete(item)
    db.session.commit()
    return True

# CRUD CardapioPedido
def criar_cardapio_pedido(id_cardapio: int, id_pedido: int, id_servico: int) -> (CardapioPedido | None):
    """Relaciona um cardápio a um pedido.

    Args:
        id_cardapio (int): identificador do cardápio.
        id_pedido (int): identificador do pedido.
        id_servico (int): identificador do serviço do cardápio no pedido.

    Returns:
        CardapioPedido | None: a associação criada, ou ``None`` em caso de erro
        de integridade.
    """
    cardapio_pedido = CardapioPedido(
        id_cardapio=id_cardapio,
        id_pedido=id_pedido,
        id_servico=id_servico,
    )

    db.session.add(cardapio_pedido)

    try:
        db.session.commit()
        return cardapio_pedido
    except IntegrityError:
        db.session.rollback()
        return None

def buscar_cardapios_pedido(id_pedido: int):
    """Retorna todos os cardápios relacionados a um pedido."""
    return db.session.execute(
        db.select(CardapioPedido).where(
    CardapioPedido.id_pedido == id_pedido,
        ),
    ).scalars().all()

def buscar_bebidas_pedido(id_pedido: int) -> list:
    """Retorna as bebidas (linhas de ``pedido_bebida``) de um pedido.

    Args:
        id_pedido (int): identificador do pedido.

    Returns:
        list[PedidoBebida]: itens de bebida do pedido. Lista vazia se não houver.
    """
    return db.session.execute(
        db.select(PedidoBebida).where(PedidoBebida.id_pedido == id_pedido),
    ).scalars().all()

def deletar_cardapios_pedido(id_pedido: int) -> (bool):
    """Deleta todos os cardápios relacionados a um pedido."""
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
