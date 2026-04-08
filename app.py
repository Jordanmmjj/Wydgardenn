from flask import Flask, render_template
from config import Config
from models import db, Producto, Usuario
from flask_login import LoginManager, current_user

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Inicializar Base de Datos
    db.init_app(app)
    
    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)
    
    @login_manager.user_loader
    def load_user(user_id):
        return Usuario.query.get(int(user_id))
    
    with app.app_context():
        # Crea las tablas si no existen según los modelos de models.py
        try:
            db.create_all()
            print("Tablas sincronizadas con éxito (o ya existentes).")
        except Exception as e:
            print("Advertencia: No se pudo conectar a la base de datos MySQL al iniciar.", e)

    # --- RUTAS ---
    @app.route('/')
    def root():
        return render_template('home.html')
        
    @app.route('/home')
    def home():
        return render_template('home.html')

    from routes.shop_routes import shop_bp
    app.register_blueprint(shop_bp)

    from routes.auth_routes import auth_bp
    app.register_blueprint(auth_bp)

    from routes.admin_routes import admin_bp
    app.register_blueprint(admin_bp)

    from routes.pqrs_routes import pqrs_bp
    app.register_blueprint(pqrs_bp)

    from flask import send_from_directory
    @app.route('/storage/<path:filename>')
    def storage(filename):
        return send_from_directory('storage', filename)
        
    @app.route('/perfil')
    def perfil():
        return render_template('perfil.html')

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, port=5000)
