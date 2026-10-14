from flask import Blueprint, request, render_template, redirect, url_for, session
from werkzeug.security import generate_password_hash

from model.usuario_model import criar_usuario
from model.cargos import Cargo
from model.ficha_model import (
    listar_pratos,
    listar_ingredientes,
    listar_lotes,
)

from decimal import Decimal, InvalidOperation

from model.servico_model import (
    atualizar_servico as atualizar_servico_model,
    deletar_servico as deletar_servico_model,
    criar_cardapio as criar_cardapio_model,
    atualizar_cardapio as atualizar_cardapio_model,
    deletar_cardapio as deletar_cardapio_model,
)

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")

# =========================
# CADASTRAR FUNCIONÁRIO
# =========================

@admin_bp.route("/cadastro", methods=("POST",))
def cadastro():
    "adiciona um novo usuario funcionário."

    nome=request.form.get("nome", "").strip()
    cpf=request.form.get("cpf", "").strip()
    telefone=request.form.get("telefone", "").strip()
    email=request.form.get("email", "").strip()
    senha=request.form.get("senha", "")
    
    criar_usuario(cpf, nome, email, senha, Cargo.CHEFE.value)
    
    return render_template("""TODO: colocar pagina de cadastro do admin""")

@admin_bp.route("/", methods=("GET",))
def home():
    """Exibe o painel inicial administrativo."""

    # Consulta os dados usando as funções já existentes no modelo.
    pratos = listar_pratos() or []
    ingredientes = listar_ingredientes() or []
    lotes = listar_lotes() or []

    # Parâmetro de pesquisa enviado pela URL.
    busca = request.args.get("busca", "").strip().casefold()

    # Identifica ingredientes que atingiram ou ficaram abaixo
    # da quantidade mínima configurada.
    ingredientes_baixo_estoque = [
        ingrediente
        for ingrediente in ingredientes
        if ingrediente.qtd <= ingrediente.qtd_min
    ]

    # Filtra os resultados sem criar novas consultas ao banco.
    if busca:
        pratos = [
            prato for prato in pratos
            if busca in prato.nome.casefold()
            or busca in prato.tipo_prato.casefold()
            or busca in str(prato.id_prato)
        ]

        ingredientes = [
            ingrediente for ingrediente in ingredientes
            if busca in ingrediente.nome.casefold()
            or busca in str(ingrediente.id_ingrediente)
        ]

        lotes = [
            lote for lote in lotes
            if busca in lote.num_lote.casefold()
            or busca in lote.marca.casefold()
            or busca in str(lote.id_lote)
        ]

        ingredientes_baixo_estoque = [
            ingrediente for ingrediente in ingredientes_baixo_estoque
            if busca in ingrediente.nome.casefold()
            or busca in str(ingrediente.id_ingrediente)
        ]

    return render_template(
        "admin/home.html",
        busca=busca,
        pratos=pratos,
        ingredientes=ingredientes,
        lotes=lotes,
        ingredientes_baixo_estoque=ingredientes_baixo_estoque,
    )



# =========================
# ATUALIZAR SERVIÇO
# =========================

@admin_bp.route("/atualizar_servico/<int:id_servico>", methods=("POST",))
def atualizar_servico(id_servico):
    nome = request.form.get("nome", "").strip()
    descricao = request.form.get("descricao", "").strip()

    if not nome or not descricao:
        return "Nome e descrição são obrigatórios.", 400

    sucesso = atualizar_servico_model(
        id_servico=id_servico,
        id_usuario=session.get("id"),
        nome=nome,
        descricao=descricao,
    )

    if not sucesso:
        return "Serviço não encontrado.", 404

    return redirect(url_for("admin.home"))


# =========================
# DELETAR SERVIÇO
# =========================

@admin_bp.route("/deletar_servico/<int:id_servico>", methods=("POST",))
def deletar_servico(id_servico):
    sucesso = deletar_servico_model(
        id_servico=id_servico,
        id_usuario=session.get("id"),
    )

    if not sucesso:
        return "Serviço não encontrado.", 404

    return redirect(url_for("admin.home"))


# =========================
# CRIAR CARDÁPIO
# =========================

@admin_bp.route("/criar_cardapio", methods=("POST",))
def criar_cardapio():
    nome = request.form.get("nome", "").strip()
    descricao = request.form.get("descricao", "").strip()
    preco_texto = request.form.get("preco_base", "").strip()

    if not nome or not descricao or not preco_texto:
        return "Preencha todos os campos.", 400

    try:
        preco_base = Decimal(preco_texto.replace(",", "."))
    except InvalidOperation:
        return "Preço inválido.", 400

    if not preco_base.is_finite() or preco_base < 0:
        return "O preço deve ser válido e não negativo.", 400

    criar_cardapio_model(
        nome=nome,
        descricao=descricao,
        preco_base=preco_base,
        id_usuario=session.get("id"),
    )

    return redirect(url_for("admin.home"))


# =========================
# ATUALIZAR CARDÁPIO
# =========================

@admin_bp.route(
    "/atualizar_cardapio/<int:id_cardapio>",
    methods=("POST",),
)
def atualizar_cardapio(id_cardapio):
    nome = request.form.get("nome", "").strip()
    descricao = request.form.get("descricao", "").strip()
    preco_texto = request.form.get("preco_base", "").strip()

    if not nome or not descricao or not preco_texto:
        return "Preencha todos os campos.", 400

    try:
        preco_base = Decimal(preco_texto.replace(",", "."))
    except InvalidOperation:
        return "Preço inválido.", 400

    if not preco_base.is_finite() or preco_base < 0:
        return "O preço deve ser válido e não negativo.", 400

    sucesso = atualizar_cardapio_model(
        id_cardapio=id_cardapio,
        id_usuario=session.get("id"),
        nome=nome,
        descricao=descricao,
        preco_base=preco_base,
    )

    if not sucesso:
        return "Cardápio não encontrado.", 404

    return redirect(url_for("admin.home"))


# =========================
# DELETAR CARDÁPIO
# =========================

@admin_bp.route(
    "/deletar_cardapio/<int:id_cardapio>",
    methods=("POST",),
)
def deletar_cardapio(id_cardapio):
    sucesso = deletar_cardapio_model(
        id_cardapio=id_cardapio,
        id_usuario=session.get("id"),
    )

    if not sucesso:
        return "Cardápio não encontrado.", 404

    return redirect(url_for("admin.home"))

