from . import _retorno, admin_bp
from flask import flash, render_template, request

from model.ficha_model import buscar_ingredientes, buscar_lotes, buscar_pratos
from model.pedido_model import buscar_bebidas
from model.servico_model import atualizar_servico, buscar_servicos, deletar_servico

# ============================== Servicos =============================

@admin_bp.get("/servicos")
def pagina_servicos():
    """Página de serviços com busca unificada.

    O parâmetro de query `busca` filtra, por correspondência parcial, todas as
    entidades exibidas nesta página: serviços, bebidas, pratos, ingredientes e
    lotes. Sem `busca`, lista tudo.
    """
    busca = request.args.get("busca", "").strip()

    servicos = buscar_servicos(busca)
    bebidas = buscar_bebidas(busca)
    pratos = buscar_pratos(busca)
    ingredientes = buscar_ingredientes(busca)
    lotes = buscar_lotes(busca)

    return render_template(
        "servico.html",  # TODO: nome da pagina
        busca=busca,
        servicos=servicos,
        bebidas=bebidas,
        pratos=pratos,
        ingredientes=ingredientes,
        lotes=lotes,
    )


# ========================= ATUALIZAR SERVIÇO =========================
@admin_bp.post("/servicos/atualizar_servico/<int:id_servico>")
def at_servico(id_servico: int):
    nome = request.form.get("nome", "").strip()
    descricao = request.form.get("descricao", "").strip()

    if not nome or not descricao:
       flash("Falha ao tentar deletar o serviço", "danger")
       _retorno()


    sucesso = atualizar_servico(
        id_servico=id_servico,
        nome=nome,
        descricao=descricao,
    )

    if not sucesso:
       flash("Falha ao tentar atualizar o serviço", "danger")
       _retorno()

    flash("Serviço atualizado.", "success")
    _retorno()

# ========================= DELETAR SERVIÇO =========================
@admin_bp.post("/servicos/deletar_servico/<int:id_servico>")
def del_servico(id_servico: int):
    sucesso = deletar_servico(id_servico=id_servico)

    if not sucesso:
        flash("Falha ao tentar deletar o serviço", "danger")
        _retorno()


    flash("Serviço deletado.", "success")
    _retorno()
