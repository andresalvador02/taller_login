from flask import Flask, render_template, request, redirect, session
import sqlite3

app = Flask(__name__)
app.secret_key = 'secreto123'

def crear_db():
    conn = sqlite3.connect('usuarios.db')
    c = conn.cursor()
    c.execute('CREATE TABLE IF NOT EXISTS usuarios (id INTEGER PRIMARY KEY, username TEXT UNIQUE, password TEXT)')
    conn.commit()
    conn.close()

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
        clave = request.form['clave']
        conn = sqlite3.connect('usuarios.db')
        c = conn.cursor()
        c.execute('INSERT INTO usuarios (username, password) VALUES (?, ?)', (usuario, clave))
        conn.commit()
        conn.close()
        return redirect('/login')
    return render_template('registro.html')

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
    crear_db()
    app.run(debug=True)