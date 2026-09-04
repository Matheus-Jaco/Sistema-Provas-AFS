# CoordenaçãoProvas — Sistema Institucional de Geração de Provas Embaralhadas

Aplicação Web profissional desenvolvida em **Python + Flask**, **SQLAlchemy / MySQL**, **HTML5/CSS3/JavaScript** puro e **Blueprints modulares**, projetada para escolas e colégios criarem provas com **embaralhamento independente de questões e alternativas** e **geração automática de gabaritos**.

---

## Funcionalidades Principais

1. **Gestão do Banco de Questões (CRUD Completo):**
   - Cadastro de questões com enunciado, disciplina, nível de dificuldade (Fácil, Média, Difícil), tipo (Múltipla Escolha / Verdadeiro ou Falso) e tags.
   - Alternativas dinâmicas com marcação visual da resposta correta.
   - Busca por texto, filtro por disciplina e filtro por dificuldade.

2. **Montagem de Prova-Base (Molde):**
   - Seleção interativa de questões do acervo com contador em tempo real e busca por disciplina.
   - Definição de metadados pedagógicos (Título, Disciplina, Turma, Data de Aplicação, Instruções para o Aluno).

3. **Geração de $X$ Versões Embaralhadas (`shuffle_service.py`):**
   - Campo para definir a quantidade $X$ de modelos diferentes a gerar.
   - **Algoritmo Fisher-Yates com Seed Registrada:** Embaralha a ordem das questões e das alternativas dentro de cada questão de forma 100% independente por versão.
   - **Gabarito Automático:** Mapeia dinamicamente as novas posições das alternativas (A, B, C, D...) de volta para a resposta correta original.
   - **Identificador Único:** Cada versão recebe um código exclusivo (Ex: `V01-A9F32B`) e *seed* de auditoria/reprodutibilidade.

4. **Exportação & Impressão:**
   - **Visualização em Tela e Impressão Direta (`@media print`):** Layout A4 limpo, sem menus administrativos, com cabeçalho escolar oficial.
   - **PDF Nativo (ReportLab):** Geração individual de PDFs da prova do aluno e do gabarito oficial.
   - **Download em Lote (ZIP):** Empacota todas as $X$ provas + $X$ gabaritos em arquivo `.ZIP` com 1 clique, incluindo um resumo consolidado em texto.
   - **Matriz Comparativa de Gabaritos:** Tabela unificada exibindo as respostas de todas as versões lado a lado.

5. **Autenticação & Segurança:**
   - Login/Logout com hash seguro de senha via `Werkzeug.security` e gerenciamento de sessão via `Flask-Login`.

---

## Estrutura do Projeto

```text
sistema_provas/
├── app.py                      # Ponto de entrada da aplicação Flask
├── config.py                   # Configurações da aplicação e conexões DB
├── requirements.txt            # Dependências Python
├── schema.sql                  # Script SQL DDL para MySQL 8.0+
├── seed.py                     # Script de povoamento inicial (demo data)
├── .env.example                # Exemplo de variáveis de ambiente
├── README.md                   # Instruções de instalação e uso
├── models/                     # Modelos SQLAlchemy relacional
│   ├── __init__.py
│   ├── usuario.py
│   ├── disciplina.py
│   ├── questao.py
│   ├── item.py
│   ├── prova_base.py
│   ├── prova_gerada.py
│   └── gabarito.py
├── services/                   # Módulos de regra de negócio
│   ├── __init__.py
│   ├── shuffle_service.py      # Algoritmo Fisher-Yates e mapeamento de gabarito
│   └── export_service.py       # Geração de PDFs e empacotamento ZIP
├── routes/                     # Blueprints Flask
│   ├── __init__.py
│   ├── auth.py                 # Autenticação (Login, Logout)
│   ├── dashboard.py            # Métricas e estatísticas gerais
│   ├── questoes.py             # CRUD de questões e alternativas
│   ├── provas.py               # Prova-base, embaralhamento e PDF/ZIP
│   └── gabaritos.py            # Visualização e matriz de gabaritos
├── static/                     # Arquivos estáticos
│   ├── css/
│   │   ├── style.css           # Design System institucional (Inter font)
│   │   └── print.css           # Estilo otimizado para impressão A4
│   └── js/
│       ├── main.js             # Gestão de formulários e alternativas dinâmicas
│       └── prova_builder.js    # Construtor interativo de prova
├── templates/                  # Templates Jinja2
│   ├── base.html               # Shell com sidebar e mensagens flash
│   ├── auth/                   # Tela de login
│   ├── dashboard/              # Painel principal
│   ├── questoes/               # Lista, cadastro e edição de questões
│   ├── provas/                 # Lista, construtor, versões e visualização A4
│   └── gabaritos/              # Gabarito individual e matriz comparativa
└── tests/                      # Suíte de testes automatizados
    ├── __init__.py
    └── test_shuffle.py         # Teste unitário do Fisher-Yates e gabarito
```

---

## Requisitos de Ambiente

- **Python:** 3.10 ou superior
- **Banco de Dados:** MySQL 8.0+ (ou SQLite automático out-of-the-box para testes rápidos)

---

## Instalação e Execução Passo a Passo

### 1. Clonar ou Acessar o Diretório
```bash
cd sistema_provas
```

### 2. Criar Ambiente Virtual (Recomendado)
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/macOS
python3 -m venv venv
source venv/bin/activate
```

### 3. Instalar Dependências
```bash
pip install -r requirements.txt
```

### 4. Configurar Banco de Dados MySQL

#### Opção A: Usar MySQL
1. Abra o MySQL Workbench ou terminal MySQL e execute o script `schema.sql`:
   ```bash
   mysql -u root -p < schema.sql
   ```
2. Crie um arquivo `.env` baseado no `.env.example`:
   ```ini
   FLASK_APP=app.py
   FLASK_ENV=development
   SECRET_KEY=sua_chave_secreta_institucional_2026

   DB_HOST=localhost
   DB_PORT=3306
   DB_USER=root
   DB_PASSWORD=sua_senha
   DB_NAME=sistema_provas
   ```

#### Opção B: Fallback SQLite (Desenvolvimento Imediato)
Caso as variáveis de conexão com o MySQL não sejam definidas no `.env`, a aplicação criará e utilizará automaticamente um banco **SQLite** local (`sistema_provas.db`) sem necessidade de configuração prévia.

---

### 5. Povoar o Banco com Dados de Exemplo (Opcional)
Execute o script `seed.py` para cadastrar usuários padrões, disciplinas e um acervo inicial de questões:
```bash
python seed.py
```

Credenciais criadas pelo seed:
- **E-mail:** `admin@escola.edu.br` | **Senha:** `admin123` (Coordenador)
- **E-mail:** `carlos@escola.edu.br` | **Senha:** `prof123` (Professor)

---

### 6. Executar a Aplicação Web
```bash
python app.py
```
Acesse no navegador: **`http://127.0.0.1:5000`**

## Execução de Testes Automatizados

Para validar o algoritmo Fisher-Yates, a reprodutibilidade com *seed* e a precisão do mapeamento de gabaritos:

```bash
python tests/test_shuffle.py
```

---

## Algoritmo de Embaralhamento (`shuffle_service.py`)

A função `gerar_versoes_embaralhadas` executa a seguinte sequência para cada versão $1..X$:
1. Define uma `seed` determinística (ou pseudo-aleatória) auditável.
2. Executa a permutação de Fisher-Yates no vetor de questões da prova-base.
3. Para cada questão reordenada, executa a permutação de Fisher-Yates no vetor de alternativas.
4. Atribui a nova sequência de letras (`A`, `B`, `C`, `D`, `E`...) às posições embaralhadas.
5. Localiza a alternativa que possuía o atributo `correta == True` e registra o mapeamento na tabela `gabaritos` com o novo número da questão e a nova letra atribuída.
