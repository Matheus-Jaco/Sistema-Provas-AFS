from functools import wraps
from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
from flask_login import login_required, current_user
from models import db
from models.usuario import Usuario
from models.disciplina import Disciplina

professores_bp = Blueprint('professores', __name__, url_prefix='/professores')

def coordenacao_required(f):
    @wraps(f)
    @login_required
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_coordenacao:
            flash('Acesso restrito. Apenas a CoordenaçãoProvas pode gerenciar contas de professores.', 'danger')
            return redirect(url_for('dashboard.index'))
        return f(*args, **kwargs)
    return decorated_function

@professores_bp.route('/')
@coordenacao_required
def list_professores():
    professores = Usuario.query.filter_by(perfil='professor').order_by(Usuario.nome).all()
    coordenadores = Usuario.query.filter(Usuario.perfil.in_(['admin', 'coordenador'])).order_by(Usuario.nome).all()
    return render_template('professores/list.html', professores=professores, coordenadores=coordenadores)

@professores_bp.route('/criar', methods=['GET', 'POST'])
@coordenacao_required
def create():
    disciplinas = Disciplina.query.order_by(Disciplina.nome).all()

    if request.method == 'POST':
        nome = request.form.get('nome', '').strip()
        email = request.form.get('email', '').strip().lower()
        senha = request.form.get('senha', '').strip()
        perfil = request.form.get('perfil', 'professor').strip()
        disciplinas_ids = request.form.getlist('disciplinas')

        if not nome or not email or not senha:
            flash('Preencha todos os campos obrigatórios (Nome, E-mail e Senha).', 'warning')
            return render_template('professores/create.html', disciplinas=disciplinas, nome=nome, email=email)

        # Verificar se email já existe
        existente = Usuario.query.filter_by(email=email).first()
        if existente:
            flash(f'O e-mail "{email}" já está cadastrado no sistema.', 'danger')
            return render_template('professores/create.html', disciplinas=disciplinas, nome=nome, email=email)

        if perfil == 'professor' and not disciplinas_ids:
            flash('Selecione pelo menos uma disciplina para o professor.', 'warning')
            return render_template('professores/create.html', disciplinas=disciplinas, nome=nome, email=email)

        novo_usuario = Usuario(
            nome=nome,
            email=email,
            perfil=perfil if perfil in ['professor', 'coordenador', 'admin'] else 'professor'
        )
        novo_usuario.set_senha(senha)

        if perfil == 'professor':
            novas_disciplinas = Disciplina.query.filter(Disciplina.id.in_([int(d) for d in disciplinas_ids if d])).all()
            novo_usuario.disciplinas = novas_disciplinas

        db.session.add(novo_usuario)
        db.session.commit()

        flash(f'Conta do(a) professor(a) "{nome}" criada com sucesso pela CoordenaçãoProvas! O login já está liberado.', 'success')
        return redirect(url_for('professores.list_professores'))

    return render_template('professores/create.html', disciplinas=disciplinas)

@professores_bp.route('/editar/<int:id>', methods=['GET', 'POST'])
@coordenacao_required
def edit(id):
    usuario = Usuario.query.get_or_404(id)
    disciplinas = Disciplina.query.order_by(Disciplina.nome).all()

    if request.method == 'POST':
        nome = request.form.get('nome', '').strip()
        email = request.form.get('email', '').strip().lower()
        nova_senha = request.form.get('senha', '').strip()
        perfil = request.form.get('perfil', usuario.perfil).strip()
        disciplinas_ids = request.form.getlist('disciplinas')

        if not nome or not email:
            flash('Nome e e-mail são obrigatórios.', 'warning')
            return render_template('professores/edit.html', usuario=usuario, disciplinas=disciplinas)

        # Checar se email já é usado por outro usuário
        email_outro = Usuario.query.filter(Usuario.email == email, Usuario.id != usuario.id).first()
        if email_outro:
            flash(f'O e-mail "{email}" já está em uso por outra conta.', 'danger')
            return render_template('professores/edit.html', usuario=usuario, disciplinas=disciplinas)

        if perfil == 'professor' and not disciplinas_ids:
            flash('Selecione pelo menos uma disciplina atribuída ao professor.', 'warning')
            return render_template('professores/edit.html', usuario=usuario, disciplinas=disciplinas)

        usuario.nome = nome
        usuario.email = email
        if perfil in ['professor', 'coordenador', 'admin']:
            usuario.perfil = perfil

        if perfil == 'professor':
            usuario.disciplinas = Disciplina.query.filter(Disciplina.id.in_([int(d) for d in disciplinas_ids if d])).all()
        else:
            usuario.disciplinas = []

        if nova_senha:
            usuario.set_senha(nova_senha)

        db.session.commit()
        flash(f'Dados de "{usuario.nome}" atualizados com sucesso.', 'success')
        return redirect(url_for('professores.list_professores'))

    return render_template('professores/edit.html', usuario=usuario, disciplinas=disciplinas)

@professores_bp.route('/excluir/<int:id>', methods=['POST'])
@coordenacao_required
def delete(id):
    usuario = Usuario.query.get_or_404(id)
    if usuario.id == current_user.id:
        flash('Você não pode excluir sua própria conta enquanto estiver conectado.', 'warning')
        return redirect(url_for('professores.list_professores'))

    nome = usuario.nome
    db.session.delete(usuario)
    db.session.commit()
    flash(f'Conta do(a) professor(a) "{nome}" e seus dados foram excluídos.', 'info')
    return redirect(url_for('professores.list_professores'))
