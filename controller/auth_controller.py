import smtplib
from email.message import EmailMessage


from flask import Blueprint, render_template, request, session
from werkzeug.security import check_password_hash, generate_password_hash

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/login", methods=("GET", "POST"))
def login():
    # TODO: garantir que os names da página batam
    cpf=request.form.get("cpf", "").strip()
    senha=request.form.get("senha", "")
    
    #adicoonar busca pelo usuario e validação da senha e geração de token
    
    """import smtplib
from email.message import EmailMessage

email = EmailMessage()

email["Subject"] = "Código de confirmação"
email["From"] = "seuemail@gmail.com"
email["To"] = "destinatario@gmail.com"

codigo = "583214"

# Versão para clientes que não exibem HTML
email.set_content(
    f"Seu código de confirmação é: {codigo}"
)

# Versão HTML
email.add_alternative(f aspastripals
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
aspastripals, subtype="html")

with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
    smtp.login("seuemail@gmail.com", "SUA_SENHA_DE_APP")
    smtp.send_message(email)aspastripals"""
    
    return render_template("login.html") #TODO :pagina de login