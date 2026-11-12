"""Fábrica da aplicação Flask (create_app) e registro de blueprints, filtros
    de template, hooks de requisição e handlers de erro."""

from flask import Flask, abort, redirect, render_template, request, session, url_for
from werkzeug.exceptions import HTTPException

from config import config_dict, mail  # importa configurações gerais da aplicação
from database import init_app as init_database
from model.cargos import Cargo
from utils import formatar_moeda, nome_exibicao


def create_app() -> Flask:
    """Cria e configura a instância da aplicação Flask.

    Registra os blueprints (auth, admin, chefe e cliente), as rotas de home e
    menu, o filtro Jinja de formatação monetária, os hooks de autenticação e
    autorização por cargo, os handlers de erro (400/403/404/500) e inicializa o
    banco de dados e o serviço de e-mail.

    Returns:
        Flask: aplicação Flask pronta para ser executada.
    """
    
    app = Flask(__name__, instance_relative_config=True)

    app.config.from_object(config_dict["default"])

    from controller.admin import admin_bp
    from controller.auth_controller import auth_bp
    from controller.chefe_controller import chefe_bp
    from controller.cliente_controller import cliente_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(chefe_bp)
    app.register_blueprint(cliente_bp)
    from controller.cliente_controller import home, menu
    app.add_url_rule("/", endpoint="cliente.home", view_func=home)
    app.add_url_rule("/menu", endpoint="cliente.menu", view_func=menu)
    
    app.jinja_env.filters["moeda"] = formatar_moeda
    app.jinja_env.filters["nome_exibicao"] = nome_exibicao

    @app.before_request
    def exigir_login():
        """Garante que o usuário esteja autenticado antes de acessar rotas privadas.

        Permite o acesso às rotas públicas; para as demais, redireciona ao login
        quando não há usuário na sessão.

        Returns:
            Response | None: redirecionamento para o login quando o acesso é
            negado; None quando a requisição pode prosseguir.
        """
        #app.logger.info("id=%s", session.get("id") or "nada")
        #app.logger.info("cargo=%s", session.get("cargo") or "nada2")

    
        rotas_publicas = {"auth.login", "auth.cadastro", "auth.verificacao", "auth.verificar_token", 
                          "static", "cliente.pagina_inicial", "cliente.home", "cliente.menu", "auth.fazer_login",
                          "auth.fazer_cadastro",
                          # fluxo de navegação do cliente: serviços e carrinho são públicos
                          "cliente.home_servico", "cliente.mostrar_servico",
                          "cliente.mostrar_carrinho", "cliente.adicionar", "cliente.remover"}
        if request.endpoint is None:
            return
        if request.endpoint not in rotas_publicas and "id" not in session:
            return redirect(url_for("auth.login", proxima=request.path))

    @app.before_request
    def verificar_cargo():
        """Restringe o acesso aos blueprints 'admin' e 'chefe' conforme o cargo.

        Aborta com 403 quando o usuário não tem cargo na sessão ou quando o nível de
        permissão é insuficiente para o blueprint acessado.

        Returns:
            Response | None: resposta 403 quando o acesso é proibido; None quando a
            requisição pode prosseguir.
        """
        
        if request.blueprint not in {"admin", "chefe"}:
            return None
        cargo_usuario = session.get("cargo")
        if cargo_usuario is None:
            return abort(403)
        if request.blueprint == "admin" and cargo_usuario < Cargo.ADMIN.value:
            return abort(403)
        if request.blueprint == "chefe" and cargo_usuario < Cargo.CHEFE.value:
            return abort(403)


    @app.errorhandler(400)  # erro do lado do cliente
    def erro_lado_cliente(_erro):
        """Renderiza a página de erro 400 (requisição inválida)."""
        return render_template("400.html"), 400

    @app.errorhandler(404)  # url nao encontrada
    def pagina_nao_encontrada(_erro):
        """Renderiza a página de erro 404 (URL não encontrada)."""
        return render_template("404.html"), 404

    @app.errorhandler(403)  # forbidden
    def proibido(_erro):
        """Renderiza a página de erro 403 (acesso proibido)."""
        return render_template("403.html"), 403

    @app.errorhandler(HTTPException)  # qualquer outro erro HTTP (405, 401, 502, ...)
    def erro_http(erro):
        """Renderiza uma página genérica preservando o código HTTP do erro.

        Respeita o código real da exceção (erro.code) em vez de forçar 500,
        reaproveitando os dados padrão do Werkzeug (code/description).

        Args:
            erro (HTTPException): exceção HTTP levantada pela aplicação.

        Returns:
            tuple: (HTML renderizado, código HTTP original do erro).
        """
        codigo_http = erro.code or 500
        return render_template(
            "erro_generico.html",
            codigo=codigo_http,
            mensagem=erro.name,
            descricao=erro.description,
        ), codigo_http

    @app.errorhandler(Exception)  # erros não-HTTP (bugs inesperados) -> 500
    def erro_inesperado(_erro):
        """Renderiza a página 500 apenas para falhas realmente inesperadas."""
        return render_template("500.html"), 500

    init_database(app)
    mail.init_app(app)

    return app

app = create_app()

if __name__ == "__main__":
    app.run(debug=True)
