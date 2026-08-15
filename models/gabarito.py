from models import db

class Gabarito(db.Model):
    __tablename__ = 'gabaritos'

    id = db.Column(db.Integer, primary_key=True)
    prova_gerada_id = db.Column(db.Integer, db.ForeignKey('provas_geradas.id', ondelete='CASCADE'), nullable=False)
    numero_questao = db.Column(db.Integer, nullable=False)
    questao_id = db.Column(db.Integer, db.ForeignKey('questoes.id', ondelete='CASCADE'), nullable=False)
    item_correto_id = db.Column(db.Integer, db.ForeignKey('itens.id', ondelete='CASCADE'), nullable=False)
    letra_correta = db.Column(db.String(5), nullable=False)

    questao = db.relationship('Questao', lazy=True)
    item_correto = db.relationship('Item', lazy=True)

    def __repr__(self):
        return f"<Gabarito Q{self.numero_questao} -> {self.letra_correta} (ProvaGerada #{self.prova_gerada_id})>"
