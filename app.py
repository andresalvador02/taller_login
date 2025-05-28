from flask import Flask, render_template, request, redirect, session, url_for
import sqlite3
import os
import re
import random

app = Flask(__name__)
app.secret_key = 'secreto123'

# Simulación de envío de correo con código
codes = {}  # correo -> código temporal

def crear_db():
    conn = sqlite3.connect('usuarios.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS usuarios (
                    id INTEGER PRIMARY KEY,
                    username TEXT UNIQUE,
                    correo TEXT UNIQUE,
                    password TEXT)''')
    conn.commit()
    conn.close()

crear_db()

def validar_contraseña(password):
    return (re.search(r'[A-Z]', password) and
            re.search(r'[a-z]', password) and
            re.search(r'[^a-zA-Z0-9]', password))

@app.route('/')
def inicio():
    return redirect('/login')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        usuario = request.form['usuario']
        clave = request.form['clave']
        conn = sqlite3.connect('usuarios.db')
        c = conn.cursor()
        c.execute('SELECT * FROM usuarios WHERE username=? AND password=?', (usuario, clave))
        data = c.fetchone()
        conn.close()
        if data:
            session['usuario'] = usuario
            return redirect('/bienvenido')
        else:
            return "Credenciales incorrectas"
    return render_template('login.html')

@app.route('/registro', methods=['GET', 'POST'])
def registro():
    if request.method == 'POST':
        usuario = request.form['usuario']
        correo = request.form['correo']
        clave = request.form['clave']
        if not validar_contraseña(clave):
            return "La contraseña debe tener al menos una mayúscula, una minúscula y un carácter especial."
        conn = sqlite3.connect('usuarios.db')
        c = conn.cursor()
        try:
            c.execute('INSERT INTO usuarios (username, correo, password) VALUES (?, ?, ?)', (usuario, correo, clave))
            conn.commit()
        except sqlite3.IntegrityError:
            return "El usuario o correo ya existe."
        finally:
            conn.close()
        return redirect('/login')
    return render_template('registro.html')

@app.route('/recuperar', methods=['GET', 'POST'])
def recuperar():
    if request.method == 'POST':
        correo = request.form['correo']
        conn = sqlite3.connect('usuarios.db')
        c = conn.cursor()
        c.execute('SELECT * FROM usuarios WHERE correo=?', (correo,))
        user = c.fetchone()
        conn.close()
        if user:
            codigo = str(random.randint(100000, 999999))
            codes[correo] = codigo
            print(f'Código de recuperación para {correo}: {codigo}')  # Simulación de envío de correo
            return redirect(url_for('verificar_codigo', correo=correo))
        else:
            return "Correo no encontrado."
    return render_template('recuperar.html')

@app.route('/verificar_codigo/<correo>', methods=['GET', 'POST'])
def verificar_codigo(correo):
    if request.method == 'POST':
        codigo = request.form['codigo']
        if codes.get(correo) == codigo:
            return redirect(url_for('nueva_contraseña', correo=correo))
        else:
            return "Código incorrecto."
    return render_template('verificar_codigo.html', correo=correo)

@app.route('/nueva_contraseña/<correo>', methods=['GET', 'POST'])
def nueva_contraseña(correo):
    if request.method == 'POST':
        nueva_clave = request.form['clave']
        if not validar_contraseña(nueva_clave):
            return "La contraseña debe tener al menos una mayúscula, una minúscula y un carácter especial."
        conn = sqlite3.connect('usuarios.db')
        c = conn.cursor()
        c.execute('UPDATE usuarios SET password=? WHERE correo=?', (nueva_clave, correo))
        conn.commit()
        conn.close()
        codes.pop(correo, None)
        return redirect('/login')
    return render_template('nueva_contraseña.html', correo=correo)

@app.route('/bienvenido')
def bienvenido():
    if 'usuario' in session:
        return f"Hola {session['usuario']}! <a href='/logout'>Cerrar sesión</a>"
    else:
        return redirect('/login')

@app.route('/logout')
def logout():
    session.pop('usuario', None)
    return redirect('/login')

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8000))
    app.run(host='0.0.0.0', port=port)
