from admin import admin_bp, _retorno

from flask import render_template, flash, request

from model.servico_model import atualizar_servico, deletar_servico, listar_servicos
# ============================== Servicos =============================

@admin_bp.get("/servicos")
def pagina_servicos():
    servicos=listar_servicos()
    return render_template("servico.html", servicos=servicos) #TODO: nome da pagina

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
    sucesso = deletar_servico(id_servico=id_servico,)

    if not sucesso:
        flash("Falha ao tentar deletar o serviço", "danger")
        _retorno()


    flash("Serviço deletado.", "success")
    _retorno()
