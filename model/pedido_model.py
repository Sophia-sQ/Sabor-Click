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

    
    id_cliente = db.Column(db.Integer, db.ForeignKey("pedido.id_pedido"), nullable=False)
    id_endereco = db.Column(db.Integer, db.ForeignKey("endereco.id_endereco"), nullable=False) #FIXME: eu n sei se essa referencia ta certa e tem q importar a tabela
    id_chefe = db.Column(db.Integer, db.ForeignKey("pedido.id_pedido"), nullable=True)  
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
    
def buscar_pedido_por_id(id_pedido:int):
    pedido=db.session.get(pedido, id_pedido)
    
    return pedido

def atualizar_pedido(id_pedido:int, status:str = None, confirmado_em:str = None, id_chefe:int=None):
    """Atualiza dados do pedido"""
    
    pedido=db.session.get(pedido,id_pedido)
    if not pedido:
        return False
    
    if status:
        pedido.status = status
    if confirmado_em: 
        pedido.confirmado_em = confirmado_em
    if id_chefe:
        pedido.id_chefe = id_chefe
   
    db.session.commit()
    registrar_log("ATUALIZACAO", f"Dados cadastrais do {id_pedido} atualizados pelo usuário {pedido.id_cliente}")        
    return True