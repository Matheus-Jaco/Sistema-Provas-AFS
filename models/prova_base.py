from datetime import datetime
from models import db

class ProvaBase(db.Model):
    __tablename__ = 'provas_base'

    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(150), nullable=False)
    disciplina_id = db.Column(db.Integer, db.ForeignKey('disciplinas.id', ondelete='CASCADE'), nullable=False)
    turma = db.Column(db.String(50), nullable=False)
    data_aplicacao = db.Column(db.Date, nullable=True)
    instrucoes = db.Column(db.Text, nullable=True)
    criado_por = db.Column(db.Integer, db.ForeignKey('usuarios.id', ondelete='CASCADE'), nullable=False)
    criada_em = db.Column(db.DateTime, default=datetime.utcnow)

    # Relacionamentos
    questoes_associadas = db.relationship('ProvaBaseQuestao', backref='prova_base', lazy=True, cascade='all, delete-orphan', order_by='ProvaBaseQuestao.ordem')
    versoes_geradas = db.relationship('ProvaGerada', backref='prova_base', lazy=True, cascade='all, delete-orphan')

    def __repr__(self):
        return f"<ProvaBase #{self.id} - {self.titulo}>"

class ProvaBaseQuestao(db.Model):
    __tablename__ = 'provas_base_questoes'

    id = db.Column(db.Integer, primary_key=True)
    prova_base_id = db.Column(db.Integer, db.ForeignKey('provas_base.id', ondelete='CASCADE'), nullable=False)
    questao_id = db.Column(db.Integer, db.ForeignKey('questoes.id', ondelete='CASCADE'), nullable=False)
    ordem = db.Column(db.Integer, default=1, nullable=False)
    valor_pontos = db.Column(db.Numeric(4, 2), default=1.00)

    questao = db.relationship('Questao', lazy=True)
