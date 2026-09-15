import unittest
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
from services.export_service import gerar_pdf_prova
from services.qr_service import gerar_qrcode_imagem_bytes, gerar_qrcode_base64

class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False
    SECRET_KEY = 'test-secret-key'

class CoordenacaoProfessoresQRTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app(TestConfig)
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

        # Criar Coordenação
        self.coord = Usuario(
            nome="Coordenação Provas",
            email="coordenacao@escola.edu.br",
            perfil="admin"
        )
        self.coord.set_senha("coord123")
        db.session.add(self.coord)
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def login(self, email, senha):
        return self.client.post('/auth/login', data={
            'email': email,
            'senha': senha
        }, follow_redirects=True)

    def logout(self):
        return self.client.get('/auth/logout', follow_redirects=True)

    def test_coordenacao_cria_professor_e_login_funciona(self):
        """CoordenaçãoProvas cadastra professor e o professor consegue logar com seu perfil"""
        disciplina = Disciplina(nome='Português', codigo='POR-01')
        db.session.add(disciplina)
        db.session.commit()

        self.login("coordenacao@escola.edu.br", "coord123")

        res_criar = self.client.post('/professores/criar', data={
            'nome': 'Prof. Fernanda Lima',
            'email': 'fernanda@escola.edu.br',
            'senha': 'senhafernanda',
            'perfil': 'professor',
            'disciplinas': [str(disciplina.id)]
        }, follow_redirects=True)
        self.assertEqual(res_criar.status_code, 200)
        self.assertIn('Prof. Fernanda Lima'.encode('utf-8'), res_criar.data)

        self.logout()

        res_prof_login = self.login("fernanda@escola.edu.br", "senhafernanda")
        self.assertEqual(res_prof_login.status_code, 200)
        self.assertIn('Prof. Fernanda Lima'.encode('utf-8'), res_prof_login.data)

    def test_isolamento_de_provas_entre_professores_e_visao_global_coordenacao(self):
        """Professores só acessam suas próprias provas; a Coordenação vê as provas de todos"""
        disc = Disciplina.query.filter_by(nome="História").first()
        if not disc:
            disc = Disciplina(nome="História", codigo="HIS-1")
            db.session.add(disc)
            db.session.flush()

        # Professor 1
        prof1 = Usuario(nome="Prof. João Silva", email="joao@escola.edu.br", perfil="professor")
        prof1.set_senha("joao123")
        prof1.disciplinas = [disc]
        # Professor 2
        prof2 = Usuario(nome="Profa. Maria Santos", email="maria@escola.edu.br", perfil="professor")
        prof2.set_senha("maria123")
        prof2.disciplinas = [disc]
        db.session.add_all([prof1, prof2])
        db.session.commit()

        # Prova do Prof 1
        pb1 = ProvaBase(titulo="Prova de História João", disciplina_id=disc.id, turma="1A", criado_por=prof1.id)
        # Prova do Prof 2
        pb2 = ProvaBase(titulo="Prova de História Maria", disciplina_id=disc.id, turma="2B", criado_por=prof2.id)
        db.session.add_all([pb1, pb2])
        db.session.commit()

        # 1. Testar visão do Professor 1 (João)
        self.login("joao@escola.edu.br", "joao123")
        res_joao = self.client.get('/provas/')
        self.assertIn('Prova de História João'.encode('utf-8'), res_joao.data)
        self.assertNotIn('Prova de História Maria'.encode('utf-8'), res_joao.data)

        # João tenta acessar versões da prova da Maria -> Bloqueado
        res_bloqueio = self.client.get(f'/provas/{pb2.id}/versoes', follow_redirects=True)
        self.assertIn('Você não tem permissão'.encode('utf-8'), res_bloqueio.data)

        self.logout()

        # 2. Testar visão do Professor 2 (Maria)
        self.login("maria@escola.edu.br", "maria123")
        res_maria = self.client.get('/provas/')
        self.assertIn('Prova de História Maria'.encode('utf-8'), res_maria.data)
        self.assertNotIn('Prova de História João'.encode('utf-8'), res_maria.data)
        self.logout()

        # 3. Testar visão da CoordenaçãoProvas (deve ver AMBAS as provas)
        self.login("coordenacao@escola.edu.br", "coord123")
        res_coord = self.client.get('/provas/')
        self.assertIn('Prova de História João'.encode('utf-8'), res_coord.data)
        self.assertIn('Prova de História Maria'.encode('utf-8'), res_coord.data)
        self.assertIn('Prof. João Silva'.encode('utf-8'), res_coord.data)
        self.assertIn('Profa. Maria Santos'.encode('utf-8'), res_coord.data)

    def test_professor_nao_pode_acessar_gestao_professores(self):
        """Professores não podem acessar o módulo de criação e gestão de professores"""
        prof = Usuario(nome="Prof. Lucas", email="lucas@escola.edu.br", perfil="professor")
        prof.set_senha("lucas123")
        db.session.add(prof)
        db.session.commit()

        self.login("lucas@escola.edu.br", "lucas123")
        res = self.client.get('/professores/', follow_redirects=True)
        self.assertIn('Acesso restrito'.encode('utf-8'), res.data)

    def test_professor_nao_ve_ou_usa_cadastro_de_disciplinas(self):
        """Professores não podem visualizar nem criar disciplinas via UI ou rotas de disciplina."""
        disc = Disciplina(nome='Filosofia', codigo='FIL-01')
        db.session.add(disc)
        db.session.commit()

        prof = Usuario(nome='Prof. Helena', email='helena@escola.edu.br', perfil='professor')
        prof.set_senha('helena123')
        prof.disciplinas = [disc]
        db.session.add(prof)
        db.session.commit()

        self.login('helena@escola.edu.br', 'helena123')

        res_provas = self.client.get('/provas/', follow_redirects=True)
        self.assertNotIn('Cadastrar Disciplina'.encode('utf-8'), res_provas.data)

        res_questoes = self.client.get('/questoes/criar', follow_redirects=True)
        self.assertNotIn('Nova Disciplina'.encode('utf-8'), res_questoes.data)

        res_quick = self.client.post('/questoes/disciplinas/criar', json={
            'nome': 'Sociologia',
            'codigo': 'SOC-01',
            'descricao': 'Nova disciplina'
        }, follow_redirects=True)
        self.assertIn('Acesso restrito', res_quick.get_data(as_text=True))

        res_provas_post = self.client.post('/provas/disciplinas/criar', data={
            'nome': 'Geografia',
            'codigo': 'GEO-01',
            'descricao': 'Nova disciplina'
        }, follow_redirects=True)
        self.assertIn('Acesso restrito', res_provas_post.get_data(as_text=True))

    def test_professor_precisa_ter_disciplinas_atribuidas_e_nao_cria_fora_delas(self):
        """Professor só pode operar em disciplinas atribuídas pela coordenação."""
        mat = Disciplina(nome="Química Aplicada", codigo="QUI-01")
        bio = Disciplina(nome="Biologia Molecular", codigo="BIO-01")
        db.session.add_all([mat, bio])
        db.session.commit()

        self.login("coordenacao@escola.edu.br", "coord123")
        res = self.client.post('/professores/criar', data={
            'nome': 'Prof. Ana Souza',
            'email': 'ana@escola.edu.br',
            'senha': 'ana123',
            'perfil': 'professor',
            'disciplinas': [str(mat.id)]
        }, follow_redirects=True)
        self.assertEqual(res.status_code, 200)
        self.assertIn('Prof. Ana Souza'.encode('utf-8'), res.data)

        self.logout()
        self.login("ana@escola.edu.br", "ana123")

        res_form = self.client.get('/questoes/criar')
        self.assertIn('Química Aplicada'.encode('utf-8'), res_form.data)
        self.assertNotIn('Biologia Molecular'.encode('utf-8'), res_form.data)

        res_forbidden = self.client.post('/questoes/criar', data={
            'enunciado': 'Questão não permitida',
            'disciplina_id': str(bio.id),
            'tipo': 'multipla_escolha',
            'dificuldade': 'media',
            'tags': 'proibida',
            'item_texto[]': ['A', 'B'],
            'item_correto': '0'
        }, follow_redirects=True)
        self.assertIn('disciplinas atribuídas'.encode('utf-8'), res_forbidden.data)

    def test_qr_code_e_cartao_resposta_na_prova(self):
        """Testa geração do QR Code e consulta pública do gabarito vinculado"""
        disc = Disciplina(nome="Biologia", codigo="BIO-1")
        db.session.add(disc)
        db.session.flush()

        q = Questao(enunciado="O que é fotossíntese?", disciplina_id=disc.id, criado_por=self.coord.id)
        db.session.add(q)
        db.session.flush()

        i1 = Item(questao_id=q.id, texto="Processo de síntese energética celular", correta=True, ordem_original=1)
        i2 = Item(questao_id=q.id, texto="Divisão celular mitótica", correta=False, ordem_original=2)
        db.session.add_all([i1, i2])

        pb = ProvaBase(titulo="Prova de Biologia 1º Bim", disciplina_id=disc.id, turma="1A", criado_por=self.coord.id)
        db.session.add(pb)
        db.session.flush()

        pb_q = ProvaBaseQuestao(prova_base_id=pb.id, questao_id=q.id, ordem=1)
        db.session.add(pb_q)
        db.session.commit()

        # Gerar versões
        versoes = gerar_versoes_embaralhadas(pb.id, 2)
        self.assertEqual(len(versoes), 2)
        pg = versoes[0]

        # Testar QR Code Service
        qr_bytes = gerar_qrcode_imagem_bytes(f"http://127.0.0.1:5000/gabaritos/qr/{pg.id}")
        self.assertTrue(len(qr_bytes) > 0)

        qr_b64 = gerar_qrcode_base64(f"http://127.0.0.1:5000/gabaritos/qr/{pg.id}")
        self.assertTrue(qr_b64.startswith("data:image/png;base64,"))

        # Testar geração de PDF com Cartão-Resposta e QR-Code
        pdf_bytes = gerar_pdf_prova(pg.id)
        self.assertTrue(len(pdf_bytes) > 0)
        self.assertTrue(pdf_bytes.startswith(b'%PDF'))

        # Testar Rota pública do QR Code
        res_qr = self.client.get(f'/gabaritos/qr/{pg.id}')
        self.assertEqual(res_qr.status_code, 200)
        self.assertIn(pg.codigo_versao.encode('utf-8'), res_qr.data)
        self.assertIn('Gabarito Oficial'.encode('utf-8'), res_qr.data)

if __name__ == '__main__':
    unittest.main()
