from flask import Flask, render_template, request, redirect, url_for, flash
from config import Config
from models import db, Producto, Usuario
from flask_login import LoginManager, current_user
from flask_mail import Mail

mail = Mail()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Inicializar Base de Datos
    db.init_app(app)
    
    # Inicializar Mail
    mail.init_app(app)
    
    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)
    
    @login_manager.user_loader
    def load_user(user_id):
        return Usuario.query.get(int(user_id))
    
    with app.app_context():
        try:
            db.create_all()
            print("Tablas sincronizadas con éxito (o ya existentes).")
        except Exception as e:
            print("Advertencia: No se pudo conectar a la base de datos MySQL al iniciar.", e)

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

    from routes.pedidos_routes import pedidos_bp
    app.register_blueprint(pedidos_bp)

    from flask import send_from_directory
    @app.route('/storage/<path:filename>')
    def storage(filename):
        return send_from_directory('storage', filename)
        
    @app.route('/perfil')
    def perfil():
        return render_template('perfil.html')

    @app.route('/perfil/actualizar', methods=['POST'])
    def actualizar_perfil():
        if not current_user.is_authenticated:
            return redirect(url_for('auth.login'))
        
        nombres = request.form.get('nombres')
        apellidos = request.form.get('apellidos')
        telefono = request.form.get('telefono')
        password = request.form.get('password')

        # Validación de solo letras
        import re
        if not re.match(r"^[a-zA-ZáéíóúÁÉÍÓÚñÑ ]+$", nombres) or not re.match(r"^[a-zA-ZáéíóúÁÉÍÓÚñÑ ]+$", apellidos):
            from flask import flash
            flash('Los nombres y apellidos solo pueden contener letras.', 'error')
            return redirect(url_for('perfil'))

        current_user.nombres = nombres
        current_user.apellidos = apellidos
        current_user.telefono = telefono
        
        if password:
            from werkzeug.security import generate_password_hash
            current_user.password = generate_password_hash(password)
        
        from models import db
        db.session.commit()
        from flask import flash
        flash('Perfil actualizado con éxito.', 'success')
        return redirect(url_for('perfil'))

    return app

if __name__ == '__main__':
    app = create_app()
    # Usamos host='0.0.0.0' para que sea accesible desde celulares en la misma red Wifi
    app.run(debug=True, host='0.0.0.0', port=5000)
