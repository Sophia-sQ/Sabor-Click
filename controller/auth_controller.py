from secrets import randbelow

from model.usuario_model import buscar_usuario_para_login, buscar_usuario_por_id, criar_usuario
from model.cargos import Cargo

from flask import Blueprint, render_template, request, session, flash, redirect, url_for
from services import enviar_email_nao_responda

from re import fullmatch, match

from security.token_auth import enviar_token, validar_token

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
    
    # Credenciais são válidas
    id_usuario = buscar_usuario_para_login(credencial, senha)

    if id_usuario is None:
        flash("Credenciais inválidas.", "danger")
        return redirect(url_for("auth.login"))

    usuario = buscar_usuario_por_id(id_usuario)

    if usuario is None:
        flash("Não foi possível localizar o usuário.", "danger")
        return redirect(url_for("auth.login"))

    # Solicita o token 
    try:
        enviar_token(usuario.email)
    except Exception:
        from flask import current_app

        current_app.logger.exception("Falha ao enviar o código de verificação.")
        flash("Não foi possível enviar o código.", "danger")
        return redirect(url_for("auth.login"))

    # Guarda os dados necessários para concluir a autenticação.
    # O usuário ainda não está autenticado.
    session.clear()
    session["usuario_pendente_id"] = id_usuario
    session["email_pendente"] = usuario.email

    flash("Código enviado. Verifique seu e-mail.", "info")

    return redirect(url_for("auth.verificar_token"))

@auth_bp.route("/verificar-token", methods=["GET", "POST"])
def verificar_token():
    email_pendente = session.get("email_pendente")
    id_pendente = session.get("usuario_pendente_id")

    if email_pendente is None or id_pendente is None:
        flash("Faça login para solicitar um código.", "warning")
        return redirect(url_for("auth.login"))

    erro = None

    if request.method == "POST":
        codigo = request.form.get("codigo", "").strip()

        if validar_token(email_pendente, codigo):
            usuario = buscar_usuario_por_id(id_pendente)

            if usuario is None:
                session.clear()
                flash("Usuário não encontrado.", "danger")
                return redirect(url_for("auth.login"))

            session.clear()
            session["id"] = id_pendente
            session["cargo"] = usuario.id_permissao

            flash("E-mail verificado com sucesso!", "success")
            return render_template("home.html")

        erro = "Código inválido ou expirado. Tente novamente."

    return render_template("verificacao.html", erro=erro)

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


def validar_senha_forte(senha:str = None) -> bool:
    """Verifica se a senha tem no mínimo 5 caracteres. Entre eles devem existir 
    pelo menos um maiúsculo, um minúsculo, um número e um caracter especial.
    
    Retorna True em caso positivo e False em caso negativo."""
    
    regex = r"^(?=.*[A-Z])(?=.*[a-z])(?=.*[0-9])(?=.*[@#$%^&+=!_*-]).{5,}$"
    
    if match(senha, regex):
        return True
    else:
        False
        