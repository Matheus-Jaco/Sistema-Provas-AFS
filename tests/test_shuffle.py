import os
import sys
import unittest
import random

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app
from config import Config
from models import db
from models.usuario import Usuario
from models.disciplina import Disciplina
from models.questao import Questao
from models.item import Item
from models.prova_base import ProvaBase, ProvaBaseQuestao
from models.prova_gerada import ProvaGerada
from services.shuffle_service import gerar_versoes_embaralhadas

class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'

class ShuffleServiceTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app(TestConfig)
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

        # Criar dados de teste
        self.user = Usuario(nome="Test User", email="test@school.edu.br", perfil="professor")
        self.user.set_senha("password")
        db.session.add(self.user)

        self.disc = Disciplina(nome="Matemática Teste", codigo="MAT-TEST")
        db.session.add(self.disc)
        db.session.commit()

        # Criar 5 questões com 4 alternativas cada
        self.questoes = []
        for q_idx in range(1, 6):
            q = Questao(
                enunciado=f"Enunciado da Questão {q_idx}",
                disciplina_id=self.disc.id,
                dificuldade="media",
                criado_por=self.user.id
            )
            db.session.add(q)
            db.session.flush()

            for i_idx in range(1, 5):
                item = Item(
                    questao_id=q.id,
                    texto=f"Alternativa {i_idx} da Q{q_idx}",
                    correta=(i_idx == 2), # Alternativa 2 é a correta
                    ordem_original=i_idx
                )
                db.session.add(item)
            self.questoes.append(q)

        db.session.commit()

        # Criar Prova-Base
        self.pb = ProvaBase(
            titulo="Prova Teste de Embaralhamento",
            disciplina_id=self.disc.id,
            turma="3A",
            criado_por=self.user.id
        )
        db.session.add(self.pb)
        db.session.flush()

        for idx, q in enumerate(self.questoes, start=1):
            pbq = ProvaBaseQuestao(prova_base_id=self.pb.id, questao_id=q.id, ordem=idx)
            db.session.add(pbq)

        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_geracao_versoes_embaralhadas(self):
        # Gerar X = 3 versões
        versoes = gerar_versoes_embaralhadas(self.pb.id, 3, seed_prefix="TEST")

        self.assertEqual(len(versoes), 3)

        # 1. Validar que cada versão tem um código de versão único
        codigos = [v.codigo_versao for v in versoes]
        self.assertEqual(len(set(codigos)), 3)

        # 2. Validar que cada versão tem 5 questões e 20 itens mapeados
        for v in versoes:
            self.assertEqual(len(v.questoes_embaralhadas), 5)
            self.assertEqual(len(v.itens_embaralhados), 20)
            self.assertEqual(len(v.gabaritos), 5)

        # 3. Validar precisão do Gabarito: a letra no Gabarito DEVE corresponder à letra atribuída ao item correto
        for v in versoes:
            for gab in v.gabaritos:
                # Localizar item_correto_id na tabela de itens embaralhados dessa prova
                item_emb = next(
                    item for item in v.itens_embaralhados
                    if item.questao_id == gab.questao_id and item.item_id == gab.item_correto_id
                )
                self.assertEqual(gab.letra_correta, item_emb.letra_atribuida)
                self.assertTrue(item_emb.item.correta)

    def test_reprodutibilidade_com_seed(self):
        # Testar se seeds idênticas produzem exatamente a mesma ordem
        v1 = gerar_versoes_embaralhadas(self.pb.id, 1, seed_prefix="FIXED_SEED")[0]
        
        db.session.delete(v1)
        db.session.commit()

        v2 = gerar_versoes_embaralhadas(self.pb.id, 1, seed_prefix="FIXED_SEED")[0]

        q_ordem1 = [q.questao_id for q in v1.questoes_embaralhadas]
        q_ordem2 = [q.questao_id for q in v2.questoes_embaralhadas]

        self.assertEqual(q_ordem1, q_ordem2)

if __name__ == '__main__':
    unittest.main()
