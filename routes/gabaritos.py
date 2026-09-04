from flask import Blueprint, render_template, redirect, url_for, flash, Response, request
from flask_login import login_required, current_user
from models.prova_gerada import ProvaGerada
from models.prova_base import ProvaBase
from services.export_service import gerar_pdf_gabarito

gabaritos_bp = Blueprint('gabaritos', __name__, url_prefix='/gabaritos')

@gabaritos_bp.route('/versao/<int:prova_gerada_id>')
@login_required
def visualizar(prova_gerada_id):
    pg = ProvaGerada.query.get_or_404(prova_gerada_id)
    pb = pg.prova_base
    if not current_user.is_coordenacao and pb.criado_por != current_user.id:
        flash('Você só tem acesso aos gabaritos das suas próprias provas.', 'danger')
        return redirect(url_for('provas.list_provas'))

    gabaritos = sorted(pg.gabaritos, key=lambda x: x.numero_questao)
    return render_template('gabaritos/visualizar.html', prova_gerada=pg, gabaritos=gabaritos)

@gabaritos_bp.route('/qr/<int:prova_gerada_id>')
@gabaritos_bp.route('/qr/codigo/<string:codigo_versao>')
def consulta_qrcode(prova_gerada_id=None, codigo_versao=None):
    """
    Rota pública otimizada para leitura via QR-Code (celular ou desktop)
    Permite conferência direta do gabarito oficial da versão da prova.
    """
    if prova_gerada_id:
        pg = ProvaGerada.query.get_or_404(prova_gerada_id)
    elif codigo_versao:
        pg = ProvaGerada.query.filter_by(codigo_versao=codigo_versao).first_or_404()
    else:
        return redirect(url_for('auth.login'))

    gabaritos = sorted(pg.gabaritos, key=lambda x: x.numero_questao)
    return render_template('gabaritos/qrcode_view.html', prova_gerada=pg, gabaritos=gabaritos)

@gabaritos_bp.route('/base/<int:prova_base_id>/matriz')
@login_required
def matriz(prova_base_id):
    pb = ProvaBase.query.get_or_404(prova_base_id)
    if not current_user.is_coordenacao and pb.criado_por != current_user.id:
        flash('Você só tem acesso à matriz de gabarito das suas próprias provas.', 'danger')
        return redirect(url_for('provas.list_provas'))

    versoes = sorted(pb.versoes_geradas, key=lambda v: v.numero_versao)

    # Coletar número de questões
    total_questoes = len(pb.questoes_associadas)

    # Estruturar matriz: [ {versao: pg, gabarito_dict: {1: 'C', 2: 'A', ...}} ]
    matriz_gabaritos = []
    for v in versoes:
        mapa_g = {g.numero_questao: g.letra_correta for g in v.gabaritos}
        matriz_gabaritos.append({
            'versao': v,
            'mapa': mapa_g
        })

    return render_template('gabaritos/matriz.html', prova_base=pb, total_questoes=total_questoes, matriz=matriz_gabaritos)

@gabaritos_bp.route('/versao/<int:prova_gerada_id>/pdf')
@login_required
def download_pdf_gabarito(prova_gerada_id):
    pg = ProvaGerada.query.get_or_404(prova_gerada_id)
    pb = pg.prova_base
    if not current_user.is_coordenacao and pb.criado_por != current_user.id:
        flash('Sem permissão para baixar este gabarito.', 'danger')
        return redirect(url_for('provas.list_provas'))

    pdf_bytes = gerar_pdf_gabarito(pg.id)
    filename = f"Gabarito_V{pg.numero_versao:02d}_{pg.codigo_versao}.pdf"

    return Response(
        pdf_bytes,
        mimetype='application/pdf',
        headers={'Content-Disposition': f'inline; filename="{filename}"'}
    )
