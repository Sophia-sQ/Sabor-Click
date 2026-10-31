from flask import Flask, abort, redirect, render_template, request, session, url_for

<<<<<<< Updated upstream
from flask import Flask, redirect, render_template, request, session, url_for, abort

=======
>>>>>>> Stashed changes
from config import config_dict, mail  # importa configurações gerais da aplicação
from database import init_app as init_database
from model.cargos import Cargo
from utils import formatar_moeda


def create_app():
<<<<<<< Updated upstream
    
    app = Flask(__name__, instance_relative_config=True)
    
    app.config.from_object(config_dict['default'])
=======

    app = Flask(__name__, instance_relative_config=True)

    app.config.from_object(config_dict["default"])
>>>>>>> Stashed changes

    from controller.admin import admin_bp
    from controller.auth_controller import auth_bp
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
<<<<<<< Updated upstream
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
            
    
    @app.errorhandler(400)  # erro do lado do cliente
    def pagina_nao_encontrada(_erro):
        return render_template("400.html"), 400
            
=======
        if request.endpoint not in rotas_publicas and "id" not in session:
            return redirect(url_for("auth.login", proxima=request.path))

    @app.before_request
    def verificar_cargo():

        cargo_usuario = session.get("cargo")

        if cargo_usuario is None:
            return abort(403)

        if request.endpoint == "static":
            return None

        if request.blueprint=="admin" and session.get("cargo")<Cargo.ADMIN.value:
            return abort(403)

        if request.blueprint=="chef" and session.get("cargo")<Cargo.CHEFE.value:
            return abort(403)


    @app.errorhandler(400)  # erro do lado do cliente
    def erro_lado_cliente(_erro):
        return render_template("400.html"), 400

>>>>>>> Stashed changes
    @app.errorhandler(404)  # url nao encontrada
    def pagina_nao_encontrada(_erro):
        return render_template("404.html"), 404

    @app.errorhandler(403)  # forbidden
    def proibido(_erro):
        return render_template("403.html"), 403
<<<<<<< Updated upstream
    
    @app.errorhandler(Exception)  # pagina de erro padrão
    def default(_erro):
        return render_template("500.html")
               
    init_database(app)
    mail.init_app(app) 
    
=======

    @app.errorhandler(Exception)  # pagina de erro padrão
    def default(_erro):
        return render_template("500.html"), 500

    init_database(app)
    mail.init_app(app)

>>>>>>> Stashed changes
    return app

app = create_app()

if __name__ == "__main__":
    app.run(debug=True) # FIXME: apagar ao final do desenvolvimento
