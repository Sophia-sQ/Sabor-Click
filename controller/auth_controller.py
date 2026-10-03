import smtplib
from email.message import EmailMessage

from os import environ as env

from model.usuario_model import buscar_usuario_para_login, buscar_usuario_por_id
from flask import Blueprint, render_template, request, session
from werkzeug.security import generate_password_hash

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/login", methods=("GET", "POST"))
def login():
    # TODO: garantir que os names da página batam
    # TODO: adicionar possibilidade de login por email
    cpf=request.form.get("cpf", "").strip()
    senha=request.form.get("senha", "")
    
    id_usuario=buscar_usuario_para_login(cpf, senha)
    
    #adicionar validação da senha e geração de token
    email = EmailMessage()

    email["Subject"] = "Código de confirmação"
    email["From"] = env.get("EMAIL")
    email["To"] = buscar_usuario_por_id(id_usuario).email

    codigo = "583214" # TODO: implementar calculo com secrets

    # Versão para clientes que não exibem HTML
    email.set_content(
        f"Seu código de confirmação é: {codigo}"
    )

    # Versão HTML
    email.add_alternative(f"""
    <!DOCTYPE html>
    <html>
    <body>
        <h1>Confirmação de login</h1>

        <p>Seu código de confirmação é:</p>

        <div style="
            font-size: 32px;
            font-weight: bold;
            padding: 15px;
            text-align: center;
        ">
            {codigo}
        </div>

        <p>Esse código é válido por 10 minutos.</p>
    </body>
    </html>
    """, subtype="html")

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        smtp.login(env.get("EMAIL"), env.get("PASSWORD"))
        smtp.send_message(email)
    
    if id_usuario is not None:
        session.clear()
        session["id"]=id_usuario
        session["cargo"]=... # TODO: adicionar busca por permissão
        
    
    return render_template("login.html") #TODO :pagina de login


@auth_bp.route("/logout", methods=("GET", "POST"))
def logout():
    session.clear()
    return render_template("""TODO: colocar pagina de login""")  