import random
import uuid
import string
from models import db
from models.prova_base import ProvaBase
from models.prova_gerada import ProvaGerada, ProvaGeradaQuestao, ProvaGeradaItem
from models.gabarito import Gabarito

LETRAS_OPCOES = list(string.ascii_uppercase) # ['A', 'B', 'C', 'D', 'E', 'F', ...]

def fisher_yates_shuffle(lista, rng):
    """
    Algoritmo Fisher-Yates clássico para embaralhamento de elementos
    utilizando a instância de gerador pseudo-aleatório fornecida (com seed).
    """
    arr = list(lista)
    n = len(arr)
    for i in range(n - 1, 0, -1):
        j = rng.randint(0, i)
        arr[i], arr[j] = arr[j], arr[i]
    return arr

def gerar_versoes_embaralhadas(prova_base_id, quantidade_x, seed_prefix=None):
    """
    Gera X versões embaralhadas de uma prova base.
    Em cada versão:
      1. Embaralha a ordem das questões de forma independente.
      2. Embaralha a ordem das alternativas/itens dentro de cada questão de forma independente.
      3. Atribui novas letras (A, B, C, D...) às posições embaralhadas.
      4. Identifica a resposta correta original e grava o gabarito correspondente.
    """
    prova_base = ProvaBase.query.get(prova_base_id)
    if not prova_base:
        raise ValueError(f"Prova-base com ID {prova_base_id} não encontrada.")

    # Obter questões associadas à prova base na ordem original
    pb_questoes = prova_base.questoes_associadas
    if not pb_questoes:
        raise ValueError("A prova-base não possui questões vinculadas.")

    provas_geradas_criadas = []

    for idx in range(1, quantidade_x + 1):
        # 1. Gerar Seed auditável e Código Único da Versão
        if seed_prefix:
            sub_seed = f"{seed_prefix}-PB{prova_base_id}-V{idx}"
        else:
            sub_seed = f"PRV-PB{prova_base_id}-V{idx}-{uuid.uuid4().hex[:6]}"
            
        rng = random.Random(sub_seed)

        codigo_versao = f"V{idx:02d}-{uuid.uuid4().hex[:6].upper()}"

        prova_gerada = ProvaGerada(
            prova_base_id=prova_base_id,
            codigo_versao=codigo_versao,
            numero_versao=idx,
            seed=sub_seed
        )
        db.session.add(prova_gerada)
        db.session.flush() # Gerar ID da prova_gerada

        # 2. Embaralhar questões da prova via Fisher-Yates
        questoes_originais = [pbq.questao for pbq in pb_questoes]
        questoes_embaralhadas = fisher_yates_shuffle(questoes_originais, rng)

        for num_q, questao in enumerate(questoes_embaralhadas, start=1):
            # Grava a nova posição da questão na prova gerada
            pg_q = ProvaGeradaQuestao(
                prova_gerada_id=prova_gerada.id,
                questao_id=questao.id,
                ordem_embaralhada=num_q
            )
            db.session.add(pg_q)

            # 3. Embaralhar itens/alternativas da questão via Fisher-Yates
            itens_originais = list(questao.itens)
            itens_embaralhados = fisher_yates_shuffle(itens_originais, rng)

            item_correto_encontrado = None
            letra_correta_encontrada = None

            for num_item, item in enumerate(itens_embaralhados):
                letra = LETRAS_OPCOES[num_item % len(LETRAS_OPCOES)]
                
                pg_i = ProvaGeradaItem(
                    prova_gerada_id=prova_gerada.id,
                    questao_id=questao.id,
                    item_id=item.id,
                    ordem_embaralhada=num_item + 1,
                    letra_atribuida=letra
                )
                db.session.add(pg_i)

                if item.correta:
                    item_correto_encontrado = item
                    letra_correta_encontrada = letra

            # 4. Gravar a entrada no Gabarito Oficial desta versão
            if item_correto_encontrado and letra_correta_encontrada:
                gab = Gabarito(
                    prova_gerada_id=prova_gerada.id,
                    numero_questao=num_q,
                    questao_id=questao.id,
                    item_correto_id=item_correto_encontrado.id,
                    letra_correta=letra_correta_encontrada
                )
                db.session.add(gab)

        provas_geradas_criadas.append(prova_gerada)

    db.session.commit()
    return provas_geradas_criadas
