"""Rotas administrativas de gerenciamento de funcionários."""

from . import admin_bp

from datetime import date

from flask import request, url_for, Response, jsonify, render_template, flash, redirect

from model.usuario_model import criar_usuario, buscar_funcionarios as listar
from model.cargos import Cargo

from re import fullmatch
from security import validar_senha_forte

# ========================= Visão geral =========================
@admin_bp.get("")
@admin_bp.get("/visao-geral")
def visao_geral():
    """Renderiza a página de visão geral do painel administrativo."""
    return render_template(
        "admin.html",
        relatorio_url=url_for("admin.gerar_relatorios_mensais"),
    )

# xxxxxxxxxxxxxxxxxxxxxxxxxx RELATÓRIOS DO MÊS xxxxxxxxxxxxxxxxxxxxxxxxxx

@admin_bp.get('/visao-geral/relatorios')
def gerar_relatorios_mensais() -> Response:
    """Gera um relatório com indicadores mensais e semanais de pedidos.

    Reúne quantidade de pedidos, faturamento mensal, ticket médio, serviços mais
    solicitados, faturamento das últimas seis semanas e distribuição por status.

    Returns:
        Response: resposta JSON contendo:
            - pedidos_quantidade (dict): total do mês e variação percentual.
            - faturamento_mensal (dict): faturamento do mês e variação percentual.
            - ticket_medio (dict): ticket médio atual e variação percentual.
            - pedidos_tipo (dict): quantidade de pedidos por serviço.
            - faturamento_semanal (dict): faturamento das últimas seis semanas.
            - pedidos_status (dict): quantidade de pedidos por status.
    """
    
    if "inicio" in request.args or "fim" in request.args:
        try:
            inicio = date.fromisoformat(request.args.get("inicio", ""))
            fim = date.fromisoformat(request.args.get("fim", ""))
            if inicio > fim:
                raise ValueError
        except ValueError:
            return jsonify(erro="Informe um intervalo de datas válido."), 400

        from services.relatorios import resumo_pedidos_por_dia

        return jsonify(dias=resumo_pedidos_por_dia(inicio, fim))

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
    """Renderiza a lista de funcionários, com filtro opcional por nome (query 'busca')."""
    from security import descriptografar

    busca = request.args.get("busca", "")

    funcionarios = [
        {
            "id": usuario.id_usuario,
            "nome": usuario.nome,
            "email": descriptografar(usuario.email_criptografado),
            "salario": usuario.salario,
            "cargo": "Chefe",
        }
        for usuario in listar(busca)
    ]

    return render_template('funcionarios.html', funcionarios=funcionarios, busca=busca)

@admin_bp.get("/funcionarios/relatorio")
def dados_funcionarios() -> Response:
    """Retorna, em JSON, o total de funcionários e a soma dos salários.

    Returns:
        Response: JSON com 'total_funcionarios' e 'total_pagamento'.
    """
    funcionarios = listar()
    total_funcionarios=len(funcionarios)
    
    total_pagamento = 0
    for funcionario in funcionarios:
        total_pagamento += funcionario.salario

    return jsonify({"total_funcionarios": total_funcionarios,
                    "total_pagamento": total_pagamento})

# xxxxxxxxxxxxxxxxxxxxxxxxxxx cadastro xxxxxxxxxxxxxxxxxxxxxxxxxxx
@admin_bp.get("/cadastrar-funcionario")
def cadastrar_funcionario():
    """Redireciona para a lista de funcionários (o cadastro é um diálogo dessa página)."""
    return redirect(url_for('admin.funcionarios'))

@admin_bp.post("/cadastrar-funcionario/cadastro")
def cadastro():
    """Cadastra um novo funcionário (cargo CHEFE) a partir do formulário.

    Valida e-mail, CPF e senha, confere a confirmação de senha e sinaliza o
    resultado via flash.

    Returns:
        Response: redirecionamento para a lista de funcionários (padrão PRG),
        tanto em caso de erro quanto de sucesso.
    """
    nome=request.form.get("nome", "").strip()
    cpf=request.form.get("cpf", "").strip()
    email=request.form.get("email", "").strip()
    senha=request.form.get("senha_provisoria", "")
    senha_comfirma=request.form.get("senha_confirmacao", "")

    # estabelece qual o formato de um email válido
    regex=r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$"

    # validação de nome, email, cpf e senha com variáveis booleanas
    nome_invalido = (not nome or len(nome) > 100)
    email_invalido = (not fullmatch(regex, email))
    cpf = cpf.replace(".", "").replace("-", "")
    cpf_invalido = ((len(cpf) != 11 or not cpf.isdigit()))

    senha_invalida = not validar_senha_forte(senha)

    if nome_invalido or email_invalido or cpf_invalido or senha_invalida:
        flash(f"Nome, e-mail, cpf ou senha inválidos.", 'danger')
        return redirect(url_for('admin.funcionarios'))
    elif senha!=senha_comfirma:
        flash(f"Senha provisória e de confirmação são diferentes.", 'danger')
        return redirect(url_for('admin.funcionarios'))

    novo_id = criar_usuario(cpf, nome, email, senha, Cargo.CHEFE.value)

    if novo_id is None:
        flash("CPF ou e-mail ja cadastrado.", "danger")
        return redirect(url_for('admin.funcionarios'))

    flash("Funcionario cadastrado com sucesso.", "success")
    return redirect(url_for('admin.funcionarios'))

