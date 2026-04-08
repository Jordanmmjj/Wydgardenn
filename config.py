import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'wydgarden_clave_secreta_super_segura'
    # Base de datos MySQL
    # Ajusta con tu usuario (por defecto root) y contraseña de MySQL
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'mysql+pymysql://root:@localhost/wydgarden'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
