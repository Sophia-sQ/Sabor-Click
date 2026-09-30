# Contém a tabela: Pedido

from datetime import datetime
from database import db

class Pedido(db.Model):
    __tablename__ = "pedido"

    id_pedido = db.Column(db.Integer, primary_key=True, autoincrement=True)
    logradouro = db.Column(db.String(150), nullable=False)
    numero = db.Column(db.String(20), nullable=False)
    complemento = db.Column(db.String(100), nullable=True)  # Opcional
    bairro = db.Column(db.String(100), nullable=False)
    cidade = db.Column(db.String(100), nullable=False)
    cep = db.Column(db.String(9), nullable=False)
    observacao = db.Column(db.Text, nullable=True)  # Opcional
    status = db.Column(
        db.Enum("aguardando", "confirmado", "em preparo", "concluído", "cancelado", name="status_pedido"),default="aguardando",nullable=False)
    confirmado_em = db.Column(db.DateTime, nullable=True)
    criado_em = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    
    id_cliente = db.Column(db.Integer, db.ForeignKey("usuario.id_usuario"), nullable=False)
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