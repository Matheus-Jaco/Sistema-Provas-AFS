from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from models import db

class Usuario(UserMixin, db.Model):
    __tablename__ = 'usuarios'

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    senha_hash = db.Column(db.String(255), nullable=False)
    perfil = db.Column(db.Enum('admin', 'coordenador', 'professor', name='perfil_usuario_enum'), default='professor', nullable=False)
    criado_em = db.Column(db.DateTime, default=datetime.utcnow)

    # Relacionamentos
    questoes = db.relationship('Questao', backref='autor', lazy=True, cascade='all, delete-orphan')
    provas_base = db.relationship('ProvaBase', backref='autor', lazy=True, cascade='all, delete-orphan')

    def set_senha(self, senha):
        self.senha_hash = generate_password_hash(senha)

    def check_senha(self, senha):
        return check_password_hash(self.senha_hash, senha)

    @property
    def is_coordenacao(self):
        return self.perfil in ['admin', 'coordenador']

    def __repr__(self):
        return f"<Usuario {self.nome} ({self.email})>"

