import re
import smtplib
import bcrypt
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadTimeSignature
from models import db, Usuario, Rol

auth_bp = Blueprint('auth', __name__)

def validar_password_fuerte(password):
    if len(password) < 8:
        return "La contraseña debe tener al menos 8 caracteres."
    # Se ha relajado por petición: Solo pedimos los 8 caracteres.
    return None

def enviar_correo_generico(destinatario, asunto, cuerpo):
    remitente = "jordan.cely06@gmail.com"
    password_app = "bbsptvhuqbqvcnwn"
    
    msg = MIMEMultipart()
    msg['From'] = remitente
    msg['To'] = destinatario
    msg['Subject'] = asunto
    msg.attach(MIMEText(cuerpo, 'plain'))
    
    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(remitente, password_app)
        server.sendmail(remitente, destinatario, msg.as_string())
        server.quit()
        return True
    except Exception as e:
        print(f"Error enviando correo a {destinatario}:", e)
        return False

def enviar_correo_bienvenida(destinatario_usuario, nombre_usuario):
    asunto = "¡Bienvenido a WYDGARDEN!"
    cuerpo = f"Hola {nombre_usuario},\n\nHas creado tu cuenta exitosamente. ¡Bienvenido a nuestra tienda!"
    enviar_correo_generico(destinatario_usuario, asunto, cuerpo)
    # Notificar admin
    admin_email = "jordan.cely06@gmail.com"
    enviar_correo_generico(admin_email, "🌱 NUEVO REGISTRO", f"Nuevo usuario: {nombre_usuario} ({destinatario_usuario})")

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    if request.method == 'POST':
        email = request.form.get('username')
        password = request.form.get('password')
        user = Usuario.query.filter_by(email=email).first()
        is_valid = False
        if user:
            if user.password == password: is_valid = True
            elif check_password_hash(user.password, password): is_valid = True
            elif user.password.startswith('$2a$') or user.password.startswith('$2b$'):
                try:
                    hp = user.password.replace('$2a$', '$2b$').encode('utf-8')
                    if bcrypt.checkpw(password.encode('utf-8'), hp): is_valid = True
                except: pass
        if user and is_valid:
            login_user(user)
            return redirect(url_for('home'))
        flash('Correo o contraseña incorrectos.', 'error')
    return render_template('login.html')

@auth_bp.route('/registro', methods=['GET', 'POST'])
def registro():
    if current_user.is_authenticated: return redirect(url_for('home'))
    if request.method == 'POST':
        nombres = request.form.get('nombre')
        email = request.form.get('correo')
        password = request.form.get('contraseña')
        if Usuario.query.filter_by(email=email).first():
            flash('El correo ya existe.', 'error')
            return redirect(url_for('auth.registro'))
        err = validar_password_fuerte(password)
        if err:
            flash(err, 'error')
            return redirect(url_for('auth.registro'))
        rol_u = Rol.query.filter_by(nombre='USUARIO').first() or Rol(nombre='USUARIO')
        u = Usuario(nombres=nombres, apellidos='', email=email, password=generate_password_hash(password), rol=rol_u)
        db.session.add(u)
        db.session.commit()
        enviar_correo_bienvenida(email, nombres)
        flash('Registro exitoso. Inicia sesión.', 'success')
        return redirect(url_for('auth.login'))
    return render_template('registro.html')

@auth_bp.route('/recuperar-password', methods=['GET', 'POST'])
def recuperar_password():
    if request.method == 'POST':
        email = request.form.get('email')
        user = Usuario.query.filter_by(email=email).first()
        if user:
            s = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
            token = s.dumps(email, salt='password-reset-salt')
            link = url_for('auth.restablecer_password', token=token, _external=True)
            cuerpo = f"Hola,\n\nHaz clic en el siguiente enlace para restablecer tu contraseña:\n{link}\n\nEste enlace expirará en 30 minutos."
            enviar_correo_generico(email, "Restablecimiento de Contraseña - WYDGARDEN", cuerpo)
        flash('Si el correo existe, se ha enviado un enlace de recuperación.', 'info')
        return redirect(url_for('auth.login'))
    return render_template('recuperar-password.html')

@auth_bp.route('/restablecer-password/<token>', methods=['GET', 'POST'])
def restablecer_password(token):
    try:
        s = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
        email = s.loads(token, salt='password-reset-salt', max_age=1800)
    except (SignatureExpired, BadTimeSignature):
        flash('El enlace ha expirado o es inválido.', 'error')
        return redirect(url_for('auth.recuperar_password'))
    
    if request.method == 'POST':
        password = request.form.get('password')
        confirm = request.form.get('confirm_password')
        if password != confirm:
            flash('Las contraseñas no coinciden.', 'error')
            return render_template('cambiar-password.html', token=token, email=email)
        err = validar_password_fuerte(password)
        if err:
            flash(err, 'error')
            return render_template('cambiar-password.html', token=token, email=email)
        user = Usuario.query.filter_by(email=email).first()
        user.password = generate_password_hash(password)
        db.session.commit()
        flash('Tu contraseña ha sido actualizada.', 'success')
        return redirect(url_for('auth.login'))
    return render_template('cambiar-password.html', token=token, email=email)

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))
