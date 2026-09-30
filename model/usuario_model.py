# Contém as tabelas: NivelPermissao, Usuario e LogAtividade
from datetime import datetime
from database import db

# Tabela Nível de permissão do usuário
class NivelPermissao(db.Model):
    __tablename__ = "nivel_permissao"

    id_permissao = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nome = db.Column(db.String(20), unique=True, nullable=False)  # Escolha: cliente, chef, adm

# Tabela do usuário
class Usuario(db.Model):
    __tablename__ = "usuario"

    id_usuario = db.Column(db.Integer, primary_key=True, autoincrement=True)
    cpf = db.Column(db.String(11), unique=True, nullable=False) 
    nome = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    senha_hash = db.Column(db.String(255), nullable=False)
    criado_em = db.Column(db.DateTime, default=datetime.utcnow)
    id_permissao = db.Column(db.Integer, db.ForeignKey("nivel_permissao.id_permissao"), nullable=False)

# Tabela das atividades realizadas pelo usuário dentro do site
class LogAtividade(db.Model):
    __tablename__ = "log_atividade"

    id_atividade = db.Column(db.Integer, primary_key=True, autoincrement=True)
    realizado_em = db.Column(db.DateTime, default=datetime.utcnow) # Se vazio cria data e hora padrão
    acao = db.Column(db.String(45), nullable=False)
    descricao = db.Column(db.Text, nullable=True)  
    id_usuario = db.Column(db.Integer, db.ForeignKey("usuario.id_usuario"), nullable=False)