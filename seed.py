"""
Script de povoamento inicial (seed) do Banco de Questões da Escola.
Cria disciplinas, questões completas com alternativas e respostas corretas.
"""

from app import app
from models import db
from models.usuario import Usuario
from models.disciplina import Disciplina
from models.questao import Questao
from models.item import Item

def popular_banco():
    with app.app_context():
        admin = Usuario.query.filter_by(email="admin@escola.edu.br").first()
        if not admin:
            admin = Usuario(nome="Coordenador Pedagógico", email="admin@escola.edu.br", perfil="admin")
            admin.set_senha("admin123")
            db.session.add(admin)
            db.session.commit()

        # Obter ou criar disciplinas
        mat = Disciplina.query.filter_by(nome="Matemática").first()
        if not mat:
            mat = Disciplina(nome="Matemática", codigo="MAT-100", descricao="Álgebra e Geometria")
            db.session.add(mat)

        fis = Disciplina.query.filter_by(nome="Física").first()
        if not fis:
            fis = Disciplina(nome="Física", codigo="FIS-100", descricao="Mecânica e Eletromagnetismo")
            db.session.add(fis)

        his = Disciplina.query.filter_by(nome="História").first()
        if not his:
            his = Disciplina(nome="História", codigo="HIS-100", descricao="História do Brasil e Geral")
            db.session.add(his)

        db.session.commit()

        # Lista de questões de exemplo
        questoes_dados = [
            {
                "enunciado": "Qual é a solução da equação do 2º grau x² - 5x + 6 = 0?",
                "disciplina_id": mat.id,
                "dificuldade": "facil",
                "tags": "equações, álgebra",
                "itens": [
                    ("x = 1 e x = 6", False),
                    ("x = 2 e x = 3", True),
                    ("x = -2 e x = -3", False),
                    ("x = 0 e x = 5", False),
                ]
            },
            {
                "enunciado": "Qual é o valor da área de um triângulo retângulo de base 8 cm e altura 6 cm?",
                "disciplina_id": mat.id,
                "dificuldade": "facil",
                "tags": "geometria, área",
                "itens": [
                    ("48 cm²", False),
                    ("24 cm²", True),
                    ("14 cm²", False),
                    ("32 cm²", False),
                ]
            },
            {
                "enunciado": "Se log₁₀(x) = 3, qual é o valor de x?",
                "disciplina_id": mat.id,
                "dificuldade": "media",
                "tags": "logaritmos, álgebra",
                "itens": [
                    ("x = 30", False),
                    ("x = 100", False),
                    ("x = 1000", True),
                    ("x = 300", False),
                ]
            },
            {
                "enunciado": "De acordo com a Primeira Lei de Newton (Lei da Inércia), um corpo em repouso tende a:",
                "disciplina_id": fis.id,
                "dificuldade": "facil",
                "tags": "newton, mecânica",
                "itens": [
                    ("Acelerar uniformemente", False),
                    ("Manter-se em repouso se a força resultante for nula", True),
                    ("Mudar de direção espontaneamente", False),
                    ("Girar em torno do seu próprio eixo", False),
                ]
            },
            {
                "enunciado": "Qual é a velocidade média de um automóvel que percorre 300 km em 4 horas?",
                "disciplina_id": fis.id,
                "dificuldade": "facil",
                "tags": "cinemática, velocidade",
                "itens": [
                    ("75 km/h", True),
                    ("60 km/h", False),
                    ("80 km/h", False),
                    ("100 km/h", False),
                ]
            },
            {
                "enunciado": "Em que ano ocorreu a Proclamação da República no Brasil?",
                "disciplina_id": his.id,
                "dificuldade": "facil",
                "tags": "república, brasil",
                "itens": [
                    ("1822", False),
                    ("1888", False),
                    ("1889", True),
                    ("1930", False),
                ]
            },
            {
                "enunciado": "Quem foi o primeiro imperador do Brasil após a Independência em 1822?",
                "disciplina_id": his.id,
                "dificuldade": "facil",
                "tags": "império, brasil",
                "itens": [
                    ("Dom Pedro II", False),
                    ("Dom Pedro I", True),
                    ("Marechal Deodoro da Fonseca", False),
                    ("Getúlio Vargas", False),
                ]
            }
        ]

        count_novas = 0
        for qd in questoes_dados:
            existente = Questao.query.filter_by(enunciado=qd["enunciado"]).first()
            if not existente:
                q = Questao(
                    enunciado=qd["enunciado"],
                    disciplina_id=qd["disciplina_id"],
                    dificuldade=qd["dificuldade"],
                    tags=qd["tags"],
                    criado_por=admin.id
                )
                db.session.add(q)
                db.session.flush()

                for idx, (texto, correta) in enumerate(qd["itens"], start=1):
                    item = Item(
                        questao_id=q.id,
                        texto=texto,
                        correta=correta,
                        ordem_original=idx
                    )
                    db.session.add(item)
                count_novas += 1

        db.session.commit()
        print(f"Povoamento concluido! {count_novas} questoes adicionadas ao banco.")

if __name__ == "__main__":
    popular_banco()
