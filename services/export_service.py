import io
import zipfile
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, HRFlowable, KeepTogether
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY

from models.prova_gerada import ProvaGerada
from models.prova_base import ProvaBase
from services.qr_service import gerar_qrcode_flowable

def gerar_pdf_prova(prova_gerada_id, base_url="http://127.0.0.1:5000"):
    """
    Gera um buffer de memória de arquivo PDF formatado para impressão da prova do aluno,
    incluindo no final o Cartão-Resposta (Gabarito do Aluno) com QR-Code vinculado à prova.
    """
    prova_gerada = ProvaGerada.query.get(prova_gerada_id)
    if not prova_gerada:
        raise ValueError("Prova gerada não encontrada.")

    prova_base = prova_gerada.prova_base
    buffer = io.BytesIO()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36
    )

    styles = getSampleStyleSheet()

    # Estilos customizados institucionais
    header_title_style = ParagraphStyle(
        'HeaderTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=13,
        leading=16,
        alignment=TA_CENTER,
        textColor=colors.HexColor('#0f172a')
    )

    header_sub_style = ParagraphStyle(
        'HeaderSub',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=12,
        alignment=TA_CENTER,
        textColor=colors.HexColor('#475569')
    )

    body_style = ParagraphStyle(
        'ExamBody',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        leading=14,
        textColor=colors.HexColor('#1e293b')
    )

    enunciado_style = ParagraphStyle(
        'EnunciadoStyle',
        parent=body_style,
        fontName='Helvetica-Bold',
        spaceBefore=8,
        spaceAfter=4
    )

    opcao_style = ParagraphStyle(
        'OpcaoStyle',
        parent=body_style,
        leftIndent=15,
        spaceBefore=2,
        spaceAfter=2
    )

    cartao_title_style = ParagraphStyle(
        'CartaoTitle',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=11,
        leading=14,
        alignment=TA_CENTER,
        textColor=colors.HexColor('#0f172a')
    )

    cartao_sub_style = ParagraphStyle(
        'CartaoSub',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8,
        leading=10,
        alignment=TA_CENTER,
        textColor=colors.HexColor('#64748b')
    )

    story = []

    # Cabeçalho da Prova Institucional
    story.append(Paragraph("COORDENAÇÃO PROVAS — SISTEMA INSTITUCIONAL DE ENSINO", header_title_style))
    story.append(Spacer(1, 3))
    story.append(Paragraph(f"<b>Avaliação de {prova_base.disciplina.nome.upper()}</b>", header_title_style))
    story.append(Spacer(1, 6))

    # Tabela de Informações do Aluno / Turma / Versão
    data_str = prova_base.data_aplicacao.strftime('%d/%m/%Y') if prova_base.data_aplicacao else '___/___/______'
    info_data = [
        [f"<b>Título:</b> {prova_base.titulo}", f"<b>Versão:</b> {prova_gerada.codigo_versao}"],
        [f"<b>Turma:</b> {prova_base.turma}", f"<b>Data:</b> {data_str}"],
        [f"<b>Aluno(a):</b> __________________________________________________", f"<b>Nota:</b> ________"]
    ]

    t_info = Table(
        [[Paragraph(cell, body_style) for cell in row] for row in info_data],
        colWidths=[360, 160]
    )
    t_info.setStyle(TableStyle([
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#cbd5e1')),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e2e8f0')),
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f8fafc')),
        ('PADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(t_info)
    story.append(Spacer(1, 8))

    # Instruções da prova
    if prova_base.instrucoes:
        inst_p = Paragraph(f"<b>Instruções:</b> {prova_base.instrucoes}", header_sub_style)
        story.append(inst_p)
        story.append(Spacer(1, 6))

    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#94a3b8'), spaceBefore=2, spaceAfter=8))

    # Renderizar Questões Embaralhadas
    pg_questoes = sorted(prova_gerada.questoes_embaralhadas, key=lambda x: x.ordem_embaralhada)

    # Mapear itens embaralhados por questão
    itens_por_questao = {}
    for pgi in prova_gerada.itens_embaralhados:
        if pgi.questao_id not in itens_por_questao:
            itens_por_questao[pgi.questao_id] = []
        itens_por_questao[pgi.questao_id].append(pgi)

    for pgq in pg_questoes:
        q_num = pgq.ordem_embaralhada
        questao = pgq.questao
        
        # Enunciado
        story.append(Paragraph(f"<b>Questão {q_num:02d}.</b> {questao.enunciado}", enunciado_style))

        # Alternativas embaralhadas
        itens = sorted(itens_por_questao.get(questao.id, []), key=lambda x: x.ordem_embaralhada)
        for item_emb in itens:
            opcao_texto = f"( {item_emb.letra_atribuida} ) {item_emb.item.texto}"
            story.append(Paragraph(opcao_texto, opcao_style))

        story.append(Spacer(1, 6))

    # ==========================================
    # SEÇÃO DO CARTÃO-RESPOSTA / GABARITO DO ALUNO + QR CODE
    # ==========================================
    story.append(Spacer(1, 14))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor('#0f172a'), spaceBefore=6, spaceAfter=8))

    # Construir URL do QR Code vinculada ao ID / código da prova gerada
    qr_url = f"{base_url.rstrip('/')}/gabaritos/qr/{prova_gerada.id}"
    qr_flowable = gerar_qrcode_flowable(qr_url, width=82, height=82)

    # Tabela de preenchimento do gabarito (em 2 colunas de questões para economizar espaço e ficar elegante)
    total_q = len(pg_questoes)
    metade = (total_q + 1) // 2

    linhas_gabarito = []
    # Cabeçalho da grade
    if total_q <= 10:
        col_headers = [Paragraph("<b>Q.</b>", body_style), Paragraph("<b>RESPOSTA</b>", body_style)]
        grid_data = [col_headers]
        for pgq in pg_questoes:
            q_num = pgq.ordem_embaralhada
            grid_data.append([
                Paragraph(f"<b>{q_num:02d}</b>", body_style),
                Paragraph("( A )   ( B )   ( C )   ( D )   ( E )", body_style)
            ])
        t_grade = Table(grid_data, colWidths=[35, 180])
    else:
        grid_data = [[
            Paragraph("<b>Q.</b>", body_style), Paragraph("<b>RESPOSTA</b>", body_style),
            Paragraph("<b>Q.</b>", body_style), Paragraph("<b>RESPOSTA</b>", body_style)
        ]]
        for i in range(metade):
            q1_num = pg_questoes[i].ordem_embaralhada
            row = [
                Paragraph(f"<b>{q1_num:02d}</b>", body_style),
                Paragraph("( A ) ( B ) ( C ) ( D ) ( E )", body_style)
            ]
            if i + metade < total_q:
                q2_num = pg_questoes[i + metade].ordem_embaralhada
                row.extend([
                    Paragraph(f"<b>{q2_num:02d}</b>", body_style),
                    Paragraph("( A ) ( B ) ( C ) ( D ) ( E )", body_style)
                ])
            else:
                row.extend([Paragraph("", body_style), Paragraph("", body_style)])
            grid_data.append(row)
        t_grade = Table(grid_data, colWidths=[25, 145, 25, 145])

    t_grade.setStyle(TableStyle([
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#94a3b8')),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cbd5e1')),
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#f1f5f9')),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('PADDING', (0, 0), (-1, -1), 3),
    ]))

    # Bloco do QR Code e informações
    bloco_qr = [
        Paragraph("<b>CONFERÊNCIA DIGITAL</b>", cartao_title_style),
        Spacer(1, 2),
        Paragraph("Aponte a câmera para ver o gabarito oficial:", cartao_sub_style),
        Spacer(1, 4),
        qr_flowable,
        Spacer(1, 2),
        Paragraph(f"<b>ID: #{prova_gerada.id} | V{prova_gerada.numero_versao}</b>", cartao_sub_style),
        Paragraph(f"Código: {prova_gerada.codigo_versao}", cartao_sub_style)
    ]

    t_qr_wrapper = Table([[bloco_qr]], colWidths=[130])
    t_qr_wrapper.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#cbd5e1')),
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f8fafc')),
        ('PADDING', (0, 0), (-1, -1), 4),
    ]))

    # Combinar Cartão-Resposta e QR Code Lado a Lado
    cartao_completo_data = [
        [
            Paragraph("<b>CARTÃO-RESPOSTA DO ALUNO (FOLHA DE GABARITO)</b>", cartao_title_style),
            Paragraph("", cartao_title_style)
        ],
        [
            t_grade,
            t_qr_wrapper
        ]
    ]

    t_cartao_final = Table(
        cartao_completo_data,
        colWidths=[380, 140]
    )
    t_cartao_final.setStyle(TableStyle([
        ('SPAN', (0, 0), (1, 0)),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('PADDING', (0, 0), (-1, -1), 2),
    ]))

    # Envolver o bloco final em KeepTogether para evitar quebra indesejada
    story.append(KeepTogether([t_cartao_final]))

    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()

def gerar_pdf_gabarito(prova_gerada_id):
    """
    Gera um buffer de memória de PDF com o Gabarito Oficial de uma versão específica.
    """
    prova_gerada = ProvaGerada.query.get(prova_gerada_id)
    if not prova_gerada:
        raise ValueError("Prova gerada não encontrada.")

    prova_base = prova_gerada.prova_base
    buffer = io.BytesIO()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36
    )

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        'GabTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=14,
        alignment=TA_CENTER,
        textColor=colors.HexColor('#0f172a')
    )

    body_style = ParagraphStyle(
        'GabBody',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        textColor=colors.HexColor('#1e293b')
    )

    table_header_style = ParagraphStyle(
        'GabTH',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=10,
        alignment=TA_CENTER,
        textColor=colors.white
    )

    table_cell_style = ParagraphStyle(
        'GabTC',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        alignment=TA_CENTER,
        textColor=colors.HexColor('#0f172a')
    )

    story = []

    story.append(Paragraph("COORDENAÇÃO PROVAS — GABARITO OFICIAL", title_style))
    story.append(Spacer(1, 4))
    story.append(Paragraph(f"<b>{prova_base.titulo}</b> — Versão {prova_gerada.numero_versao} (Código: {prova_gerada.codigo_versao})", title_style))
    story.append(Spacer(1, 10))

    gabaritos_lista = sorted(prova_gerada.gabaritos, key=lambda x: x.numero_questao)

    table_data = [[
        Paragraph("Questão nº", table_header_style),
        Paragraph("Resposta Correta", table_header_style),
        Paragraph("Código Interno Questão", table_header_style)
    ]]

    for g in gabaritos_lista:
        table_data.append([
            Paragraph(f"<b>Questão {g.numero_questao:02d}</b>", table_cell_style),
            Paragraph(f"<b>[ {g.letra_correta} ]</b>", table_cell_style),
            Paragraph(f"#{g.questao_id}", table_cell_style)
        ])

    t_gab = Table(table_data, colWidths=[150, 180, 170])
    t_gab.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e293b')),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cbd5e1')),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8fafc')]),
        ('PADDING', (0, 0), (-1, -1), 6),
    ]))

    story.append(t_gab)
    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()

def gerar_zip_lote_provas(prova_base_id, base_url="http://127.0.0.1:5000"):
    """
    Gera um pacote .ZIP contendo todas as X provas geradas + seus gabaritos + tabela resumo.
    """
    prova_base = ProvaBase.query.get(prova_base_id)
    if not prova_base or not prova_base.versoes_geradas:
        raise ValueError("Nenhuma prova gerada encontrada para esta prova-base.")

    zip_buffer = io.BytesIO()

    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zf:
        resumo_gabaritos_txt = f"COORDENAÇÃO PROVAS - RESUMO DE GABARITOS EM LOTE\n"
        resumo_gabaritos_txt += f"Prova: {prova_base.titulo}\n"
        resumo_gabaritos_txt += f"Turma: {prova_base.turma} | Disciplina: {prova_base.disciplina.nome}\n"
        resumo_gabaritos_txt += "=" * 60 + "\n\n"

        for pg in sorted(prova_base.versoes_geradas, key=lambda x: x.numero_versao):
            pdf_prova_bytes = gerar_pdf_prova(pg.id, base_url=base_url)
            pdf_gabarito_bytes = gerar_pdf_gabarito(pg.id)

            nome_prova_file = f"provas/Prova_V{pg.numero_versao:02d}_{pg.codigo_versao}.pdf"
            nome_gabarito_file = f"gabaritos/Gabarito_V{pg.numero_versao:02d}_{pg.codigo_versao}.pdf"

            zf.writestr(nome_prova_file, pdf_prova_bytes)
            zf.writestr(nome_gabarito_file, pdf_gabarito_bytes)

            # Montar resumo texto
            resumo_gabaritos_txt += f"Versão {pg.numero_versao:02d} (Código: {pg.codigo_versao}):\n"
            gab_sorted = sorted(pg.gabaritos, key=lambda g: g.numero_questao)
            linha_g = "  " + " | ".join([f"Q{g.numero_questao:02d}:{g.letra_correta}" for g in gab_sorted])
            resumo_gabaritos_txt += linha_g + "\n\n"

        zf.writestr("Resumo_Gabaritos_Todas_Versoes.txt", resumo_gabaritos_txt.encode('utf-8'))

    zip_buffer.seek(0)
    return zip_buffer.getvalue()
