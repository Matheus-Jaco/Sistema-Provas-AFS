from datetime import datetime
from flask import Blueprint, render_template, redirect, url_for, flash, request, Response, send_file, make_response
from flask_login import login_required, current_user
import io

from models import db
from models.prova_base import ProvaBase, ProvaBaseQuestao
from models.prova_gerada import ProvaGerada
from models.disciplina import Disciplina
from models.questao import Questao
from services.shuffle_service import gerar_versoes_embaralhadas
from services.export_service import gerar_pdf_prova, gerar_pdf_gabarito, gerar_zip_lote_provas
from services.qr_service import gerar_qrcode_base64

provas_bp = Blueprint('provas', __name__, url_prefix='/provas')

@provas_bp.route('/')
@login_required
def list_provas():
    if current_user.is_coordenacao:
        provas_base = ProvaBase.query.order_by(ProvaBase.criada_em.desc()).all()
        disciplinas = Disciplina.query.order_by(Disciplina.nome).all()
    else:
        disciplinas = current_user.disciplinas_permitidas()
        disciplina_ids = [d.id for d in disciplinas]
        provas_base = ProvaBase.query.filter(ProvaBase.criado_por == current_user.id, ProvaBase.disciplina_id.in_(disciplina_ids)).order_by(ProvaBase.criada_em.desc()).all()

    return render_template('provas/list.html', provas_base=provas_base, disciplinas=disciplinas)

@provas_bp.route('/disciplinas/criar', methods=['POST'])
@login_required
def criar_disciplina():
    if not current_user.is_coordenacao:
        flash('Acesso restrito: somente a coordenação pode cadastrar disciplinas.', 'danger')
        return redirect(url_for('dashboard.index'))

    nome = request.form.get('nome', '').strip()
    codigo = request.form.get('codigo', '').strip()
    descricao = request.form.get('descricao', '').strip()

    if not nome:
        flash('O nome da disciplina é obrigatório.', 'warning')
        return redirect(url_for('provas.list_provas'))

    existente = Disciplina.query.filter_by(nome=nome).first()
    if existente:
        flash(f'A disciplina "{nome}" já existe.', 'info')
        return redirect(url_for('provas.list_provas'))

    nova_disc = Disciplina(nome=nome, codigo=codigo or None, descricao=descricao or None)
    db.session.add(nova_disc)
    db.session.commit()
    flash(f'Disciplina "{nome}" cadastrada com sucesso!', 'success')
    return redirect(url_for('provas.list_provas'))

@provas_bp.route('/criar', methods=['GET', 'POST'])
@login_required
def create():
    disciplinas = current_user.disciplinas_permitidas() if not current_user.is_coordenacao else Disciplina.query.order_by(Disciplina.nome).all()

    if current_user.is_coordenacao:
        questoes_disponiveis = Questao.query.order_by(Questao.criado_em.desc()).all()
    else:
        disciplina_ids = [d.id for d in disciplinas]
        questoes_disponiveis = Questao.query.filter(Questao.disciplina_id.in_(disciplina_ids), Questao.criado_por == current_user.id).order_by(Questao.criado_em.desc()).all()

    if request.method == 'POST':
        titulo = request.form.get('titulo', '').strip()
        disciplina_id = request.form.get('disciplina_id', type=int)
        turma = request.form.get('turma', '').strip()
        data_str = request.form.get('data_aplicacao', '').strip()
        instrucoes = request.form.get('instrucoes', '').strip()

        questoes_ids = request.form.getlist('questoes_ids[]')
        quantidade_x = request.form.get('quantidade_x', type=int, default=1)

        if not titulo or not disciplina_id or not turma:
            flash('Título, disciplina e turma são campos obrigatórios.', 'warning')
            return render_template('provas/create.html', disciplinas=disciplinas, questoes=questoes_disponiveis)
        if not current_user.is_coordenacao and not current_user.pode_acessar_disciplina(disciplina_id):
            flash('Você só pode criar provas para disciplinas atribuídas pela coordenação.', 'danger')
            return render_template('provas/create.html', disciplinas=disciplinas, questoes=questoes_disponiveis)
        if not questoes_ids:
            flash('Selecione pelo menos 1 questão para compor a prova-base.', 'danger')
            return render_template('provas/create.html', disciplinas=disciplinas, questoes=questoes_disponiveis)

        questoes_validas = []
        for q_id in questoes_ids:
            q = Questao.query.get(int(q_id))
            if q and (current_user.is_coordenacao or (q.criado_por == current_user.id and current_user.pode_acessar_disciplina(q.disciplina_id))):
                questoes_validas.append(int(q_id))

        if not questoes_validas:
            flash('Nenhuma questão selecionada está disponível para a sua disciplina atribuída.', 'danger')
            return render_template('provas/create.html', disciplinas=disciplinas, questoes=questoes_disponiveis)

        data_aplicacao = None
        if data_str:
            try:
                data_aplicacao = datetime.strptime(data_str, '%Y-%m-%d').date()
            except ValueError:
                pass

        pb = ProvaBase(
            titulo=titulo,
            disciplina_id=disciplina_id,
            turma=turma,
            data_aplicacao=data_aplicacao,
            instrucoes=instrucoes,
            criado_por=current_user.id
        )
        db.session.add(pb)
        db.session.flush()

        for idx, q_id in enumerate(questoes_validas, start=1):
            pb_q = ProvaBaseQuestao(
                prova_base_id=pb.id,
                questao_id=int(q_id),
                ordem=idx
            )
            db.session.add(pb_q)

        db.session.commit()

        try:
            versoes = gerar_versoes_embaralhadas(pb.id, quantidade_x)
            flash(f'Prova-base criada com sucesso! Foram geradas {len(versoes)} versões embaralhadas com gabaritos e QR-Codes vinculados.', 'success')
            return redirect(url_for('provas.geradas_list', prova_base_id=pb.id))
        except Exception as e:
            flash(f'Prova base salva, mas ocorreu um erro na geração das versões: {str(e)}', 'danger')
            return redirect(url_for('provas.list_provas'))

    return render_template('provas/create.html', disciplinas=disciplinas, questoes=questoes_disponiveis)

@provas_bp.route('/<int:prova_base_id>/versoes')
@login_required
def geradas_list(prova_base_id):
    pb = ProvaBase.query.get_or_404(prova_base_id)
    if not current_user.is_coordenacao and (pb.criado_por != current_user.id or not current_user.pode_acessar_disciplina(pb.disciplina_id)):
        flash('Você não tem permissão para visualizar as versões desta prova.', 'danger')
        return redirect(url_for('provas.list_provas'))

    versoes = ProvaGerada.query.filter_by(prova_base_id=pb.id).order_by(ProvaGerada.numero_versao).all()
    return render_template('provas/geradas_list.html', prova_base=pb, versoes=versoes)

@provas_bp.route('/<int:prova_base_id>/gerar-mais', methods=['POST'])
@login_required
def gerar_mais_versoes(prova_base_id):
    pb = ProvaBase.query.get_or_404(prova_base_id)
    if not current_user.is_coordenacao and (pb.criado_por != current_user.id or not current_user.pode_acessar_disciplina(pb.disciplina_id)):
        flash('Sem permissão para alterar esta prova.', 'danger')
        return redirect(url_for('provas.list_provas'))

    quantidade = request.form.get('quantidade', type=int, default=1)
    
    try:
        gerar_versoes_embaralhadas(pb.id, quantidade)
        flash(f'Geradas mais {quantidade} versões com sucesso!', 'success')
    except Exception as e:
        flash(f'Erro ao gerar versões: {str(e)}', 'danger')
        
    return redirect(url_for('provas.geradas_list', prova_base_id=pb.id))

@provas_bp.route('/versao/<int:prova_gerada_id>')
@login_required
def visualizar_prova(prova_gerada_id):
    pg = ProvaGerada.query.get_or_404(prova_gerada_id)
    pb = pg.prova_base
    if not current_user.is_coordenacao and (pb.criado_por != current_user.id or not current_user.pode_acessar_disciplina(pb.disciplina_id)):
        flash('Sem permissão para visualizar esta versão.', 'danger')
        return redirect(url_for('provas.list_provas'))

    # Ordenar questões embaralhadas
    pg_questoes = sorted(pg.questoes_embaralhadas, key=lambda x: x.ordem_embaralhada)
    
    # Mapear itens embaralhados por questão
    itens_por_questao = {}
    for pgi in pg.itens_embaralhados:
        if pgi.questao_id not in itens_por_questao:
            itens_por_questao[pgi.questao_id] = []
        itens_por_questao[pgi.questao_id].append(pgi)
        
    for q_id in itens_por_questao:
        itens_por_questao[q_id] = sorted(itens_por_questao[q_id], key=lambda x: x.ordem_embaralhada)

    # Gerar QR Code em base64 para a página
    qr_url = f"{request.host_url.rstrip('/')}/gabaritos/qr/{pg.id}"
    qr_code_b64 = gerar_qrcode_base64(qr_url)

    return render_template(
        'provas/visualizar_prova.html',
        prova_gerada=pg,
        pg_questoes=pg_questoes,
        itens_por_questao=itens_por_questao,
        qr_code_b64=qr_code_b64,
        qr_url=qr_url
    )

@provas_bp.route('/versao/<int:prova_gerada_id>/pdf')
@login_required
def download_pdf_prova(prova_gerada_id):
    pg = ProvaGerada.query.get_or_404(prova_gerada_id)
    pb = pg.prova_base
    if not current_user.is_coordenacao and (pb.criado_por != current_user.id or not current_user.pode_acessar_disciplina(pb.disciplina_id)):
        flash('Sem permissão para baixar esta prova.', 'danger')
        return redirect(url_for('provas.list_provas'))

    pdf_bytes = gerar_pdf_prova(pg.id, base_url=request.host_url)
    filename = f"Prova_V{pg.numero_versao:02d}_{pg.codigo_versao}.pdf"
    
    return Response(
        pdf_bytes,
        mimetype='application/pdf',
        headers={'Content-Disposition': f'inline; filename="{filename}"'}
    )

@provas_bp.route('/<int:prova_base_id>/zip')
@login_required
def download_zip_lote(prova_base_id):
    pb = ProvaBase.query.get_or_404(prova_base_id)
    if not current_user.is_coordenacao and (pb.criado_por != current_user.id or not current_user.pode_acessar_disciplina(pb.disciplina_id)):
        flash('Sem permissão para exportar este lote.', 'danger')
        return redirect(url_for('provas.list_provas'))

    zip_bytes = gerar_zip_lote_provas(pb.id, base_url=request.host_url)
    filename = f"Provas_e_Gabaritos_{pb.titulo.replace(' ', '_')}.zip"
    
    return Response(
        zip_bytes,
        mimetype='application/zip',
        headers={'Content-Disposition': f'attachment; filename="{filename}"'}
    )

@provas_bp.route('/excluir/<int:id>', methods=['POST'])
@login_required
def delete(id):
    pb = ProvaBase.query.get_or_404(id)
    if not current_user.is_coordenacao and pb.criado_por != current_user.id:
        flash('Você só pode excluir provas que você mesmo criou.', 'danger')
        return redirect(url_for('provas.list_provas'))

    db.session.delete(pb)
    db.session.commit()
    flash('Prova-base e suas versões geradas foram removidas.', 'info')
    return redirect(url_for('provas.list_provas'))
