from datetime import datetime
from models import db

class ProvaGerada(db.Model):
    __tablename__ = 'provas_geradas'

    id = db.Column(db.Integer, primary_key=True)
    prova_base_id = db.Column(db.Integer, db.ForeignKey('provas_base.id', ondelete='CASCADE'), nullable=False)
    codigo_versao = db.Column(db.String(50), unique=True, nullable=False)
    numero_versao = db.Column(db.Integer, nullable=False)
    seed = db.Column(db.String(64), nullable=True)
    criada_em = db.Column(db.DateTime, default=datetime.utcnow)

    # Relacionamentos
    questoes_embaralhadas = db.relationship('ProvaGeradaQuestao', backref='prova_gerada', lazy=True, cascade='all, delete-orphan', order_by='ProvaGeradaQuestao.ordem_embaralhada')
    itens_embaralhados = db.relationship('ProvaGeradaItem', backref='prova_gerada', lazy=True, cascade='all, delete-orphan', order_by='ProvaGeradaItem.ordem_embaralhada')
    gabaritos = db.relationship('Gabarito', backref='prova_gerada', lazy=True, cascade='all, delete-orphan', order_by='Gabarito.numero_questao')

    def __repr__(self):
        return f"<ProvaGerada Versao #{self.numero_versao} - Codigo: {self.codigo_versao}>"

class ProvaGeradaQuestao(db.Model):
    __tablename__ = 'provas_geradas_questoes'

    id = db.Column(db.Integer, primary_key=True)
    prova_gerada_id = db.Column(db.Integer, db.ForeignKey('provas_geradas.id', ondelete='CASCADE'), nullable=False)
    questao_id = db.Column(db.Integer, db.ForeignKey('questoes.id', ondelete='CASCADE'), nullable=False)
    ordem_embaralhada = db.Column(db.Integer, nullable=False)

    questao = db.relationship('Questao', lazy=True)

class ProvaGeradaItem(db.Model):
    __tablename__ = 'provas_geradas_itens'

    id = db.Column(db.Integer, primary_key=True)
    prova_gerada_id = db.Column(db.Integer, db.ForeignKey('provas_geradas.id', ondelete='CASCADE'), nullable=False)
    questao_id = db.Column(db.Integer, db.ForeignKey('questoes.id', ondelete='CASCADE'), nullable=False)
    item_id = db.Column(db.Integer, db.ForeignKey('itens.id', ondelete='CASCADE'), nullable=False)
    ordem_embaralhada = db.Column(db.Integer, nullable=False)
    letra_atribuida = db.Column(db.String(5), nullable=False)

    item = db.relationship('Item', lazy=True)
