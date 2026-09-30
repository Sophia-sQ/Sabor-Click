from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase

#classe base: Não contém nada, pois utiliza o padrão do Python
class Base(DeclarativeBase):
    pass


db = SQLAlchemy(model_class=Base)

# Inicializa o banco
def init_app(app):
    db.init_app(app)
    
    # Cria automaticamente todas as tabelas no arquivo do banco se elas não existirem
    with app.app_context():
        db.create_all()