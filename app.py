from os import environ as env

from flask import Flask, redirect, render_template, request, session, url_for, abort

from config import config_dict  # importa configurações gerais da aplicação
from database import init_app as init_database
from utils import formatar_moeda

from model.cargos import Cargo

def create_app(test_config=None):
    
    app = Flask(__name__, instance_relative_config=True)
    
    app.config.from_object(config_dict['default'])

    from controller.auth_controller import auth_bp
    from controller.admin_controller import admin_bp
    from controller.chefe_controller import chefe_bp
    from controller.cliente_controller import cliente_bp
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(chefe_bp)
    app.register_blueprint(cliente_bp)
    
    app.jinja_env.filters["moeda"] = formatar_moeda
    
    @app.before_request
    def exigir_login():
        rotas_publicas = {"auth.login", "auth.cadastro", "static", "cliente.pagina_inicial"}
        if request.endpoint not in rotas_publicas and "usuario_id" not in session:
            return redirect(url_for("auth.login", proxima=request.path))
        
    @app.before_request
    def verificar_cargo():
        if request.endpoint == 'static':
            return
        
        if request.blueprint=="admin" and session.get("cargo")<Cargo.ADMIN.value:
            return abort(403)
        
        if request.blueprint=="chef" and session.get("cargo")<Cargo.CHEFE.value:
            return abort(403)
            
            
    @app.errorhandler(404)  # url nao encontrada
    def pagina_nao_encontrada(_erro):
        return render_template("404.html"), 404
    
    @app.errorhandler(403)  # forbidden
    def proibido(_erro):
        return render_template("403.html"), 403
    
    @app.errorhandler(Exception)  # forbidden
    def default(_erro):
        return render_template("500.html")
               
    init_database(app)
    return app

app = create_app()

if __name__ == "__main__":
    app.run(debug=True) # FIXME: apagar ao final do desenvolvimento
