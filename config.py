import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'wydgarden_clave_secreta_super_segura'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'mysql+pymysql://root:@localhost/wydgarden'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Configuración de Correo (Ejemplo para Gmail)
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME') or 'jordan.cely06@gmail.com'
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD') or 'ypju mmuq utzv ecfd'
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_USERNAME') or 'jordan.cely06@gmail.com'
    ADMIN_EMAIL = os.environ.get('ADMIN_EMAIL') or 'jordancely00@gmail.com'

    # Configuración de Expiración y Stock
    LIMITE_HORAS_EXPIRACION = int(os.environ.get('LIMITE_HORAS_EXPIRACION', 24))
    STOCK_MINIMO_ALERTA = int(os.environ.get('STOCK_MINIMO_ALERTA', 5))

