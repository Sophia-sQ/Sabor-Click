# Contém a tabela: Pedido
from model.usuario_model import registrar_log

from datetime import datetime
from database import db

class Pedido(db.Model):
    __tablename__ = "pedido"

    id_pedido = db.Column(db.Integer, primary_key=True, autoincrement=True)
    observacao = db.Column(db.Text, nullable=True)  # Opcional
    status = db.Column(
        db.Enum("aguardando", "confirmado", "em preparo", "concluído", "cancelado", name="status_pedido"),default="aguardando",nullable=False)
    confirmado_em = db.Column(db.DateTime, nullable=True)
    criado_em = db.Column(db.DateTime, default=datetime.now(datetime.timezone.utc), nullable=False)
    num_convidados = db.Column(db.Integer, nullable=False, default=1)
    valor_total = db.Column(db.Numeric(10, 2), nullable=False, default=0.00)
    
    id_cliente = db.Column(db.Integer, db.ForeignKey("usuario.id_usuario"), nullable=False)
    id_endereco = db.Column(db.Integer, db.ForeignKey("endereco.id_endereco"), nullable=False) #FIXME: eu n sei se essa referencia ta certa e tem q importar a tabela
    id_chefe = db.Column(db.Integer, db.ForeignKey("usuario.id_usuario"), nullable=True)  
    id_servico = db.Column(db.Integer, db.ForeignKey("servico.id_servico"), nullable=False)
    id_cardapio = db.Column(db.Integer, db.ForeignKey("cardapio.id_cardapio"), nullable=False)

    __table_args__ = (
        db.CheckConstraint("num_convidados > 0", name="ck_pedido_convidados"),
        db.CheckConstraint("valor_total >= 0", name="ck_pedido_valor"),
    )


class Bebida(db.Model):
    __tablename__ = "bebida"

    id_bebida = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nome = db.Column(db.String(60), nullable=False)
    descricao = db.Column(db.Text, nullable=False)
    qtd = db.Column(db.Integer, default=0, nullable=False)
    qtd_min = db.Column(db.Integer, default=0, nullable=False)

    __table_args__ = (
        db.CheckConstraint("qtd >= 0 AND qtd_min >= 0", name="ck_bebida_qtd"),
    )


class PedidoBebida(db.Model):
    __tablename__ = "pedido_bebida"

    
    id_pedido = db.Column(db.Integer, db.ForeignKey("pedido.id_pedido"), primary_key=True)
    id_bebida = db.Column(db.Integer, db.ForeignKey("bebida.id_bebida"), primary_key=True)
    
    qtd = db.Column(db.Integer, nullable=False)
    valor_unitario = db.Column(db.Numeric(10, 2), nullable=False)

    __table_args__ = (
        db.CheckConstraint("qtd > 0", name="ck_pedido_bebida_qtd"),
    )
    
# CRUYD BEBIDA

def criar_bebida(nome: str, descricao: str, qtd: int = 0, qtd_min: int = 0):
    '''Cria a bebida'''
    bebida = Bebida(nome=nome, descricao=descricao, qtd=qtd, qtd_min=qtd_min)
    db.session.add(bebida)
    db.session.commit()
    return bebida

def buscar_bebida_por_id(id_bebida: int) :
    '''Busca a bebidada pelo id'''
    return db.session.get(Bebida, id_bebida)

def listar_bebidas():
    '''Lista as bebidas disponíveis'''
    return db.session.query(Bebida).all()


def atualizar_bebida(id_bebida: int, novo_nome: str = None, novo_preco: float = None):
    '''Atualiza os dados da bebida'''
    bebida = db.session.get(Bebida, id_bebida)
    
    if not bebida:
        return False
    
    if novo_nome is not None:
        bebida.nome = novo_nome
        
    if novo_preco is not None:
        bebida.preco = novo_preco
        
    db.session.commit()
    return True


def deletar_bebida(id_bebida: int):
    '''Deleta a bebida'''
    bebida = db.session.get(Bebida, id_bebida)
    if not bebida:
        return False
    db.session.delete(bebida)
    db.session.commit()
    registrar_log("REMOCAO BEBIDA", f"Usuario deletou bebida {bebida.nome}")        

    return True



# CRUD - PEDIDO

def criar_pedido(id_cliente: int,id_endereco: int,id_servico: int,id_cardapio: int,num_convidados: int,valor_total: float, observacao: str = None,bebidas: list[dict] = None):
    """Cria um pedido e associa bebidas a ele caso tenha """
    novo_pedido = Pedido(
        id_cliente=id_cliente,
        id_endereco=id_endereco,
        id_servico=id_servico,
        id_cardapio=id_cardapio,
        num_convidados=num_convidados,
        valor_total=valor_total,
        observacao=observacao
    )
    db.session.add(novo_pedido)
    db.session.flush() 
    #verifica se o pedido tem bebida, se tiver adiciona
    if bebidas:
        for item in bebidas:
            p_b = PedidoBebida(
                id_pedido=novo_pedido.id_pedido,
                id_bebida=item["id_bebida"],
                qtd=item["qtd"],
                valor_unitario=item["valor_unitario"]
            )
            db.session.add(p_b)

    db.session.commit()
    registrar_log("PEDIDO", f"Pedido {novo_pedido.id_pedido} criado pelo cliente {id_cliente}")
    return novo_pedido


def buscar_pedido_por_id(id_pedido: int):
    '''Busca pedido '''
    return db.session.get(Pedido, id_pedido)


def listar_pedidos_por_cliente(id_cliente: int) :
    '''Lista os pedidos realizados pelo clientre'''
    return db.session.query(Pedido).filter_by(id_cliente=id_cliente).all()


def atualizar_pedido(
    id_pedido: int,
    status: str = None,
    confirmado_em: datetime = None,
    id_chefe: int = None,
    observacao: str = None,
    num_convidados: int = None,
    valor_total: float = None):
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

    db.session.commit()
    registrar_log("ATUALIZACAO PEDIDO", f"Dados do pedido {id_pedido} atualizados.")
    return True


def deletar_pedido(id_pedido: int):
    '''Deleta pedido'''
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
            valor_unitario=valor_unitario
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