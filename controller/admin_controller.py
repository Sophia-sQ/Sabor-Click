from flask import Blueprint, request, render_template
from werkzeug.security import generate_password_hash

from model.usuario_model import criar_usuario
from model.cargos import Cargo

admin_bp = Blueprint("admin", __name__, url_prefix='/admin')

@admin_bp.route("/cadastro", methods=("POST"))
def cadastro():
    "adiciona um novo usuario funcionário."

    nome=request.form.get("nome", "").strip()
    cpf=request.form.get("cpf", "").strip()
    telefone=request.form.get("telefone", "").strip()
    email=request.form.get("email", "").strip()
    senha=request.form.get("senha", "")
    
    criar_usuario(cpf, nome, email, generate_password_hash(senha), Cargo.CHEFE)
    
    return render_template("""TODO: colocar pagina de cadastro do admin""")