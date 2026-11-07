"""Modelos e operações de usuários, permissões, endereços, tokens e logs."""
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from database import db, Base
from sqlalchemy.exc import IntegrityError

from flask import session
from werkzeug.security import check_password_hash,generate_password_hash

from security import gerar_hmac, criptografar

from utils import hoje

# Tabela Nível de permissão do usuário
class NivelPermissao(db.Model):
    """Nível de permissão (cargo) de um usuário."""
    __tablename__ = "nivel_permissao"

    """Certificar que os id dos cargos estão de acordo com a Enum cargos em cargos.py"""
    id_permissao = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(20), unique=True, nullable=False)  # Escolha: cliente, chefe, admin

    def __init__(self, id_permissao: int, nome: str):
        self.id_permissao = id_permissao
        self.nome = nome

# Tabela do usuário
class Usuario(db.Model):
    """Usuário do sistema, com dados sensíveis criptografados e indexados por HMAC."""
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
    salario = db.Column(db.Integer, nullable=True, default=0)
    
    def __init__(self, cpf_criptografado: str, cpf_hmac: str, nome: str,
                 email_criptografado: str, email_hmac: str, senha_hash: str,
                 id_permissao: int, ativo: bool = True,
                 criado_em=None, salario: int = 0):
        self.cpf_criptografado = cpf_criptografado
        self.cpf_hmac = cpf_hmac
        self.nome = nome
        self.email_criptografado = email_criptografado
        self.email_hmac = email_hmac
        self.senha_hash = senha_hash
        self.id_permissao = id_permissao
        self.ativo = ativo
        if criado_em is not None:
            self.criado_em = criado_em
        self.salario = salario
    
# Tabela de endereços do usuário
class Endereco(db.Model):
    """Endereço cadastrado por um usuário."""
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
    """Registro de uma atividade realizada por um usuário (trilha de auditoria)."""
    __tablename__ = "log_atividade"

    id_atividade = db.Column(db.Integer, primary_key=True, autoincrement=True)
    realizado_em = db.Column(db.DateTime, default=lambda: datetime.now(ZoneInfo("America/Sao_Paulo")), nullable=False) # Se vazio cria data e hora padrão
    acao = db.Column(db.String(45), nullable=False)
    descricao = db.Column(db.Text, nullable=True)
    id_usuario = db.Column(db.Integer, db.ForeignKey("usuario.id_usuario"), nullable=False)

    def __init__(self, acao: str, id_usuario: int,
                 descricao: str = None, realizado_em=None):
        self.acao = acao
        self.id_usuario = id_usuario
        self.descricao = descricao
        if realizado_em is not None:
            self.realizado_em = realizado_em

# Tabelas de tokens
class Token(db.Model):
    """Token de verificação (código de uso único) associado a um usuário."""

    __tablename__ = "token"

    id_token = db.Column(db.Integer, primary_key=True, autoincrement=True)
    codigo_hash = db.Column(db.Text, nullable=False)
    ativo = db.Column(db.Boolean, nullable=False, default=True)
    tentativas = db.Column(db.Integer, nullable=False, default=0)
    id_usuario = db.Column(db.Integer,db.ForeignKey("usuario.id_usuario"),nullable=False)
    criado_em = db.Column(db.DateTime(timezone=True),default=hoje,nullable=False)

    def __init__(self, codigo_hash: str, id_usuario: int,
                 ativo: bool = True, tentativas: int = 0, criado_em=None):
        self.codigo_hash = codigo_hash
        self.id_usuario = id_usuario
        self.ativo = ativo
        self.tentativas = tentativas
        if criado_em is not None:
            self.criado_em = criado_em

# funções de consulta
def criar_token(hash: str, id_usuario: int) -> Token | None:
    """Cria e persiste um token de verificação para um usuário.

    Args:
        hash (str): hash do código de verificação.
        id_usuario (int): identificador do usuário dono do token.

    Returns:
        Token | None: o token criado; None em caso de violação de integridade.
    """
    token=Token(codigo_hash=hash, id_usuario=id_usuario)
    db.session.add(token)

    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return None
    return token

def deletar_token(id_token: int) -> bool:
    """Remove um token pelo id. Retorna False se não existir."""

    token = db.session.get(Token, id_token)
    if not token:
        return False
    db.session.delete(token)
    db.session.commit()
    return True

def buscar_token(id_usuario: int, insercao: datetime) -> Token | None:
    """Busca o token ativo mais recente de um usuário e valida a expiração.

    Considera o token expirado após 10 minutos da criação; nesse caso, o
    desativa e retorna None.

    Args:
        id_usuario (int): identificador do usuário.
        insercao (datetime): momento usado como referência para checar a
            expiração (normalmente o instante atual).

    Returns:
        Token | None: token válido e ativo; None se não houver ou se expirado.
    """""
    token = db.session.execute(
        db.select(Token)
        .where(
            Token.id_usuario == id_usuario,
            Token.ativo.is_(True),
        )
        .order_by(Token.criado_em.desc()),
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

def criar_cargo(id_permissao: int, nome: str) -> NivelPermissao | None:
    """Cria um novo cargo (nível de permissão).

    Args:
        id_permissao (int): identificador do cargo.
        nome (str): nome do cargo.

    Returns:
        NivelPermissao | None: o cargo criado; None se já existir (violação de
        integridade).
    """
    cargo=NivelPermissao(id_permissao=id_permissao, nome=nome)
    db.session.add(cargo)

    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return None
    registrar_log("NOVO CARGO", f"Novo cargo {nome} criado.")
    return cargo

def buscar_permissao_por_nome(nome_permissao: str) -> NivelPermissao | None:
    """Busca uma permissão pelo nome (comparação em minúsculas).

    Args:
        nome_permissao (str): nome da permissão procurada.

    Returns:
        NivelPermissao | None: a permissão encontrada ou None.
    """
    permissao = db.session.execute(
        db.session.select(NivelPermissao).where(NivelPermissao.nome == nome_permissao.lower()),
    ).scalar_one_or_none()

    if permissao:
        return permissao
    return None

def atualizar_permissao(id_cargo: int, nome: str) -> NivelPermissao | None:
    """Atualiza o nome de um cargo, trocando-o com o do cargo que já usa o nome.

    Args:
        id_cargo (int): identificador do cargo a atualizar.
        nome (str): novo nome desejado.

    Returns:
        NivelPermissao | None: o cargo atualizado; None se o cargo não existir.
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

def criar_usuario(cpf: str, nome: str, email: str, senha: str, id_permissao: int, salario=None) -> int | None: 
    """
    Cria um novo usuário com dados sensíveis criptografados. 
    Criptografa CPF e e-mail, gera seus HMACs de busca, aplica hash na senha e, quando informado, converte o salário para centavos. 
    
    Args: 
        cpf (str): CPF do usuário. 
        nome (str): nome do usuário. 
        email (str): e-mail do usuário. 
        senha (str): senha em texto puro (será transformada em hash). 
        id_permissao (int): cargo/nível de permissão do usuário. 
        salario (optional): salário em formato monetário; convertido para centavos quando fornecido. 
        
    Returns: 
        int | None: id do usuário criado; None em caso de violação de integridade.
    """
    cpf_criptografado=criptografar(cpf) 
    cpf_hmac=gerar_hmac(cpf=cpf) 
    email_criptografado=criptografar(email) 
    email_hmac=gerar_hmac(email=email) 
    senha_criptografada=generate_password_hash(senha) 
    
    from utils import moeda_para_centavos 
    if salario: 
        salario = moeda_para_centavos(salario) 
        
    novo_usuario=Usuario(cpf_criptografado=cpf_criptografado, cpf_hmac=cpf_hmac, nome=nome, email_criptografado=email_criptografado, email_hmac=email_hmac, senha_hash=senha_criptografada,id_permissao=id_permissao, salario=salario) 
    db.session.add(novo_usuario) 
    
    try: 
        db.session.commit() 
    except IntegrityError: 
        db.session.rollback() 
        return None 
        
    cargo = db.session.get(NivelPermissao, id_permissao).nome 
    registrar_log('CADASTRO', f'Novo usuário {cargo} {nome} cadastrado.') 
    
    return novo_usuario.id_usuario


def registrar_log(acao: str, descricao: str | None = None) -> bool:
    """Registra uma atividade do usuário logado na trilha de auditoria.

    Args:
        acao (str): rótulo curto da ação realizada.
        descricao (str | None, optional): detalhamento da ação.

    Returns:
        bool: True após o registro.
    """
    log = LogAtividade(id_usuario=session.get("id"), acao=acao, descricao=descricao )
    db.session.add(log)
    try:
        db.session.commit()
    except IntegrityError:
        return False
    return True

def buscar_usuario_para_login(credencial: str, senha: str) -> int | None:
    """Autentica um usuário por CPF/e-mail e senha e retorna o id.

    Decide o campo de busca pelo formato da credencial (presença de '@').

    Args:
        credencial (str): CPF ou e-mail do usuário.
        senha (str): senha em texto puro.

    Returns:
        int | None: id do usuário se as credenciais forem válidas; None caso
        contrário.
    """

    if "@" in credencial:
        credencial_hmac=gerar_hmac(email=credencial)
        campo=Usuario.email_hmac
    else:
        credencial_hmac=gerar_hmac(cpf=credencial)
        campo=Usuario.cpf_hmac

    usuario = db.session.execute(
        db.select(Usuario).where(campo == credencial_hmac, Usuario.ativo.is_(True)),
    ).scalar_one_or_none()


    if usuario and check_password_hash(usuario.senha_hash, senha):
        return usuario.id_usuario

    return None

def buscar_endereco_por_id(id_endereco: int) -> Endereco | None:
    """Busca um endereço pelo id. Retorna None se não existir."""
    return db.session.get(Endereco, id_endereco)

def buscar_usuario_por_id(id: int) -> Usuario | None:
    """Busca um usuário ativo pelo id. Retorna None se não existir."""
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
            Usuario.id_permissao==Cargo.CHEFE.value,
            ).order_by(Usuario.nome.collate("NOCASE")),
    ).scalars().all()


def atualizar_usuario(id_usuario: int, nome: str | None = None, email: str | None = None, cpf: str | None = None, nova_senha: str | None = None) -> bool:
    """Atualiza os dados cadastrais de um usuário (campos None são ignorados).

    Recriptografa e regenera os HMACs de e-mail/CPF quando alterados e aplica
    hash na nova senha quando informada.

    Args:
        id_usuario (int): identificador do usuário.
        nome (str | None, optional): novo nome.
        email (str | None, optional): novo e-mail.
        cpf (str | None, optional): novo CPF.
        nova_senha (str | None, optional): nova senha em texto puro.

    Returns:
        bool: True se atualizado; False se o usuário não existir.
    """
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


def deletar_usuario(id_usuario: int, soft_delete: bool = True) -> bool:
    """Desativa (soft delete) ou remove definitivamente um usuário.

    Args:
        id_usuario (int): identificador do usuário.
        soft_delete (bool, optional): se True, apenas marca como inativo; se
            False, remove o registro. Padrão: True.

    Returns:
        bool: True se a operação ocorreu; False se o usuário não existir.
    """
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

def reativar_usuario(id_usuario: int) -> bool:
    """Reativa a conta de um usuário inativo. Retorna False se não existir."""
    usuario=db.session.get(Usuario,id_usuario)

    if not usuario:
        return False

    usuario.ativo=True
    db.session.commit()
    registrar_log("REATIVACAO", f"Conta do usuário {id_usuario} reativada")

    return True

def adicionar_endereco(nome: str, logradouro: str, numero: str, complemento: str, bairro: str, cidade: str, cep: str) -> Endereco | None:
    """Adiciona um novo endereço ao usuário logado.

    Args:
        nome (str): identificação do endereço (ex.: "Casa").
        logradouro (str): logradouro (rua/avenida).
        numero (str): número.
        complemento (str): complemento (opcional).
        bairro (str): bairro.
        cidade (str): cidade.
        cep (str): CEP.

    Returns:
        Endereco | None: endereço criado; None em caso de violação de integridade.
    """
    endereco=Endereco(id_usuario=session.get("id"), nome=nome, logradouro=logradouro, numero=int(numero), complemento=complemento, bairro=bairro, cidade=cidade, cep=cep)
    db.session.add(endereco)

    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return None
    registrar_log("NOVO ENDERECO", f"Novo endereco no id {endereco.id_endereco} criado.")
    return endereco

def buscar_enderco_por_usuario(id_usuario: int) -> list[Endereco] | None:
    """Busca todos os endereços de um usuário.

    Args:
        id_usuario (int): identificador do usuário.

    Returns:
        list[Endereco] | None: lista de endereços; None se o usuário não tiver
        nenhum.
    """

    enderecos=db.session.execute(
        db.select(Endereco).where(Endereco.id_usuario==id_usuario),
    ).scalars().all()

    if not enderecos:
        return None

    return enderecos

def buscar_endereco_por_id(id_endereco: int) -> Endereco | None:
    """Busca um endereço pelo id. Retorna None se não existir."""
    endereco=db.session.get(Endereco, id_endereco)

    if not endereco:
        return None

    return endereco

def listar_enderecos_do_usuario(id_usuario: int) -> list[Endereco]:
    """Lista os endereços de um usuário (lista vazia se não houver)."""
    return db.session.execute(
        db.select(Endereco).where(Endereco.id_usuario == id_usuario),
    ).scalars().all()

def atualizar_endereco(id_endereco: int, nome=None, logradouro=None, numero=None, complemento=None, bairro=None, cidade=None, cep=None) -> bool:
    """Atualiza os dados de um endereço (campos None não são alterados).

    O complemento pode ser limpo (aceita string vazia).

    Args:
        id_endereco (int): identificador do endereço.
        nome (str | None, optional): nova identificação do endereço.
        logradouro (str | None, optional): novo logradouro.
        numero (str | None, optional): novo número.
        complemento (str | None, optional): novo complemento.
        bairro (str | None, optional): novo bairro.
        cidade (str | None, optional): nova cidade.
        cep (str | None, optional): novo CEP.

    Returns:
        bool: True se atualizado; False se o endereço não existir.
    """

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
    """Remove um endereço pelo id. Retorna False se não existir."""
    endereco = db.session.get(Endereco, id_endereco)
    if not endereco:
        return False

    db.session.delete(endereco)
    db.session.commit()
    registrar_log("REMOCAO ENDERECO", f"Endereço {id_endereco} removido.")
    return True

def buscar_log_por_id(id_atividade: int) -> LogAtividade | None:
    """Busca um registro de atividade pelo id. Retorna None se não existir."""
    return db.session.get(LogAtividade, id_atividade)

def listar_logs(busca: str = "") -> list[LogAtividade]:
    """Lista os registros de atividade, do mais recente para o mais antigo.

    Args:
        busca (str, optional): filtra pela ação (correspondência parcial).
            Padrão: "".

    Returns:
        list[LogAtividade]: registros encontrados (lista vazia se não houver).
    """
    stmt = db.select(LogAtividade)

    termo = busca.strip()
    if termo:
        stmt = stmt.where(LogAtividade.acao.like(f"%{termo}%"))

    stmt = stmt.order_by(LogAtividade.realizado_em.desc())

    return db.session.execute(stmt).scalars().all()

def deletar_log(id_atividade: int) -> bool:
    """Remove um registro de atividade pelo id. Retorna False se não existir."""
    log = db.session.get(LogAtividade, id_atividade)
    if not log:
        return False
    db.session.delete(log)
    db.session.commit()
    return True
