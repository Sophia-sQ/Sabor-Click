<<<<<<< Updated upstream
from model.usuario_model import buscar_usuario_para_login, buscar_usuario_por_id, criar_usuario
from model.cargos import Cargo
from flask import Blueprint, render_template, request, session, flash, redirect, url_for
from re import fullmatch
from security import enviar_token, validar_token, validar_senha_forte
=======
from re import fullmatch

from flask import Blueprint, flash, redirect, render_template, request, session, url_for

from model.cargos import Cargo
from model.usuario_model import (
    buscar_usuario_para_login,
    buscar_usuario_por_id,
    criar_usuario,
)
from security import enviar_token, validar_senha_forte, validar_token
>>>>>>> Stashed changes

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")

    tipo_login = request.form.get("tipo_login", "")
    credencial = request.form.get("credencial", "").strip()
    senha = request.form.get("senha", "")
    email_invalido = cpf_invalido = False

    if tipo_login == "email":
        regex = r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$"
        email_invalido = not fullmatch(regex, credencial)
    elif tipo_login == "cpf":
        cpf = credencial.replace(".", "").replace("-", "")
        cpf_invalido = len(cpf) != 11 or not cpf.isdigit()
    else:
        email_invalido = True

    if email_invalido or cpf_invalido or not validar_senha_forte(senha):
        flash("Credenciais inválidas.", "danger")
        return redirect(url_for("auth.login"))

    id_usuario = buscar_usuario_para_login(credencial, senha)
    if id_usuario is None:
        flash("Credenciais inválidas.", "danger")
        return redirect(url_for("auth.login"))

    usuario = buscar_usuario_por_id(id_usuario)
    if usuario is None:
        flash("Não foi possível localizar o usuário.", "danger")
        return redirect(url_for("auth.login"))

    try:
        enviar_token(usuario.email_criptografado, id_usuario)
    except Exception:
        from flask import current_app
        current_app.logger.exception("Falha ao enviar o código de verificação.")
        flash("Não foi possível enviar o código.", "danger")
        return redirect(url_for("auth.login"))

    session.clear()
    session["usuario_pendente_id"] = id_usuario
    session["email_pendente"] = usuario.email_criptografado
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

        if len(codigo) != 6 or not codigo.isascii() or not codigo.isdigit():
            erro = "Informe um código válido de seis dígitos."
            return render_template("verificacao.html", erro=erro)

        if validar_token(id_pendente, codigo):
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
    session.clear()
    return render_template("home.html")


@auth_bp.route("/cadastro", methods=["GET", "POST"])
def cadastro():
    if request.method == "GET":
        return render_template("cadastro.html")
<<<<<<< Updated upstream

    nome = request.form.get("nome", "").strip()
    cpf = request.form.get("cpf", "").strip()
    email = request.form.get("email", "").strip()
    senha = request.form.get("senha", "")

    if not all([nome, cpf, email, senha]):
        flash("Preencha todos os campos.", "danger")
        return render_template("cadastro.html")

    usuario = criar_usuario(cpf, nome, email, senha, Cargo.CLIENTE.value)
    if not usuario:
        flash("Falha no cadastro. Tente novamente.", "danger")
        return render_template("cadastro.html")
    
    return render_template('login.html')  
        
=======

    nome = request.form.get("nome", "").strip()
    cpf = request.form.get("cpf", "").strip()
    email = request.form.get("email", "").strip()
    senha = request.form.get("senha", "")

    if not all([nome, cpf, email, senha]):
        flash("Preencha todos os campos.", "danger")
        return render_template("cadastro.html")

    usuario = criar_usuario(cpf, nome, email, senha, Cargo.CLIENTE.value)
    if not usuario:
        flash("Falha no cadastro. Tente novamente.", "danger")
        return render_template("cadastro.html")

    return render_template("login.html")

>>>>>>> Stashed changes
