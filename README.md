# EduProvas — Sistema Institucional de Geração e Embaralhamento de Provas

![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Framework-Flask-000000?logo=flask&logoColor=white)
![SQLAlchemy](https://img.shields.io/badge/ORM-SQLAlchemy-red)
![Database](https://img.shields.io/badge/Database-MySQL%20%7C%20SQLite-00758F?logo=mysql&logoColor=white)
![Status](https://img.shields.io/badge/Status-Production--Ready-brightgreen)

Plataforma Web de gestão pedagógica e elaboração de avaliações institucionais desenvolvida em **Python + Flask**, **SQLAlchemy** e **JavaScript ES6**. O sistema permite que instituições de ensino gerenciem um acervo centralizado de questões e gerem automaticamente **múltiplas versões embaralhadas** com **gabaritos oficiais vinculados** e auditáveis.

---

## 📌 Principais Recursos

- **Gestão Centralizada do Banco de Questões (CRUD):**
  - Cadastro de questões categorizadas por disciplina, nível de dificuldade (*Fácil, Média, Difícil*), modalidade (*Múltipla Escolha* ou *Verdadeiro/Falso*) e *tags* de pesquisa.
  - Alternativas dinâmicas com validação de gabarito e suporte a múltiplas opções.
  - Filtros avançados por busca textual, disciplinas ativas e graus de complexidade.

- **Construtor Interativo de Provas-Base:**
  - Interface dinâmica para seleção de questões do banco com contagem em tempo real.
  - Configuração de metadados pedagógicos (Título da Avaliação, Disciplina, Turma, Data de Aplicação e Instruções para os Alunos).

- **Algoritmo de Embaralhamento Independente (Fisher-Yates):**
  - Geração de $X$ versões (ex: 4, 10 ou mais) a partir de um único modelo base.
  - **Dupla Permutação:** Reordenação estocástica independente da sequência das questões e das alternativas de cada questão.
  - **Mapeamento de Gabaritos Automático:** Rastreia as posições reordenadas e gera o gabarito oficial para cada versão.
  - **Auditabilidade via Seed:** Cada versão gerada possui um código único (ex: `V01-A9F32B`) e uma *seed* matemática registrada para auditoria pedagógica.

- **Exportação, Impressão e Download em Lote:**
  - **Impressão Nativa A4 (`@media print`):** Formatação limpa conforme normas de avaliações escolares.
  - **Exportação em PDF Nativo (ReportLab):** Geração individual de provas e gabaritos.
  - **Empacotamento ZIP:** Download em lote com todas as versões em PDF, gabaritos e matriz comparativa.
  - **Matriz Comparativa de Gabaritos:** Tabela unificada exibindo as respostas de todas as versões lado a lado.

- **Segurança e Controle de Acesso:**
  - Autenticação de professores e coordenadores via `Flask-Login` e criptografia de senhas com `Werkzeug.security`.

---

## 🏗️ Arquitetura e Estrutura de Arquivos

```text
sistema_provas/
├── app.py                      # Ponto de entrada da aplicação Flask
├── config.py                   # Configurações de ambiente e ORM
├── requirements.txt            # Dependências da aplicação
├── schema.sql                  # DDL de criação das tabelas (MySQL 8.0+)
├── seed.py                     # Script de população inicial de dados (Demo)
├── .env.example                # Template de variáveis de ambiente
├── .gitignore                  # Regras de exclusão de versionamento
├── README.md                   # Documentação do projeto
├── models/                     # Camada de Modelos SQLAlchemy (ORM)
│   ├── usuario.py              # Autenticação e Perfis (Professor / Coordenador)
│   ├── disciplina.py           # Gestão de Disciplinas / Matérias
│   ├── questao.py              # Banco de Questões
│   ├── item.py                 # Alternativas / Opções da Questão
│   ├── prova_base.py           # Modelo / Molde da Prova
│   ├── prova_gerada.py         # Instância da Versão Embaralhada
│   └── gabarito.py             # Mapeamento do Gabarito Oficial
├── services/                   # Camada de Regras de Negócio e Serviços
│   ├── shuffle_service.py      # Algoritmo Fisher-Yates e auditoria de Seed
│   └── export_service.py       # Geração de PDFs e pacote ZIP
├── routes/                     # Camada de Controladores / Blueprints Flask
│   ├── auth.py                 # Rotas de Login e Session Management
│   ├── dashboard.py            # Visão Geral e Estatísticas
│   ├── questoes.py             # Rotas de Gestão do Banco de Questões
│   ├── provas.py               # Rotas do Construtor de Provas e Versões
│   └── gabaritos.py            # Rotas da Matriz e Gabaritos Oficiais
├── static/                     # Ativos Estáticos da Interface
│   ├── css/                    # Estilos CSS (Design System Inter Font)
│   └── js/                     # Interatividade Frontend
├── templates/                  # Views / Layouts Jinja2
└── tests/                      # Suíte de Testes Automatizados (Unittest)
```

---

## 🚀 Guia de Instalação e Execução

### 1. Pré-requisitos
- **Python:** 3.10 ou superior
- **Gerenciador de Pacotes:** `pip`

### 2. Configuração do Ambiente

```bash
# Clonar o repositório
git clone https://github.com/Matheus-Jaco/sistema_provas.git
cd sistema_provas

# Criar ambiente virtual
python -m venv venv

# Ativar o ambiente virtual
# No Windows:
venv\Scripts\activate
# No Linux/macOS:
source venv/bin/activate

# Instalar dependências
pip install -r requirements.txt
```

### 3. Configurar Banco de Dados

- **Modo Desenvolvimento Rápido (SQLite Automático):**
  Caso nenhum arquivo `.env` com dados de banco seja especificado, o sistema inicializa automaticamente um banco de dados SQLite local (`sistema_provas.db`).

- **Modo Produção (MySQL):**
  Crie um arquivo `.env` baseado em `.env.example` e configure as credenciais do seu servidor MySQL:
  ```env
  DB_HOST=localhost
  DB_PORT=3306
  DB_USER=seu_usuario
  DB_PASSWORD=sua_senha
  DB_NAME=sistema_provas
  ```

### 4. Popular com Dados Iniciais (Opcional)
```bash
python seed.py
```
*Credenciais de teste geradas:*
- **Coordenador:** `admin@escola.edu.br` | Senha: `admin123`
- **Professor:** `carlos@escola.edu.br` | Senha: `prof123`

### 5. Executar a Aplicação
```bash
python app.py
```
Acesse no navegador: **`http://127.0.0.1:5000`**

---

## 🧪 Suíte de Testes Automatizados

Para executar os testes unitários do algoritmo de embaralhamento e verificação de gabarito:

```bash
python -m unittest discover -s tests
```

---

## 📄 Licença

Este projeto está sob licença MIT. Desenvolvido para fins institucionais e educacionais.
