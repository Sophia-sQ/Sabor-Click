from secrets import randbelow

from model.usuario_model import buscar_usuario_para_login, buscar_usuario_por_id, criar_usuario
from model.cargos import Cargo

from flask import Blueprint, render_template, request, session, flash, redirect, url_for
from services import enviar_email_nao_responda

from re import fullmatch, match
from security import validar_senha_forte

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method=='GET':
        return render_template("login.html")
    
    # estabelece qual o formato de um email válido
    regex=r"^['A-Za-z0-9._%+-']+@[A-Za-z0-9.-]+\.['A-Za-z']{2,}$"
    
    tipo_login=request.form.get("tipo_login", "")
    credencial=request.form.get("credencial", "").strip()
    senha=request.form.get("senha", "")
    
    # validação de email, cpf e senha com variáveis booleanas
    if tipo_login=='email':
        email_invalido = (tipo_login == 'email' and not fullmatch(regex, credencial))
        
    elif tipo_login=='cpf':
        cpf = credencial.replace(".", "").replace("-", "")
        cpf_invalido = (tipo_login == 'cpf' and (len(cpf) != 11 or not cpf.isdigit()))

    senha_invalida = not validar_senha_forte(senha)

    if email_invalido or cpf_invalido or senha_invalida:  
        flash(f"{tipo_login} ou senha inválidos.", 'danger')
        return redirect(url_for("auth.login"))
    
    # credenciais são válidas    
    id_usuario=buscar_usuario_para_login(credencial, senha)
    usuario = buscar_usuario_por_id(id_usuario)
    
    #geração de token
    tamanho = 6
    codigo = "".join(str(randbelow(10)) for _ in range(tamanho))
    
    
    if usuario: #não envia emails para contas que não existem 
        enviar_email_nao_responda("Código de validação", usuario.email, 
    f"""seu codigo de validação: {codigo}.
    
    Ele permanecerá ativo por 10 minutos.""",
    render_template('email_token.html', token=codigo))
    
    if id_usuario is not None:
        session.clear()
        session["id"]=id_usuario
        session["cargo"]=usuario.id_permissao
        return render_template("home.html")    
    
    return render_template("login.html")


@auth_bp.route("/logout", methods=["POST"])
def logout():
    "Remove o usuário da sessão e volta para página inicial."
    
    session.clear()
    return render_template("home.html")  

@auth_bp.route("/cadastro", methods=["GET","POST"])
def cadastro():
    "adiciona um novo usuario cliente."

    if request.method=='GET':
        return render_template("cadastro.html")

    nome=request.form.get("nome", "").strip()
    cpf=request.form.get("cpf", "").strip()
    email=request.form.get("email", "").strip()
    senha=request.form.get("senha", "")
    
    usuario=criar_usuario(cpf, nome, email, senha, Cargo.CLIENTE.value)
    if not usuario:
        flash("Falha no cadastro. Tente novamente", "danger")
        return render_template("cadastro.html")
    
    return render_template('login.html')  
        
