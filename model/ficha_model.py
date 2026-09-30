from datetime import datetime
from database import db

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