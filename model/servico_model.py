# Contém as tabelas : Bancada, serviço e cardápio

from database import db

class Bancada(db.Model):
    __tablename__ = "bancada"

    id_bancada = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nome = db.Column(db.String(60), nullable=False)
    descricao = db.Column(db.Text, nullable=False)


class Servico(db.Model):
    __tablename__ = "servico"

    id_servico = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nome = db.Column(db.String(60), unique=True, nullable=False)
    descricao = db.Column(db.Text, nullable=False)

# Tabela de associação entre bancada e o serviço 
class ServicoBancada(db.Model):
    __tablename__ = "servico_bancada"

    id_servico = db.Column(db.Integer, db.ForeignKey("servico.id_servico"), primary_key=True)
    id_bancada = db.Column(db.Integer, db.ForeignKey("bancada.id_bancada"), primary_key=True)

class Cardapio(db.Model):
    __tablename__ = "cardapio"

    id_cardapio = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nome = db.Column(db.String(60), nullable=False)
    descricao = db.Column(db.Text, nullable=False)
    preco_base = db.Column(db.Numeric(10, 2), nullable=False)

    __table_args__ = (
        db.CheckConstraint("preco_base >= 0", name="ck_cardapio_preco"),
    )
# Tabela de associação entre cardápio e serviço, pois existem serviços com o mesmo cardápio 

class ServicoCardapio(db.Model):
    __tablename__ = "servico_cardapio"

    id_servico = db.Column(db.Integer, db.ForeignKey("servico.id_servico"), primary_key=True)
    id_cardapio = db.Column(db.Integer, db.ForeignKey("cardapio.id_cardapio"), primary_key=True)
    descricao = db.Column(db.Text, nullable=True)  