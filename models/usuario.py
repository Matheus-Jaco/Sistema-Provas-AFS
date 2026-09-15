from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from models import db

usuario_disciplinas = db.Table(
    'usuario_disciplinas',
    db.Column('usuario_id', db.Integer, db.ForeignKey('usuarios.id', ondelete='CASCADE'), primary_key=True),
    db.Column('disciplina_id', db.Integer, db.ForeignKey('disciplinas.id', ondelete='CASCADE'), primary_key=True)
)

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
    disciplinas = db.relationship('Disciplina', secondary=usuario_disciplinas, back_populates='professores', lazy='select')

    def set_senha(self, senha):
        self.senha_hash = generate_password_hash(senha)

    def check_senha(self, senha):
        return check_password_hash(self.senha_hash, senha)

    @property
    def is_coordenacao(self):
        return self.perfil in ['admin', 'coordenador']

    def disciplinas_permitidas(self):
        from models.disciplina import Disciplina
        if self.is_coordenacao:
            return Disciplina.query.order_by(Disciplina.nome).all()
        return sorted(self.disciplinas, key=lambda d: d.nome)

    def disciplina_ids_permitidos(self):
        return {disc.id for disc in self.disciplinas_permitidas()}

    def pode_acessar_disciplina(self, disciplina_id):
        return disciplina_id in self.disciplina_ids_permitidos()

    def __repr__(self):
        return f"<Usuario {self.nome} ({self.email})>"

