from os import environ as env

from model.usuario_model import buscar_usuario_para_login, buscar_usuario_por_id
from flask import Blueprint, render_template, request, session
from werkzeug.security import generate_password_hash
from utils import enviar_email_nao_responda


auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/verificacao", methods=("GET", "POST"))
def verificacao():
    """Exibe o formulário; integrar a consulta do código antes de liberar acesso."""
    if request.method == "POST":
        codigo = request.form.get("codigo", "").strip()
        if len(codigo) != 6 or not codigo.isascii() or not codigo.isdigit():
            return render_template("verificacao.html", erro="Digite os 6 números do código recebido por e-mail."), 400
        # TODO: validar código, expiração e tentativas no banco para o usuário pendente.
        return render_template("verificacao.html", erro="A verificação está temporariamente indisponível. Tente novamente mais tarde."), 503
    return render_template("verificacao.html")

@auth_bp.route("/login", methods=("GET", "POST"))
def login():
    # TODO: garantir que os names da página batam
    # TODO: adicionar possibilidade de login por email
    credencial=request.form.get("credencial", "").strip()
    senha=request.form.get("senha", "")
    
    id_usuario=buscar_usuario_para_login(credencial, senha)
    
    #adicionar validação da senha e geração de token
    codigo = ... #TODO: gerar codigo
    
    enviar_email_nao_responda("Código de validação", buscar_usuario_por_id(id_usuario).email, 
    f"""seu codigo de validação: {codigo}.
    
    Ele permanecerá ativo por 10 minutos.""", 
    
    f"""fazer modelo de email
    """)
    
    if id_usuario is not None:
        session.clear()
        session["id"]=id_usuario
        session["cargo"]=... # TODO: adicionar busca por permissão
        
    
    return render_template("login.html") #TODO :pagina de login


@auth_bp.route("/logout", methods=("GET", "POST"))
def logout():
    "Remove o usuário da sessão e volta paraa página de login."
    
    session.clear()
    return render_template("""TODO: colocar pagina de login""")  

@auth_bp.route("/cadatro", methods=("POST"))
def cadastro():
    "adiciona um novo usuario cliente."

    nome=request.form.get("nome", "").strip()
    cpf=request.form.get("cpf", "").strip()
    telefone=request.form.get("telefone", "").strip()
    email=request.form.get("email", "").strip()
    senha=request.form.get("senha", "")
    
    # TODO: adicionar função de criação de usuário e de busca de id de permissões
    
    return render_template("""TODO: colocar pagina de login""")  