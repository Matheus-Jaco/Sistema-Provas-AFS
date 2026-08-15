from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from models import db
from models.questao import Questao
from models.item import Item
from models.disciplina import Disciplina

questoes_bp = Blueprint('questoes', __name__, url_prefix='/questoes')

@questoes_bp.route('/disciplinas/criar', methods=['POST'])
@login_required
def criar_disciplina_rapida():
    if request.is_json:
        data = request.get_json()
        nome = data.get('nome', '').strip()
        codigo = data.get('codigo', '').strip()
        descricao = data.get('descricao', '').strip()
    else:
        nome = request.form.get('nome', '').strip()
        codigo = request.form.get('codigo', '').strip()
        descricao = request.form.get('descricao', '').strip()

    if not nome:
        if request.is_json:
            return jsonify({'success': False, 'message': 'O nome da disciplina é obrigatório.'}), 400
        flash('O nome da disciplina é obrigatório.', 'warning')
        return redirect(request.referrer or url_for('questoes.list_questoes'))

    existente = Disciplina.query.filter_by(nome=nome).first()
    if existente:
        if request.is_json:
            return jsonify({'success': True, 'id': existente.id, 'nome': existente.nome, 'message': 'Disciplina já existente selecionada.'})
        flash(f'A disciplina "{nome}" já existe.', 'info')
        return redirect(request.referrer or url_for('questoes.list_questoes'))

    nova_disc = Disciplina(nome=nome, codigo=codigo or None, descricao=descricao or None)
    db.session.add(nova_disc)
    db.session.commit()

    if request.is_json:
        return jsonify({'success': True, 'id': nova_disc.id, 'nome': nova_disc.nome, 'message': 'Disciplina criada com sucesso!'})

    flash(f'Disciplina "{nome}" cadastrada com sucesso!', 'success')
    return redirect(request.referrer or url_for('questoes.list_questoes'))

@questoes_bp.route('/')
@login_required
def list_questoes():
    disciplina_id = request.args.get('disciplina_id', type=int)
    dificuldade = request.args.get('dificuldade', type=str)
    busca = request.args.get('busca', type=str, default='').strip()

    query = Questao.query

    if disciplina_id:
        query = query.filter(Questao.disciplina_id == disciplina_id)
    if dificuldade:
        query = query.filter(Questao.dificuldade == dificuldade)
    if busca:
        query = query.filter((Questao.enunciado.ilike(f'%{busca}%')) | (Questao.tags.ilike(f'%{busca}%')))

    questoes = query.order_by(Questao.criado_em.desc()).all()
    disciplinas = Disciplina.query.order_by(Disciplina.nome).all()

    return render_template(
        'questoes/list.html',
        questoes=questoes,
        disciplinas=disciplinas,
        disciplina_id=disciplina_id,
        dificuldade=dificuldade,
        busca=busca
    )

@questoes_bp.route('/criar', methods=['GET', 'POST'])
@login_required
def create():
    disciplinas = Disciplina.query.order_by(Disciplina.nome).all()

    if request.method == 'POST':
        enunciado = request.form.get('enunciado', '').strip()
        disciplina_id = request.form.get('disciplina_id', type=int)
        tipo = request.form.get('tipo', 'multipla_escolha')
        dificuldade = request.form.get('dificuldade', 'media')
        tags = request.form.get('tags', '').strip()

        # Validação backend
        if not enunciado:
            flash('O enunciado da questão é obrigatório.', 'warning')
            return render_template('questoes/create.html', disciplinas=disciplinas)
        if not disciplina_id:
            flash('Selecione uma disciplina válida.', 'warning')
            return render_template('questoes/create.html', disciplinas=disciplinas)

        # Capturar itens/alternativas
        itens_textos = request.form.getlist('item_texto[]')
        item_correto_idx = request.form.get('item_correto', type=int, default=0)

        itens_validos = [t.strip() for t in itens_textos if t.strip()]
        if len(itens_validos) < 2:
            flash('A questão precisa ter no mínimo 2 alternativas/itens cadastrados.', 'danger')
            return render_template('questoes/create.html', disciplinas=disciplinas)

        nueva_questao = Questao(
            enunciado=enunciado,
            disciplina_id=disciplina_id,
            tipo=tipo,
            dificuldade=dificuldade,
            tags=tags,
            criado_por=current_user.id
        )
        db.session.add(nueva_questao)
        db.session.flush()

        for idx, texto in enumerate(itens_validos):
            is_correta = (idx == item_correto_idx)
            item = Item(
                questao_id=nueva_questao.id,
                texto=texto,
                correta=is_correta,
                ordem_original=idx + 1
            )
            db.session.add(item)

        db.session.commit()
        flash('Questão cadastrada com sucesso no banco de questões!', 'success')
        return redirect(url_for('questoes.list_questoes'))

    return render_template('questoes/create.html', disciplinas=disciplinas)

@questoes_bp.route('/editar/<int:id>', methods=['GET', 'POST'])
@login_required
def edit(id):
    questao = Questao.query.get_or_404(id)
    disciplinas = Disciplina.query.order_by(Disciplina.nome).all()

    if request.method == 'POST':
        enunciado = request.form.get('enunciado', '').strip()
        disciplina_id = request.form.get('disciplina_id', type=int)
        tipo = request.form.get('tipo', 'multipla_escolha')
        dificuldade = request.form.get('dificuldade', 'media')
        tags = request.form.get('tags', '').strip()

        if not enunciado or not disciplina_id:
            flash('Enunciado e disciplina são campos obrigatórios.', 'warning')
            return render_template('questoes/edit.html', questao=questao, disciplinas=disciplinas)

        itens_textos = request.form.getlist('item_texto[]')
        item_correto_idx = request.form.get('item_correto', type=int, default=0)

        itens_validos = [t.strip() for t in itens_textos if t.strip()]
        if len(itens_validos) < 2:
            flash('A questão precisa ter no mínimo 2 alternativas válidas.', 'danger')
            return render_template('questoes/edit.html', questao=questao, disciplinas=disciplinas)

        questao.enunciado = enunciado
        questao.disciplina_id = disciplina_id
        questao.tipo = tipo
        questao.dificuldade = dificuldade
        questao.tags = tags

        # Atualizar itens
        Item.query.filter_by(questao_id=questao.id).delete()
        for idx, texto in enumerate(itens_validos):
            is_correta = (idx == item_correto_idx)
            item = Item(
                questao_id=questao.id,
                texto=texto,
                correta=is_correta,
                ordem_original=idx + 1
            )
            db.session.add(item)

        db.session.commit()
        flash('Questão atualizada com sucesso!', 'success')
        return redirect(url_for('questoes.list_questoes'))

    return render_template('questoes/edit.html', questao=questao, disciplinas=disciplinas)

@questoes_bp.route('/excluir/<int:id>', methods=['POST'])
@login_required
def delete(id):
    questao = Questao.query.get_or_404(id)
    db.session.delete(questao)
    db.session.commit()
    flash('Questão removida do banco de dados.', 'info')
    return redirect(url_for('questoes.list_questoes'))
