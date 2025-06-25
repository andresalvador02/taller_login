from flask import Flask, render_template, request, redirect, session, flash, url_for
from flask_mail import Mail, Message
import os
import re

app = Flask(__name__)
app.secret_key = os.urandom(24)

# Configuración de Flask-Mail
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'andretellos@gmail.com'
app.config['MAIL_PASSWORD'] = 'unbm vsnd otld oeka'  # Considera usar variable de entorno en producción
app.config['MAIL_DEFAULT_SENDER'] = 'andretellos@gmail.com'

mail = Mail(app)

def juegos_disponibles():
    return [
        {
            'nombre': 'Dragon Ball Sparking! ZERO',
            'precio': '262.50',
            'descripcion': '¡Revive los combates más épicos del universo Dragon Ball! Con gráficos de nueva generación...',
            'plataformas': 'PS5, Xbox Series X|S, PC',
            'genero': 'Lucha / Acción',
            'imagen': 'dragonball.png',
            'icono': '⚡'
        },
        {
            'nombre': 'FIFA 25 (Standard Edition)',
            'precio': '262.50',
            'descripcion': 'El simulador de fútbol más popular del mundo regresa con más realismo, nuevas licencias...',
            'plataformas': 'PS5, Xbox Series X|S, PC',
            'genero': 'Deportes / Simulación',
            'imagen': 'fifa25.png',
            'icono': '⚽'
        },
        {
            'nombre': 'Crash Team Racing: Nitro-Fueled',
            'precio': '150.00',
            'descripcion': '¡Prepárate para acelerar al fondo! CTR Nitro-Fueled es la experiencia definitiva de karts...',
            'plataformas': 'PS4, Xbox One, Nintendo Switch',
            'genero': 'Carreras / Arcade',
            'imagen': 'crash.png',
            'icono': '🏁'
        },
        {
            'nombre': 'Super Smash Bros Ultimate',
            'precio': '225.00',
            'descripcion': '¡Juego de lucha de ensueño! Con más de 80 personajes de franquicias icónicas...',
            'plataformas': 'Nintendo Switch',
            'genero': 'Lucha / Party Game',
            'imagen': 'smash.png',
            'icono': '🔥'
        }
    ]

@app.route('/')
def inicio():
    return render_template('index.html')

@app.route('/catalogo')
def catalogo():
    juegos = juegos_disponibles()
    return render_template('catalogo.html', juegos=juegos)

@app.route('/agregar_carrito/<nombre_juego>', methods=['POST'])
def agregar_carrito(nombre_juego):
    if 'carrito' not in session:
        session['carrito'] = []

    for juego in juegos_disponibles():
        if juego['nombre'] == nombre_juego:
            session['carrito'].append(juego)
            session.modified = True
            flash(f"{juego['nombre']} añadido al carrito.")
            break

    return redirect(url_for('catalogo'))

@app.route('/carrito')
def carrito():
    carrito = session.get('carrito', [])
    total = sum(float(j['precio']) for j in carrito)
    return render_template('carrito.html', carrito=carrito, total=total)

@app.route('/pago', methods=['GET', 'POST'])
def pago():
    carrito = session.get('carrito', [])
    if not carrito:
        return redirect(url_for('catalogo'))

    if request.method == 'POST':
        nombre = request.form.get('nombre', '').strip()
        tarjeta = request.form.get('tarjeta', '').strip()
        cvv = request.form.get('cvv', '').strip()
        vencimiento = request.form.get('expiracion', '').strip()

        errores = []

        if not nombre:
            errores.append("El nombre es obligatorio.")
        if not re.fullmatch(r'\d{16}', tarjeta):
            errores.append("El número de tarjeta debe tener 16 dígitos.")
        if not re.fullmatch(r'\d{2}/\d{2}', vencimiento):
            errores.append("La fecha de expiración debe tener formato MM/AA.")
        if not re.fullmatch(r'\d{3,4}', cvv):
            errores.append("El CVV debe tener 3 o 4 dígitos.")

        if errores:
            for error in errores:
                flash(error)
            total = sum(float(j['precio']) for j in carrito)
            return render_template('pago.html', carrito=carrito, total=total)

        # 📨 Enviar correo
        try:
            total = sum(float(j['precio']) for j in carrito)
            lista_juegos = '\n'.join(f"- {j['nombre']} (S/ {j['precio']})" for j in carrito)

            mensaje = Message(
                subject="🎮 Confirmación de compra - GameZone",
                recipients=["diego.telloso@usil.pe"],
                body=f"¡Hola {nombre}!\n\nGracias por tu compra en GameZone. Aquí está el resumen:\n\n{lista_juegos}\n\nTotal: S/ {total:.2f}\n\n¡Que disfrutes tus juegos!"
            )
            mail.send(mensaje)
        except Exception as e:
            flash(f"⚠️ No se pudo enviar el correo: {str(e)}")

        session.pop('carrito', None)
        return render_template('confirmacion.html', nombre=nombre)

    total = sum(float(j['precio']) for j in carrito)
    return render_template('pago.html', carrito=carrito, total=total)

@app.route('/confirmacion')
def confirmacion():
    return render_template('confirmacion.html')

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8000))
    app.run(host='0.0.0.0', port=port, debug=True)
