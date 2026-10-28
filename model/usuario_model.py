# Contém as tabelas: NivelPermissao, Usuario e LogAtividade
from datetime import datetime, timezone, timedelta
from database import db
from sqlalchemy.exc import IntegrityError


from flask import session
from werkzeug.security import check_password_hash,generate_password_hash

from security import gerar_hmac, criptografar

from zoneinfo import ZoneInfo
from utils import hoje

# Tabela Nível de permissão do usuário
class NivelPermissao(db.Model):
    __tablename__ = "nivel_permissao"

    """Certificar que os id dos cargos estão de acordo com a Enum cargos em cargos.py"""
    id_permissao = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(20), unique=True, nullable=False)  # Escolha: cliente, chefe, admin

# Tabela do usuário
class Usuario(db.Model):
    __tablename__ = "usuario"

    id_usuario = db.Column(db.Integer, primary_key=True, autoincrement=True)
    #cpf = db.Column(db.Text, nullable=False) 
    cpf_criptografado = db.Column(db.Text, nullable=False) 
    cpf_hmac = db.Column(db.String(64), unique=True, nullable=False) 
    nome = db.Column(db.String(100), nullable=False)
    email_criptografado = db.Column(db.Text, nullable=False)
    email_hmac = db.Column(db.String(64), unique=True, nullable=False)
    senha_hash = db.Column(db.String(255), nullable=False)
    ativo = db.Column(db.Boolean, default=True, nullable=False)
    criado_em = db.Column(db.DateTime, default=lambda: datetime.now(ZoneInfo("America/Sao_Paulo")), nullable=False)
    id_permissao = db.Column(db.Integer, db.ForeignKey("nivel_permissao.id_permissao"), nullable=False)
    
# Tabela de endereços do usuário
class Endereco(db.Model):
    __tablename__ = "endereco"

    id_endereco = db.Column(db.Integer, primary_key=True, autoincrement=True)
    id_usuario = db.Column(db.Integer, db.ForeignKey("usuario.id_usuario")) 
    nome = db.Column(db.String(150), nullable=False)
    logradouro = db.Column(db.String(150), nullable=False)
    numero = db.Column(db.String(20), nullable=False)
    complemento = db.Column(db.String(100), nullable=True)  # Opcional
    bairro = db.Column(db.String(100), nullable=False)
    cidade = db.Column(db.String(100), nullable=False)
    cep = db.Column(db.String(9), nullable=False)

# Tabela das atividades realizadas pelo usuário dentro do site
class LogAtividade(db.Model):
    __tablename__ = "log_atividade"

    id_atividade = db.Column(db.Integer, primary_key=True, autoincrement=True)
    realizado_em = db.Column(db.DateTime, default=lambda: datetime.now(ZoneInfo("America/Sao_Paulo")), nullable=False) # Se vazio cria data e hora padrão
    acao = db.Column(db.String(45), nullable=False)
    descricao = db.Column(db.Text, nullable=True)  
    id_usuario = db.Column(db.Integer, db.ForeignKey("usuario.id_usuario"), nullable=False)
    
# Tabelas de tokens
class Token(db.Model):
    __tablename__ = "token"

    id_token = db.Column(db.Integer, primary_key=True, autoincrement=True)
    codigo_hash = db.Column(db.Text, nullable=False)
    ativo = db.Column(db.Boolean, nullable=False, default=True)
    tentativas = db.Column(db.Integer, nullable=False, default=0)
    id_usuario = db.Column(db.Integer,db.ForeignKey("usuario.id_usuario"),nullable=False)
    criado_em = db.Column(db.DateTime(timezone=True),default=hoje,nullable=False)
    
# funções de consulta   
def criar_token(hash: str, id_usuario: int) -> Token | None:
    token=Token(codigo_hash=hash, id_usuario=id_usuario)
    db.session.add(token)

    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return None
    return token

def deletar_token(id_token: int):
    """Deleta token."""
    token = db.session.get(Token, id_token)
    if not token:
        return False
    db.session.delete(token)
    db.session.commit()
    return True

def buscar_token(id_usuario: int, insercao: datetime) -> Token | None:
    """Busca o token ativo mais recente e verifica a validade."""

    token = db.session.execute(
        db.select(Token)
        .where(
            Token.id_usuario == id_usuario,
            Token.ativo.is_(True)
        )
        .order_by(Token.criado_em.desc())
    ).scalars().first()

    if token is None:
        return None

    criado_em = token.criado_em
    fuso = hoje().tzinfo

    if criado_em.tzinfo is None:
        criado_em = criado_em.replace(tzinfo=fuso)

    if insercao.tzinfo is None:
        insercao = insercao.replace(tzinfo=fuso)

    if insercao >= criado_em + timedelta(minutes=10):
        token.ativo = False
        db.session.commit()
        return None

    return token

def criar_cargo(id_permissao:int, nome:str):
    """Cria novo cargo.
    
    Caso o cargo já exista, retorna None, senão retorna a nova instância."""
   
    cargo=NivelPermissao(id_permissao=id_permissao, nome=nome)
    db.session.add(cargo)
    
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return None
    
    registrar_log("NOVO CARGO", f"Novo cargo {nome} criado.")
    return cargo

def buscar_permissao_por_nome(nome_permissao: str) -> (NivelPermissao | None):
    """Procura uma permissão no banco de dado de nome equivalente.

    Args:
        nome_permissao (str): nome da permissão alvo.

    Returns:
        NivelPermissao: Instância da tabela NivelPermissao.
    """
    
    permissao = db.session.execute(
        db.session.select(NivelPermissao).where(NivelPermissao.nome == nome_permissao.lower())
    ).scalar_one_or_none()

    if permissao:
        return permissao
    return None

def atualizar_permissao(id_cargo: int, nome: str) -> (NivelPermissao | None):
    """Procura uma permissão no banco de dado de nome equivalente.

    Args:
        nome_permissao (str): nome da permissão alvo.

    Returns:
        NivelPermissao: Instância da tabela NivelPermissao.
    """
    
    cargo=db.session.get(NivelPermissao, id_cargo)
    if not cargo:
        return None
    
    if nome:
        cargo_conflitante=buscar_permissao_por_nome(nome)
        cargo.nome, cargo_conflitante.nome = nome, cargo.nome
        
    db.session.commit()
    registrar_log("ATUALIZACAO", f"Cargo {id_cargo} atualizado.")        
    return cargo

def criar_usuario(cpf:str, nome:str, email:str, senha:str, id_permissao:int):
   """Cria novo usuario."""
   
   cpf_criptografado=criptografar(cpf)
   cpf_hmac=gerar_hmac(cpf=cpf)
   
   email_criptografado=criptografar(email)
   email_hmac=gerar_hmac(email=email)
   
   senha_criptografada=generate_password_hash(senha)
   
   novo_usuario=Usuario(cpf_criptografado=cpf_criptografado, cpf_hmac=cpf_hmac, nome=nome, email_criptografado=email_criptografado, email_hmac=email_hmac, senha_hash=senha_criptografada,id_permissao=id_permissao)
   
   db.session.add(novo_usuario)
   try:
        db.session.commit()
   except IntegrityError:
       db.session.rollback()
       return None
   cargo = db.session.get(NivelPermissao, id_permissao).nome
   registrar_log("CADASTRO", f"Novo usuário {cargo} {nome} cadastrado.")
   return novo_usuario.id_usuario

def registrar_log(acao:str, descricao: str = None):
    """Registra uma atividade."""
    
    log = LogAtividade(id_usuario=session.get('id'), acao=acao, descricao=descricao )
    db.session.add(log)
    db.session.commit()
    return True
    
def buscar_usuario_para_login(credencial:str, senha:str):
    """Busca um usuário pelo CPF ou email e senha e retorna o id.
    
    Se usuário nao existir, retorna None"""
    
    # retorna apenas uma entrada ou None 
    
    if '@' in credencial:
        credencial_hmac=gerar_hmac(email=credencial)
        campo=Usuario.email_hmac
    else:
        credencial_hmac=gerar_hmac(cpf=credencial)
        campo=Usuario.cpf_hmac
        
    usuario = db.session.execute(
        db.select(Usuario).where(campo == credencial_hmac, Usuario.ativo.is_(True))
    ).scalar_one_or_none()

    
    if usuario and check_password_hash(usuario.senha_hash, senha):
        return usuario.id_usuario
    
    return None
    
def buscar_usuario_por_id(id:int):
    """Busca um usuário pelo id e retorna o objeto usuário equivalente."""
    
    # retorna apenas uma entrada ou None 
    usuario = db.session.execute(db.select(Usuario).where(Usuario.id_usuario == id, Usuario.ativo.is_(True))).scalar_one_or_none()
    
    if usuario:
        return usuario
    
    return None
    
def buscar_funcionarios(busca: str = "") -> list[Usuario]:
    """Busca funcionários pelo nome.

    Args:
        busca (str, optional): nome buscado. Defaults to "".

    Returns:
        list[Usuario]: todos os funcionários que se enquadram nos critérios de busca.
    """
    
    # % significa que pode haver quaisquer caracteres entre a busca
    termo = f"%{busca.strip()}%"
    
    from model.cargos import Cargo
    
    return db.session.execute(
        db.select(Usuario).where(
            Usuario.nome.like(termo), 
            Usuario.id_permissao==Cargo.CHEFE.value
            ).order_by(Usuario.nome.collate("NOCASE"))
    ).scalars().all()


def atualizar_usuario(id_usuario: int, nome: str = None, email: str = None, cpf: str = None, nova_senha: str = None):
    """Atualiza o usuário."""

    usuario = db.session.get(Usuario, id_usuario)
    if not usuario:
        return False
    if nome:
        usuario.nome = nome
    if email:
        usuario.email_criptografado = criptografar(email)
        usuario.email_hmac = gerar_hmac(email=email)   # keyword: usa EMAIL_LOOKUP_HMAC_SECRET
    if cpf:
        usuario.cpf_criptografado = criptografar(cpf)
        usuario.cpf_hmac = gerar_hmac(cpf=cpf)          # keyword: usa CPF_LOOKUP_HMAC_SECRET
    if nova_senha:
        usuario.senha_hash = generate_password_hash(nova_senha)

    db.session.commit()
    registrar_log("ATUALIZACAO", f"Dados cadastrais atualizados pelo usuário {id_usuario}")
    return True


def deletar_usuario(id_usuario: int, soft_delete:bool = True):
    """Deleta ou desativa"""
    usuario=db.session.get(Usuario,id_usuario)
    
    if not usuario:
        return False
    
    if soft_delete: #Desativa
        usuario.ativo=False
        db.session.commit()
        registrar_log("DESATIVACAO", f"Usuário {id_usuario} desativado")
    else: #Deleta
        db.session.delete(usuario)
        db.session.commit()
    
    return True     

def reativar_usuario (id_usuario: int):
    """Reativa conta de usuario inativo"""
    
    usuario=db.session.get(Usuario,id_usuario)
    
    if not usuario:
        return False
    
    usuario.ativo=True
    db.session.commit()
    registrar_log("REATIVACAO", f"Conta do usuário {id_usuario} reativada")
    
    return True

def adicionar_endereco(nome: str, logradouro: str, numero: str, complemento: str, bairro: str, cidade: str, cep: str) -> (Endereco | None):
    """Adiciona novo endereço para o cliente."""
    
    endereco=Endereco(id_usuario=session.get("id"), nome=nome, logradouro=logradouro, numero=int(numero), complemento=complemento, bairro=bairro, cidade=cidade, cep=cep)
    db.session.add(endereco)
    
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return None
    
    registrar_log("NOVO ENDERECO", f"Novo endereco no id {endereco.id_endereco} criado.")
    return endereco

def buscar_enderco_por_usuario (id_usuario: int) -> list[Endereco] | None:
    """Busca todos os endereços de um usuário.

    Args:
        id_usuario (int): id do usuário.

    Returns:
        list: Todos os endereços do usuário.
    """
    
    enderecos=db.session.execute(
        db.select(Endereco).where(Endereco.id_usuario==id_usuario)
    ).scalars().all()
    
    if not enderecos:
        return None
    
    return enderecos

def buscar_enderco_por_id (id_endereco: int) -> Endereco | None:
    """Busca um endereço a partir do seu id.

    Args:
        id_endereco (int): id do endereco.

    Returns:
        Endereco: Instância relativa ao id.
    """
    
    endereco=db.session.get(Endereco, id_endereco)
    
    if not endereco:
        return None
    
    return endereco

def buscar_endereco_por_id(id_endereco: int) -> (Endereco | None):
    """Busca um endereço pelo id."""
    return db.session.get(Endereco, id_endereco)

def listar_enderecos_do_usuario(id_usuario: int) -> list[Endereco]:
    """Lista todos os endereços de um usuário. Retorna lista vazia se não houver."""
    return db.session.execute(
        db.select(Endereco).where(Endereco.id_usuario == id_usuario)
    ).scalars().all()

def atualizar_endereco(id_endereco: int, nome: str = None, logradouro: str = None, numero: str = None,
                       complemento: str = None, bairro: str = None, cidade: str = None, cep: str = None) -> bool:
    """Atualiza os dados de um endereço. Campos None não são alterados."""

    endereco = db.session.get(Endereco, id_endereco)
    if not endereco:
        return False

    if nome:
        endereco.nome = nome
    if logradouro:
        endereco.logradouro = logradouro
    if numero:
        endereco.numero = numero
    if complemento is not None:        # permite limpar o complemento (opcional)
        endereco.complemento = complemento
    if bairro:
        endereco.bairro = bairro
    if cidade:
        endereco.cidade = cidade
    if cep:
        endereco.cep = cep

    db.session.commit()
    registrar_log("ATUALIZACAO ENDERECO", f"Endereço {id_endereco} atualizado.")
    return True

def deletar_endereco(id_endereco: int) -> bool:
    """Deleta um endereço."""

    endereco = db.session.get(Endereco, id_endereco)
    if not endereco:
        return False

    db.session.delete(endereco)
    db.session.commit()
    registrar_log("REMOCAO ENDERECO", f"Endereço {id_endereco} removido.")
    return True

def buscar_log_por_id(id_atividade: int):
    """Busca um registro de atividade pelo id."""
    return db.session.get(LogAtividade, id_atividade)

def listar_logs(busca: str = "") -> list[LogAtividade]:
    """Lista os registros de atividade, do mais recente para o mais antigo.

    Args:
        busca (str, optional): filtra pela ação (correspondência parcial). Defaults to "".

    Returns:
        list[LogAtividade]: registros de atividade. Lista vazia se não houver.
    """
    stmt = db.select(LogAtividade)

    termo = busca.strip()
    if termo:
        stmt = stmt.where(LogAtividade.acao.like(f"%{termo}%"))

    stmt = stmt.order_by(LogAtividade.realizado_em.desc())

    return db.session.execute(stmt).scalars().all()

def deletar_log(id_atividade: int):
    """Deleta um registro de atividade."""
    log = db.session.get(LogAtividade, id_atividade)
    if not log:
        return False
    db.session.delete(log)
    db.session.commit()
    return True
