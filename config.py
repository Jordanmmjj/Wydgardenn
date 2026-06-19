import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'wydgarden_clave_secreta_super_segura')
    
    # Railway provee DATABASE_URL con prefijo mysql://, pero SQLAlchemy requiere mysql+pymysql://
    db_url = os.environ.get('DATABASE_URL') or 'mysql+pymysql://root:@localhost/wydgarden'
    if db_url and db_url.startswith('mysql://'):
        db_url = db_url.replace('mysql://', 'mysql+pymysql://', 1)
        
    SQLALCHEMY_DATABASE_URI = db_url
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    MAIL_SERVER = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
    MAIL_PORT = int(os.environ.get('MAIL_PORT', 587))
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'True').lower() in ['true', '1', 't']
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_USERNAME')
    ADMIN_EMAIL = os.environ.get('ADMIN_EMAIL', 'jordancely00@gmail.com')

    LIMITE_HORAS_EXPIRACION = int(os.environ.get('LIMITE_HORAS_EXPIRACION', 24))
    STOCK_MINIMO_ALERTA = int(os.environ.get('STOCK_MINIMO_ALERTA', 5))