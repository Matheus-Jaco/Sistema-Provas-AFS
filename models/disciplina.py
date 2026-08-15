from datetime import datetime
from models import db

class Disciplina(db.Model):
    __tablename__ = 'disciplinas'

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), unique=True, nullable=False)
    codigo = db.Column(db.String(20), unique=True, nullable=True)
    descricao = db.Column(db.String(255), nullable=True)
    criada_em = db.Column(db.DateTime, default=datetime.utcnow)

    # Relacionamentos
    questoes = db.relationship('Questao', backref='disciplina', lazy=True, cascade='all, delete-orphan')
    provas_base = db.relationship('ProvaBase', backref='disciplina', lazy=True, cascade='all, delete-orphan')

    def __repr__(self):
        return f"<Disciplina {self.nome}>"
