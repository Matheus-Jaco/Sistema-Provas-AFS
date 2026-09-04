import os
from flask import Flask, redirect, url_for
from flask_login import LoginManager

from config import Config
from models import db
from models.usuario import Usuario
from models.disciplina import Disciplina
from models.questao import Questao
from models.item import Item
from models.prova_base import ProvaBase, ProvaBaseQuestao
from models.prova_gerada import ProvaGerada, ProvaGeradaQuestao, ProvaGeradaItem
from models.gabarito import Gabarito

from routes.auth import auth_bp
from routes.dashboard import dashboard_bp
from routes.questoes import questoes_bp
from routes.provas import provas_bp
from routes.gabaritos import gabaritos_bp
from routes.professores import professores_bp

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Inicializar extensões
    db.init_app(app)

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Por favor, realize o login para acessar esta área.'
    login_manager.login_message_category = 'warning'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return Usuario.query.get(int(user_id))

    # Registrar Blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(questoes_bp)
    app.register_blueprint(provas_bp)
    app.register_blueprint(gabaritos_bp)
    app.register_blueprint(professores_bp)

    # Inicialização de tabelas e usuário admin padrão
    with app.app_context():
        try:
            db.create_all()
            _inicializar_dados_padrao()
        except Exception as e:
            app.logger.error(f"Erro ao inicializar o banco de dados: {e}")

    return app

def _inicializar_dados_padrao():
    """
    Cria a conta da CoordenaçãoProvas e disciplinas de exemplo se o banco estiver vazio.
    """
    if Usuario.query.count() == 0:
        coordenacao = Usuario(
            nome="Coordenação Provas",
            email="admin@escola.edu.br",
            perfil="admin"
        )
        coordenacao.set_senha("admin123")
        db.session.add(coordenacao)

        prof = Usuario(
            nome="Prof. Carlos Silva",
            email="carlos@escola.edu.br",
            perfil="professor"
        )
        prof.set_senha("prof123")
        db.session.add(prof)

        db.session.commit()

    if Disciplina.query.count() == 0:
        mat = Disciplina(nome="Matemática", codigo="MAT-100", descricao="Álgebra, Geometria e Estatística")
        fis = Disciplina(nome="Física", codigo="FIS-100", descricao="Mecânica, Termodinâmica e Eletromagnetismo")
        his = Disciplina(nome="História", codigo="HIS-100", descricao="História do Brasil e História Geral")
        
        db.session.add_all([mat, fis, his])
        db.session.commit()

app = create_app()

if __name__ == '__main__':
    print("[INFO] Iniciando Servidor CoordenaçãoProvas em http://127.0.0.1:5000 ...")
    app.run(host='127.0.0.1', port=5000, debug=True)
