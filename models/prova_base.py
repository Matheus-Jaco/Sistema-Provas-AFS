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
    disciplinas_associadas = db.relationship('ProvaBaseDisciplina', backref='prova_base', lazy=True, cascade='all, delete-orphan', order_by='ProvaBaseDisciplina.ordem')
    configuracao = db.relationship('ProvaBaseConfiguracao', backref='prova_base', uselist=False, lazy=True, cascade='all, delete-orphan')

    @property
    def embaralhar_blocos(self):
        return bool(self.configuracao and self.configuracao.embaralhar_blocos)

    @property
    def disciplina_ids(self):
        if self.disciplinas_associadas:
            return {bloco.disciplina_id for bloco in self.disciplinas_associadas}
        return {self.disciplina_id}

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


class ProvaBaseDisciplina(db.Model):
    __tablename__ = 'provas_base_disciplinas'

    id = db.Column(db.Integer, primary_key=True)
    prova_base_id = db.Column(db.Integer, db.ForeignKey('provas_base.id', ondelete='CASCADE'), nullable=False)
    disciplina_id = db.Column(db.Integer, db.ForeignKey('disciplinas.id', ondelete='CASCADE'), nullable=False)
    ordem = db.Column(db.Integer, nullable=False, default=1)

    disciplina = db.relationship('Disciplina', lazy=True)


class ProvaBaseConfiguracao(db.Model):
    __tablename__ = 'provas_base_configuracoes'

    prova_base_id = db.Column(db.Integer, db.ForeignKey('provas_base.id', ondelete='CASCADE'), primary_key=True)
    embaralhar_blocos = db.Column(db.Boolean, nullable=False, default=False)
