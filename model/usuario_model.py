# Contém as tabelas: NivelPermissao, Usuario e LogAtividade
from datetime import datetime
from database import db

from werkzeug.security import check_password_hash,generate_password_hash

# Tabela Nível de permissão do usuário
class NivelPermissao(db.Model):
    __tablename__ = "nivel_permissao"

    """Certificar que os id dos cargos estão de acordo com a Enum cargos em cargos.py"""
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
    ativo= db.Column(db.Boolean, default=True, nullable=False)
    criado_em = db.Column(db.DateTime, default=datetime.now(datetime.timezone.utc))
    id_permissao = db.Column(db.Integer, db.ForeignKey("nivel_permissao.id_permissao"), nullable=False)

# Tabela das atividades realizadas pelo usuário dentro do site
class LogAtividade(db.Model):
    __tablename__ = "log_atividade"

    id_atividade = db.Column(db.Integer, primary_key=True, autoincrement=True)
    realizado_em = db.Column(db.DateTime, default=datetime.now(datetime.timezone.utc)) # Se vazio cria data e hora padrão
    acao = db.Column(db.String(45), nullable=False)
    descricao = db.Column(db.Text, nullable=True)  
    id_usuario = db.Column(db.Integer, db.ForeignKey("usuario.id_usuario"), nullable=False)
    
def criar_usuario(cpf:str, nome:str, email:str, senha:str, id_permissao:int):
   """Cria novo usuario"""
   senha_criptografada=generate_password_hash(senha)
   novo_usuario=Usuario(cpf=cpf, nome=nome, email=email, senha_hash=senha_criptografada,id_permissao=id_permissao)
   db.session.add(novo_usuario)
   db.session.commit()
   registrar_log(novo_usuario.id_usuario, "CADASTRO", "Usuario cadastrado")
   return novo_usuario.id_usuario

def registrar_log(id_usuario: int, acao:str, descricao: str = None):
    """Registra uma atividade """
    log= LogAtividade(id_usuario=id_usuario, acao=acao, descricao=descricao )
    db.session.add(log)
    db.session.commit()
def buscar_usuario_para_login(cpf:str, senha:str):
    """Busca um usuário pelo CPF e senha e retorna o id.
    
    Se usuário nao existir, retorna None"""
    
    # retorna apenas uma entrada ou None 
    usuario = db.session.execute(
        db.select(Usuario).where(Usuario.cpf == cpf) # Não pode utilizar check_password_hash em where
    ).scalar_one_or_none()

    
    if usuario and check_password_hash(usuario.senha_hash, senha):
        return usuario.id_usuario
    
    return None
    
def buscar_usuario_por_id(id:int):
    """Busca um usuário pelo id e retorna um result object??????????????????????."""
    
    # retorna apenas uma entrada ou None 
    usuario = db.session.execute(db.select(Usuario).where(Usuario.id_usuario == id)).scalar_one_or_none()
    
    if usuario:
        return usuario
    
    return None
    
def buscar_usuario_por_cpf(cpf:str):
    """Busca um usuário pelo CPF e retorna um dicionario/JSON.
    
    Retorna id, nome, email e cargo do usuário"""
    
    # retorna apenas uma entrada ou None 
    usuario = db.session.execute(db.select(Usuario).where(Usuario.cpf == cpf)).scalar_one_or_none()
    
    if usuario:
        return {'id': usuario.id_usuario,
                'nome': usuario.nome,
                'email': usuario.email,
                'cargo': db.session.execute(
                    db.select(NivelPermissao).where(NivelPermissao.id_permissao == Usuario.id_permissao)
                ).scalar_one() }
    
    return None
    
def buscar_todos_usuarios():
    """Retorna todos os usuários registrados como uma lista.
    
    retorna dados sensíveis em texto criptografado."""
    
    usuarios = db.session.execute(db.select(Usuario)).scalars().all()
    
    if usuarios:
        return usuarios
    
    return None

def atualizar_usuario(id_usuario:int, nome:str = None, email:str= None,nova_senha:str=None):
    """Atualiza o usuário"""
    usuario=db.session.get(Usuario,id_usuario)
    if not usuario:
        return False
    if nome:
        usuario.nome= nome
    if email: 
        usuario.email= email
    if nova_senha:
        usuario.senha_hash = generate_password_hash(nova_senha)
   
    db.session.commit()
    registrar_log(id_usuario, "ATUALIZACAO", "Dados cadastrais atualizados pelo usuário")        
    return True

def deletar_usuario(id_usuario: int, soft_delete:bool= True):
    """Deleta ou desativa"""
    usuario=db.session.get(Usuario,id_usuario)
    if not usuario:
        return False
    if soft_delete: #Desativa
        usuario.ativo=False
        db.session.commit()
        registrar_log(id_usuario,"DESATIVACAO", "Usuário desativado")

    else: #Deleta
        db.session.delete(usuario)
        db.session.commit()
    return True     
def reativar_usuario   (id_usuario: int):
    """Reativa conta de usuario inativo"""
    usuario=db.session.get(Usuario,id_usuario)
    if not usuario:
        return False
    usuario.ativo=True
    db.session.commit()
    registrar_log(id_usuario,"REATIVACAO", "Conta reativada")
    return True