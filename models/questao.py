from datetime import datetime
from models import db

class Questao(db.Model):
    __tablename__ = 'questoes'

    id = db.Column(db.Integer, primary_key=True)
    enunciado = db.Column(db.Text, nullable=False)
    disciplina_id = db.Column(db.Integer, db.ForeignKey('disciplinas.id', ondelete='CASCADE'), nullable=False)
    tipo = db.Column(db.Enum('multipla_escolha', 'verdadeiro_falso', name='tipo_questao_enum'), default='multipla_escolha', nullable=False)
    dificuldade = db.Column(db.Enum('facil', 'media', 'dificil', name='dificuldade_enum'), default='media', nullable=False)
    tags = db.Column(db.String(255), nullable=True) # Tags separadas por vírgula
    criado_por = db.Column(db.Integer, db.ForeignKey('usuarios.id', ondelete='CASCADE'), nullable=False)
    criado_em = db.Column(db.DateTime, default=datetime.utcnow)

    # Relacionamentos
    itens = db.relationship('Item', backref='questao', lazy=True, cascade='all, delete-orphan', order_by='Item.ordem_original')

    @property
    def item_correto(self):
        for item in self.itens:
            if item.correta:
                return item
        return None

    def __repr__(self):
        return f"<Questao #{self.id} - {self.enunciado[:30]}...>"
