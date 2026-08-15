from flask import Blueprint, render_template
from flask_login import login_required, current_user
from models.questao import Questao
from models.disciplina import Disciplina
from models.prova_base import ProvaBase
from models.prova_gerada import ProvaGerada

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/')
@login_required
def index():
    total_questoes = Questao.query.count()
    total_disciplinas = Disciplina.query.count()
    total_provas_base = ProvaBase.query.count()
    total_provas_geradas = ProvaGerada.query.count()

    ultimas_provas_base = ProvaBase.query.order_by(ProvaBase.criada_em.desc()).limit(5).all()
    ultimas_questoes = Questao.query.order_by(Questao.criado_em.desc()).limit(5).all()

    return render_template(
        'dashboard/index.html',
        total_questoes=total_questoes,
        total_disciplinas=total_disciplinas,
        total_provas_base=total_provas_base,
        total_provas_geradas=total_provas_geradas,
        ultimas_provas_base=ultimas_provas_base,
        ultimas_questoes=ultimas_questoes
    )
