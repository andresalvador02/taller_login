
# Taller Login Flask

Proyecto de ejemplo para un sistema de login con Flask, HTML, CSS y SQLite.

## Archivos

- **app.py**: Archivo principal de la aplicación.
- **templates/**: Carpeta con las plantillas HTML (login y registro).
- **static/style.css**: Estilos CSS.
- **.gitignore**: Archivos ignorados por Git.

## Instalación y ejecución

1. Clona o descarga este repositorio.
2. Entra a la carpeta:
   ```bash
   cd taller_login_repo_ready
   ```
3. Instala Flask:
   ```bash
   pip install flask
   ```
4. Ejecuta la aplicación:
   ```bash
   python app.py
   ```
5. Abre en el navegador:
   ```
   http://127.0.0.1:5000/registro
   ```
   Para crear un usuario, luego:
   ```
   http://127.0.0.1:5000/login
   ```
   Para iniciar sesión.

## GitHub

Para subirlo a tu repositorio **taller_login**, ejecuta:

```bash
git init
git add .
git commit -m "Primer commit: login con Flask"
git config --global user.name "André Salvador Tello Sosa"
git config --global user.email "andretellos@gmail.com"
git branch -M main
git remote add origin https://github.com/andresalvador02/taller_login.git
git push -u origin main
```
