# Contém a tabela: Pedido
<<<<<<< Updated upstream
from model.usuario_model import registrar_log

from datetime import datetime, timezone, timedelta
from database import db
from sqlalchemy.exc import IntegrityError
from sqlalchemy import extract

=======
from datetime import datetime
from zoneinfo import ZoneInfo

from model.usuario_model import registrar_log

from database import db
from sqlalchemy.exc import IntegrityError
from sqlalchemy import extract


>>>>>>> Stashed changes
# TABELAS
class Pedido(db.Model):
    __tablename__ = "pedido"

    id_pedido = db.Column(db.Integer, primary_key=True, autoincrement=True)
    observacao = db.Column(db.Text, nullable=True)  # Opcional
    status = db.Column(
        db.Enum("aguardando", "confirmado", "em preparo", "concluido", "cancelado", name="status_pedido"),default="aguardando",nullable=False)
    confirmado_em = db.Column(db.DateTime, nullable=True)
<<<<<<< Updated upstream
    criado_em = db.Column(db.DateTime, default=datetime.now(timezone.utc), nullable=False)
=======
    criado_em = db.Column(db.DateTime, default=lambda: datetime.now(ZoneInfo("America/Sao_Paulo")), nullable=False)
>>>>>>> Stashed changes
    num_convidados = db.Column(db.Integer, nullable=False, default=1)
    valor_total = db.Column(db.Numeric(10, 2), nullable=False, default=0.00)
    data_evento = db.Column(db.Date, nullable=False)
    hora_inicio = db.Column(db.Time, nullable=False)
    hora_fim = db.Column(db.Time, nullable=False)
<<<<<<< Updated upstream
    
    id_cliente = db.Column(db.Integer, db.ForeignKey("usuario.id_usuario"), nullable=False)
    id_endereco = db.Column(db.Integer, db.ForeignKey("endereco.id_endereco"), nullable=False)
    id_chefe = db.Column(db.Integer, db.ForeignKey("usuario.id_usuario"), nullable=True)  
=======

    id_cliente = db.Column(db.Integer, db.ForeignKey("usuario.id_usuario"), nullable=False)
    id_endereco = db.Column(db.Integer, db.ForeignKey("endereco.id_endereco"), nullable=False)
    id_chefe = db.Column(db.Integer, db.ForeignKey("usuario.id_usuario"), nullable=True)
>>>>>>> Stashed changes
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
<<<<<<< Updated upstream
# Tabela de associação entre cardápio e bebida 
=======
# Tabela de associação entre cardápio e bebida
>>>>>>> Stashed changes

class bebidaCardapio(db.Model):
    __tablename__ = "bebida_cardapio"

    id_bebida = db.Column(db.Integer, db.ForeignKey("bebida.id_servico"), primary_key=True)
<<<<<<< Updated upstream
    id_cardapio = db.Column(db.Integer, db.ForeignKey("cardapio.id_cardapio"), primary_key=True)    
    
class CardapioPedido(db.Model):
    __tablename__ = "cardapio_pedido"
    
=======
    id_cardapio = db.Column(db.Integer, db.ForeignKey("cardapio.id_cardapio"), primary_key=True)

class CardapioPedido(db.Model):
    __tablename__ = "cardapio_pedido"

>>>>>>> Stashed changes
    id_cardapio = db.Column(db.Integer, db.ForeignKey("cardapio.id_cardapio"), primary_key=True)
    id_pedido = db.Column(db.Integer, db.ForeignKey("pedido.id_pedido"), primary_key=True)
    id_servico = db.Column(db.Integer, db.ForeignKey("servico.id_servico"), primary_key=True)

# ======================================================

# CRUD BEBIDA
def criar_bebida(nome: str, descricao: str, valor_unitario: float):
<<<<<<< Updated upstream
    '''Cria a bebida'''
=======
    """Cria a bebida"""
>>>>>>> Stashed changes
    bebida = Bebida(nome=nome, descricao=descricao, valor_unitario=valor_unitario)
    db.session.add(bebida)
    db.session.commit()
    registrar_log("CRIACAO BEBIDA", f"Usuário criou a bebida {bebida.nome}")
    return bebida

def buscar_bebida_por_id(id_bebida: int) :
<<<<<<< Updated upstream
    '''Busca a bebidada pelo id'''
=======
    """Busca a bebidada pelo id"""
>>>>>>> Stashed changes
    return db.session.get(Bebida, id_bebida)

def buscar_bebida_por_nome(nome_bebida: str):
    """Busca bebida pelo nome"""
<<<<<<< Updated upstream
    
    bebida = db.session.execute(
        db.session.select(Bebida).where(Bebida.nome == nome_bebida)
    ).scalar_one_or_none()
    
=======
    bebida = db.session.execute(
        db.session.select(Bebida).where(Bebida.nome == nome_bebida),
    ).scalar_one_or_none()

>>>>>>> Stashed changes
    if bebida:
        return bebida
    return None

def listar_bebidas():
<<<<<<< Updated upstream
    '''Lista as bebidas disponíveis'''
=======
    """Lista as bebidas disponíveis"""
>>>>>>> Stashed changes
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


<<<<<<< Updated upstream
def atualizar_bebida(id_bebida: int, nome: str = None, descricao: str = None, valor_unitario: float = None):
    '''Atualiza os dados da bebida'''
    bebida = db.session.get(Bebida, id_bebida)
    
    if not bebida:
        return False
    
=======
def atualizar_bebida(id_bebida: int, nome: str | None = None, descricao: str | None = None, valor_unitario: float | None = None):
    """Atualiza os dados da bebida"""
    bebida = db.session.get(Bebida, id_bebida)

    if not bebida:
        return False

>>>>>>> Stashed changes
    if nome is not None:
        bebida.nome = nome
    if descricao is not None:
        bebida.descricao = descricao
    if valor_unitario is not None:
        bebida.valor_unitario = valor_unitario
<<<<<<< Updated upstream
        
=======

>>>>>>> Stashed changes
    db.session.commit()
    registrar_log("ATUALIZACAO BEBIDA", f"Usuário atualizou a bebida {id_bebida}")
    return True

def deletar_bebida(id_bebida: int):
<<<<<<< Updated upstream
    '''Deleta a bebida'''
=======
    """Deleta a bebida"""
>>>>>>> Stashed changes
    bebida = db.session.get(Bebida, id_bebida)
    if not bebida:
        return False
    db.session.delete(bebida)
    db.session.commit()
<<<<<<< Updated upstream
    registrar_log("REMOCAO BEBIDA", f"Usuario deletou bebida {bebida.nome}")        
=======
    registrar_log("REMOCAO BEBIDA", f"Usuario deletou bebida {bebida.nome}")
>>>>>>> Stashed changes

    return True

def associar_bebida_cardapio(id_bebida: int, id_cardapio: int):
    """Associa uma bebida a um cardápio"""
<<<<<<< Updated upstream
    novo_item = bebidaCardapio(id_bebida=id_bebida,id_cardapio=id_cardapio
=======
    novo_item = bebidaCardapio(id_bebida=id_bebida,id_cardapio=id_cardapio,
>>>>>>> Stashed changes
    )
    db.session.add(novo_item)
    db.session.commit()
    registrar_log("CRIACAO BEBIDA_CARDAPIO", f"Usuário associou a bebida {id_bebida} ao cardápio {id_cardapio}")
    return (id_bebida, id_cardapio)

# CRUD - PEDIDO
<<<<<<< Updated upstream
def criar_pedido(id_cliente: int, id_endereco: int , num_convidados: int, valor_total: float, data_evento: str, hora_inicio: str, hora_fim: str, cardapios: list[dict], observacao: str = None, bebidas: list[dict] = None) -> (Pedido | None):
=======
def criar_pedido(id_cliente: int, id_endereco: int , num_convidados: int, valor_total: float, data_evento: str, hora_inicio: str, hora_fim: str, cardapios: list[dict], observacao: str | None = None, bebidas: list[dict] | None = None) -> (Pedido | None):
>>>>>>> Stashed changes
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
<<<<<<< Updated upstream
        
    )
    db.session.add(novo_pedido)
    
    try:
        db.session.flush()
        
=======

    )
    db.session.add(novo_pedido)

    try:
        db.session.flush()

>>>>>>> Stashed changes
        for cardapio in cardapios:
            p_c = CardapioPedido(
                id_cardapio=cardapio["id_cardapio"],
                id_pedido=novo_pedido.id_pedido,
            )
            db.session.add(p_c)

        db.session.flush()
<<<<<<< Updated upstream
    
=======

>>>>>>> Stashed changes
        #verifica se o pedido tem bebida, se tiver adiciona
        if bebidas:
            for item in bebidas:
                p_b = PedidoBebida(
                    id_pedido=novo_pedido.id_pedido,
                    id_bebida=item["id_bebida"],
                    qtd=item["qtd"],
<<<<<<< Updated upstream
                    valor_unitario=item["valor_unitario"]
=======
                    valor_unitario=item["valor_unitario"],
>>>>>>> Stashed changes
                )
                db.session.add(p_b)

        # TODO: adicionar triggers de baixa de estoque

        db.session.commit()
<<<<<<< Updated upstream
        
=======

>>>>>>> Stashed changes
    except IntegrityError:
        db.session.rollback()
        return None

    registrar_log("PEDIDO", f"Pedido {novo_pedido.id_pedido} criado.")
    return novo_pedido

def buscar_pedido_por_id(id_pedido: int):
<<<<<<< Updated upstream
    '''Busca pedido.'''
    return db.session.get(Pedido, id_pedido)

def listar_pedidos_por_cliente(id_cliente: int) :
    '''Lista os pedidos realizados pelo clientre'''
=======
    """Busca pedido."""
    return db.session.get(Pedido, id_pedido)

def listar_pedidos_por_cliente(id_cliente: int) :
    """Lista os pedidos realizados pelo clientre"""
>>>>>>> Stashed changes
    return db.session.query(Pedido).filter_by(id_cliente=id_cliente).all()

def listar_pedidos_periodo(ano:int|str, mes:int|str, dia:int|str, status=None) -> list[Pedido] | None:
    """Retorna todos os pedidos concluidos até certo dia de mês e ano específicos.

    Args:
        ano (int | str): Ano de referencia. Deve ser um dígito. 
        mes (int | str): Mês de referencia. Deve ser um dígito. 
        dia (int | str): Dia de referencia. Deve ser um dígito. 

    Returns:
        list[Pedido] | None: Retorna uma lista vazia caso não existam pedidos no periodo ou None se um dos parâmetros não for dígito. Do contrário, retorna uma lista de objetos Pedido.
<<<<<<< Updated upstream
=======

>>>>>>> Stashed changes
    """
    try:
        ano=int(ano)
        mes=int(mes)
        dia=int(dia)
    except (ValueError, TypeError):
        return None
<<<<<<< Updated upstream
    
    if not 1 <= mes <= 12 or not 1 <= dia <= 31:
        return None
    
    return db.session.execute(
        db.select(Pedido).where(
            Pedido.status==status, 
            extract('month', Pedido.data_evento) == mes, 
            extract('year', Pedido.data_evento) == ano,
            extract('day', Pedido.data_evento) <= dia,
        )
    ).scalars().all()

def listar_pedidos_entre_datas(ano:int|str, mes:int|str, dia:int|str, ano_final:int|str = None, mes_final:int|str = None, dia_final:int|str = None, status='concluido') -> list[Pedido] | None:
=======

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

def listar_pedidos_entre_datas(ano:int|str, mes:int|str, dia:int|str, ano_final:int | str | None = None, mes_final:int | str | None = None, dia_final:int | str | None = None, status="concluido") -> list[Pedido] | None:
>>>>>>> Stashed changes
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
<<<<<<< Updated upstream
    """
    
    from utils import para_data, hoje
    
    if not (ano_final or mes_final or dia_final):
        ano_final=hoje().year
        mes_final=hoje().month
        dia_final=hoje().day 
    
=======

    """
    from utils import hoje, para_data

    if not (ano_final or mes_final or dia_final):
        ano_final=hoje().year
        mes_final=hoje().month
        dia_final=hoje().day

>>>>>>> Stashed changes
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
<<<<<<< Updated upstream
            Pedido.data_evento <= data_fim
        )
=======
            Pedido.data_evento <= data_fim,
        ),
>>>>>>> Stashed changes
    ).scalars().all()

def atualizar_pedido(
    id_pedido: int,
<<<<<<< Updated upstream
    status: str = None,
    confirmado_em: datetime = None,
    id_chefe: int = None,
    observacao: str = None,
    num_convidados: int = None,
    valor_total: float = None):
=======
    status: str | None = None,
    confirmado_em: datetime | None = None,
    id_chefe: int | None = None,
    observacao: str | None = None,
    num_convidados: int | None = None,
    valor_total: float | None = None):
>>>>>>> Stashed changes
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


def deletar_pedido(id_pedido: int):
<<<<<<< Updated upstream
    '''Deleta pedido'''
=======
    """Deleta pedido"""
>>>>>>> Stashed changes
    pedido = db.session.get(Pedido, id_pedido)
    if not pedido:
        return False

    db.session.delete(pedido)
    db.session.commit()
    registrar_log("REMOCAO PEDIDO", f"Pedido {id_pedido} removido do sistema.")
    return True



#PEDIDO_BEBIDA
def adicionar_bebida_ao_pedido(id_pedido: int, id_bebida: int, qtd: int, valor_unitario: float) -> bool:
    pedido = db.session.get(Pedido, id_pedido)
    bebida = db.session.get(Bebida, id_bebida)
<<<<<<< Updated upstream
    
=======

>>>>>>> Stashed changes
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
<<<<<<< Updated upstream
            valor_unitario=valor_unitario
=======
            valor_unitario=valor_unitario,
>>>>>>> Stashed changes
        )
        db.session.add(item)

    db.session.commit()
    return True

def remover_bebida_do_pedido(id_pedido: int, id_bebida: int) -> bool:
    item = db.session.get(PedidoBebida, (id_pedido, id_bebida))
    if not item:
        return False

    db.session.delete(item)
    db.session.commit()
    return True

# CRUD CardapioPedido
def criar_cardapio_pedido(id_cardapio: int, id_pedido: int, id_servico: int) -> (CardapioPedido | None):
    """Relaciona um cardapio a um pedido."""
<<<<<<< Updated upstream
    
    cardapio_pedido=CardapioPedido(id_cardapio, id_pedido, id_servico)
    
    db.session.add(cardapio_pedido)
    
=======
    cardapio_pedido=CardapioPedido(id_cardapio, id_pedido, id_servico)

    db.session.add(cardapio_pedido)

>>>>>>> Stashed changes
    try:
        db.session.commit(cardapio_pedido)
        return cardapio_pedido
    except IntegrityError:
        db.session.rollback()
        return None
<<<<<<< Updated upstream
    
def buscar_cardapios_pedido(id_pedido: int):
    """Retorna todos os cardápios relacionados a um pedido."""
    
    return db.session.execute(
        db.select(CardapioPedido).where(
    CardapioPedido.id_pedido == id_pedido
        )
    ).scalars().all()
    
def deletar_cardapios_pedido(id_pedido: int) -> (bool):
    """Deleta todos os cardápios relacionados a um pedido."""

    try:
        db.session.execute(
            db.delete(CardapioPedido).where(
                CardapioPedido.id_pedido == id_pedido
            )
=======

def buscar_cardapios_pedido(id_pedido: int):
    """Retorna todos os cardápios relacionados a um pedido."""
    return db.session.execute(
        db.select(CardapioPedido).where(
    CardapioPedido.id_pedido == id_pedido,
        ),
    ).scalars().all()

def deletar_cardapios_pedido(id_pedido: int) -> (bool):
    """Deleta todos os cardápios relacionados a um pedido."""
    try:
        db.session.execute(
            db.delete(CardapioPedido).where(
                CardapioPedido.id_pedido == id_pedido,
            ),
>>>>>>> Stashed changes
        )
        db.session.commit()
        return True

    except IntegrityError:
        db.session.rollback()
<<<<<<< Updated upstream
        return False
=======
        return False
>>>>>>> Stashed changes
