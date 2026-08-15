import os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'escola-sistema-provas-secret-key-2026'
    
    db_user = os.environ.get('DB_USER')
    db_password = os.environ.get('DB_PASSWORD')
    db_host = os.environ.get('DB_HOST', 'localhost')
    db_port = os.environ.get('DB_PORT', '3306')
    db_name = os.environ.get('DB_NAME', 'sistema_provas')
    
    explicit_db_url = os.environ.get('DATABASE_URL')
    
    if explicit_db_url:
        SQLALCHEMY_DATABASE_URI = explicit_db_url
    elif db_user:
        SQLALCHEMY_DATABASE_URI = f"mysql+pymysql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}?charset=utf8mb4"
    else:
        # Fallback local SQLite para execução imediata de demonstração/testes
        SQLALCHEMY_DATABASE_URI = os.environ.get('SQLITE_URL') or f"sqlite:///{os.path.join(basedir, 'sistema_provas.db')}"
        
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JSON_AS_ASCII = False
