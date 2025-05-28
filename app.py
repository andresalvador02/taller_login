from flask import Flask, render_template, request, redirect, session, flash, url_for
import sqlite3
import os
import re
import random
import string
from flask_mail import Mail, Message

app = Flask(__name__)
app.secret_key = 'secreto123'

# Configuración de Flask-Mail con Gmail SMTP
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'andretellos@gmail.com'  # Tu correo Gmail real
app.config['MAIL_PASSWORD'] = 'xtmmeidirxfindgw'       # Tu contraseña de aplicación sin espacios
app.config['MAIL_DEFAULT_SENDER'] = 'andretellos@gmail.com'  # Igual que MAIL_USERNAME

mail = Mail(app)

# Para guardar códigos temporales para recuperación de contraseña
recuperacion_codigos = {}

def crear_db():
    conn = sqlite3.connect('usuarios.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY,
            correo TEXT UNIQUE,
            password TEXT
        )
    ''')
    conn.commit()
    conn.close()

crear_db()

def validar_password(pw):
    # Debe contener al menos una mayúscula, una minúscula y un carácter especial
    if len(pw) < 6:  # mínimo 6 caracteres
        return False
    if not re.search(r'[A-Z]', pw):
        return False
    if not re.search(r'[a-z]', pw):
        return False
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', pw):
        return False
    return True

def enviar_codigo(correo, codigo):
    msg = Message('Código de recuperación de contraseña',
                  recipients=[correo])
    msg.body = f'Tu código para recuperar la contraseña es: {codigo}'
    mail.send(msg)

@app.route('/')
def inicio():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        correo = request.form['correo']
        clave = request.form['clave']
        conn = sqlite3.connect('usuarios.db')
        c = conn.cursor()
        c.execute('SELECT * FROM usuarios WHERE correo=? AND password=?', (correo, clave))
        data = c.fetchone()
        conn.close()
        if data:
            session['correo'] = correo
            return redirect(url_for('bienvenido'))
        else:
            flash("Credenciales incorrectas")
    return render_template('login.html')

@app.route('/registro', methods=['GET', 'POST'])
def registro():
    if request.method == 'POST':
        correo = request.form['correo']
        clave = request.form['clave']

        if not validar_password(clave):
            flash("La contraseña debe tener al menos una mayúscula, una minúscula, un carácter especial y mínimo 6 caracteres.")
            return redirect(url_for('registro'))

        conn = sqlite3.connect('usuarios.db')
        c = conn.cursor()
        try:
            c.execute('INSERT INTO usuarios (correo, password) VALUES (?, ?)', (correo, clave))
            conn.commit()
            flash("Registro exitoso, ya puedes iniciar sesión")
        except sqlite3.IntegrityError:
            flash("El correo ya está registrado.")
            return redirect(url_for('registro'))
        finally:
            conn.close()
        return redirect(url_for('login'))
    return render_template('registro.html')

@app.route('/bienvenido')
def bienvenido():
    if 'correo' in session:
        return f"Hola {session['correo']}! <a href='{url_for('logout')}'>Cerrar sesión</a>"
    else:
        return redirect(url_for('login'))

@app.route('/logout')
def logout():
    session.pop('correo', None)
    return redirect(url_for('login'))

@app.route('/recuperar', methods=['GET', 'POST'])
def recuperar():
    if request.method == 'POST':
        correo = request.form['correo']
        conn = sqlite3.connect('usuarios.db')
        c = conn.cursor()
        c.execute('SELECT * FROM usuarios WHERE correo=?', (correo,))
        data = c.fetchone()
        conn.close()
        if data:
            codigo = ''.join(random.choices(string.digits, k=6))
            recuperacion_codigos[correo] = codigo
            try:
                enviar_codigo(correo, codigo)
                flash("Código enviado a tu correo.")
                return redirect(url_for('validar_codigo', correo=correo))
            except Exception as e:
                flash(f"Error al enviar correo: {e}")
        else:
            flash("Correo no registrado.")
    return render_template('recuperar.html')

@app.route('/validar_codigo', methods=['GET', 'POST'])
def validar_codigo():
    correo = request.args.get('correo')

    # Si no se proporciona el correo, redirige a la página de recuperación
    if not correo:
        flash("Correo no especificado. Intenta de nuevo.")
        return redirect(url_for('recuperar'))

    if request.method == 'POST':
        codigo_ingresado = request.form.get('codigo', '').strip()

        # Verifica si el código existe para ese correo
        codigo_correcto = recuperacion_codigos.get(correo)
        if not codigo_correcto:
            flash("No se encontró un código para este correo. Solicita uno nuevo.")
            return redirect(url_for('recuperar'))

        if codigo_correcto == codigo_ingresado:
            # Si el código es correcto, borra el código y redirige
            recuperacion_codigos.pop(correo, None)
            return redirect(url_for('nueva_clave', correo=correo))
        else:
            flash("Código incorrecto. Inténtalo de nuevo.")

    return render_template('validar_codigo.html', correo=correo)

@app.route('/nueva_clave', methods=['GET', 'POST'])
def nueva_clave():
    correo = request.args.get('correo')
    if not correo:
        return redirect(url_for('recuperar'))
    if request.method == 'POST':
        nueva_pw = request.form['nueva_clave']
        if not validar_password(nueva_pw):
            flash("La contraseña debe tener al menos una mayúscula, una minúscula, un carácter especial y mínimo 6 caracteres.")
            return redirect(url_for('nueva_clave', correo=correo))
        conn = sqlite3.connect('usuarios.db')
        c = conn.cursor()
        c.execute('UPDATE usuarios SET password=? WHERE correo=?', (nueva_pw, correo))
        conn.commit()
        conn.close()
        recuperacion_codigos.pop(correo, None)
        flash("Contraseña actualizada con éxito. Por favor inicia sesión.")
        return redirect(url_for('login'))
    return render_template('nueva_clave.html', correo=correo)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8000))
    app.run(host='0.0.0.0', port=port)
