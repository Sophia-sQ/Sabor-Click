from secrets import randbelow

from model.usuario_model import buscar_usuario_para_login, buscar_usuario_por_id, criar_usuario
from model.cargos import Cargo

from flask import Blueprint, render_template, request, session
from utils import enviar_email_nao_responda


auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/login", methods=("GET", "POST"))
def login():
    credencial=request.form.get("credencial", "").strip()
    senha=request.form.get("senha", "")
    
    id_usuario=buscar_usuario_para_login(credencial, senha)
    usuario = buscar_usuario_por_id(id_usuario)
    
    #geração de token
    tamanho = 6
    codigo = "".join(str(randbelow(10)) for _ in range(tamanho))
    
    
    if usuario: #não envia emails para contas que não existem 
        enviar_email_nao_responda("Código de validação", usuario.email, 
    f"""seu codigo de validação: {codigo}.
    
    Ele permanecerá ativo por 10 minutos.""", 
    
    f"""fazer modelo de email
    """)
    
    if id_usuario is not None:
        session.clear()
        session["id"]=id_usuario
        session["cargo"]=usuario.id_permissao
        return render_template("home.html")    
    
    return render_template("login.html")


@auth_bp.route("/logout", methods=("GET", "POST"))
def logout():
    "Remove o usuário da sessão e volta para página inicial."
    
    session.clear()
    return render_template("home.html")  

@auth_bp.route("/cadastro", methods=("POST"))
def cadastro():
    "adiciona um novo usuario cliente."

    nome=request.form.get("nome", "").strip()
    cpf=request.form.get("cpf", "").strip()
    email=request.form.get("email", "").strip()
    senha=request.form.get("senha", "")
    
    usuario=criar_usuario(cpf, nome, email, senha, Cargo.CLIENTE.value)
    if not usuario:
        return render_template("cadastro.html")
    
    return render_template('home.html')  