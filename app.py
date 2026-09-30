from flask import Flask, redirect, render_template, request, session, url_for

from config import Config  # importa configurações gerais da aplicação
from database import init_app as init_database
from utils import formatar_moeda

from model.cargos import Cargo

def create_app(test_config=None):

    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(Config)
    if test_config: 
        app.config.update(test_config)

        from controllers.auth_controller import auth_bp
        from controllers.compra_controller import compra_bp
        from controllers.main_controller import main_bp
        from controllers.produto_controller import produto_bp

        app.register_blueprint(auth_bp)
        app.register_blueprint(main_bp)
        app.register_blueprint(produto_bp)
        app.register_blueprint(compra_bp)

        app.jinja_env.filters["moeda"] = formatar_moeda

        @app.before_request
        def exigir_login():
            rotas_publicas = {"auth.login", "auth.cadastro", "static"}
            if request.endpoint not in rotas_publicas and "usuario_id" not in session:
                return redirect(url_for("auth.login", proxima=request.path))

        @app.before_request
        def verificar_cargo():
            if request.endpoint == 'static':
            if request.blueprint=="admin" and session.get("cargo")<Cargo.ADMIN:
                return abort(403)
            if request.blueprint=="chef" and session.get("cargo")<Cargo.CHEF:
                return abort(403)
                
                
        @app.errorhandler(404)  # url nao encontrada
        def pagina_nao_encontrada(_erro):
            return render_template("404.html"), 404

        @app.errorhandler(403)  # forbidden
        def proibido(_erro):
            return render_template("403.html"), 403

                   
        init_database(app)
        return app

        
app = create_app()

if __name__ == "__main__":
    app.run(debug=True)
