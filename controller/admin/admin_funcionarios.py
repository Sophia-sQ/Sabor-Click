from admin import admin_bp

from flask import request, url_for, Response, jsonify, render_template, flash, redirect

from model.usuario_model import criar_usuario, buscar_funcionarios as listar
from model.cargos import Cargo

from re import fullmatch
from security import validar_senha_forte

# ========================= Visão geral =========================
@admin_bp.get("")
@admin_bp.get("/visao-geral")
def visao_geral():
    return render_template("TODO: visao geral painel administrativo")

# xxxxxxxxxxxxxxxxxxxxxxxxxx RELATÓRIOS DO MÊS xxxxxxxxxxxxxxxxxxxxxxxxxx

@admin_bp.get('/visao-geral/relatorios')
def gerar_relatorios_mensais() -> Response:
    """Gera um relatório com indicadores mensais e semanais de pedidos.

    Reúne informações sobre a quantidade de pedidos, faturamento mensal,
    ticket médio, serviços mais solicitados, faturamento das últimas seis
    semanas e distribuição dos pedidos por status.

    Returns:
        Response: Resposta JSON contendo:
            - pedidos_quantidade (dict): total de pedidos no mês atual
              e variação percentual em relação ao período anterior.
            - faturamento_mensal (dict): faturamento do mês atual e
              variação percentual em relação ao período anterior.
            - ticket_medio (dict): ticket médio atual e variação
              percentual em relação ao período anterior.
            - pedidos_tipo (dict): quantidade de pedidos por serviço.
            - faturamento_semanal (dict): faturamento de cada uma das
              últimas seis semanas completas.
            - pedidos_status (dict): quantidade de pedidos por status.
    """
    
    import services 
    
    pq=services.pedidos_quantidade()
    fm=services.faturamento_periodo()
    tm=services.ticket_medio_periodo()
    pt=services.pedidos_tipo()
    fs=services.faturamento_semanal()
    ps=services.pedidos_status()
    
    return jsonify({
    "pedidos_quantidade": {
        "numero": pq[0],
        "porcentagem": pq[1]
    },
    "faturamento_mensal": {
        "numero": fm[0],
        "porcentagem": fm[1]
    },
    "ticket_medio": {
        "numero": tm[0],
        "porcentagem": tm[1]
    },
    "pedidos_tipo": pt,
    "faturamento_semanal": fs,
    "pedidos_status": ps
    })

# ========================= Funcionarios =========================

@admin_bp.get('/funcionarios')
def funcionarios():
    busca = request.args.get("busca", "")
    return render_template('paginas funcionaris', funcionarios=listar(busca), busca=busca) #TODO: pagina de funcionarios

@admin_bp.get("/funcionarios/relatorio")
def dados_funcionarios():
    funcionarios = listar()
    total_funcionarios=len(funcionarios)
    
    total_pagamento = 0
    for funcionario in funcionarios:
        total_pagamento += funcionario.salario #FIXME: verificar se essa é a coluna correta

    return jsonify({"total_funcionarios": total_funcionarios,
                    "total_pagamento": total_pagamento})

# xxxxxxxxxxxxxxxxxxxxxxxxxxx cadastro xxxxxxxxxxxxxxxxxxxxxxxxxxx
@admin_bp.get("/cadastrar-funcionario")
def cadastrar_funcionario():
    return render_template("casadtro do admin") #TODO

@admin_bp.post("/cadastrar-funcionario/cadastro")
def cadastro():
    "adiciona um novo usuario funcionário."

    nome=request.form.get("nome", "").strip()
    cpf=request.form.get("cpf", "").strip()
    email=request.form.get("email", "").strip()
    senha=request.form.get("senha_provisoria", "")
    senha_comfirma=request.form.get("senha_confirmacao", "")

    # estabelece qual o formato de um email válido
    regex=r"^['A-Za-z0-9._%+-']+@[A-Za-z0-9.-]+\.['A-Za-z']{2,}$"

    # validação de email, cpf e senha com variáveis booleanas
    email_invalido = (not fullmatch(regex, email))
    cpf = cpf.replace(".", "").replace("-", "")
    cpf_invalido = ((len(cpf) != 11 or not cpf.isdigit()))

    senha_invalida = not validar_senha_forte(senha)

    if email_invalido or cpf_invalido or senha_invalida:  
        flash(f"E-mail, cpf ou senha inválidos.", 'danger')
        return redirect(url_for(''))
    elif senha!=senha_comfirma:
        flash(f"Senha provisória e de confirmação são diferentes.", 'danger')
        return redirect(url_for('admin.cadastrar_funcionario'))
    
    criar_usuario(cpf, nome, email, senha, Cargo.CHEFE.value)

    flash("novo funcionaria cadastrado", "success")
    return render_template('admin.cadastrar_funcionario')

