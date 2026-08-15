from models import db

class Item(db.Model):
    __tablename__ = 'itens'

    id = db.Column(db.Integer, primary_key=True)
    questao_id = db.Column(db.Integer, db.ForeignKey('questoes.id', ondelete='CASCADE'), nullable=False)
    texto = db.Column(db.Text, nullable=False)
    correta = db.Column(db.Boolean, default=False, nullable=False)
    ordem_original = db.Column(db.Integer, default=1, nullable=False)

    def __repr__(self):
        return f"<Item #{self.id} (Questao #{self.questao_id}) - Correta: {self.correta}>"
