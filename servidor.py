import os
from flask import Flask, request, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_httpauth import HTTPBasicAuth

# --- Configuración de la aplicación Flask ---
app = Flask(__name__)
# Configura la base de datos SQLite.
# 'sqlite:///database.db' indica que el archivo de la base de datos será 'database.db'
# y se creará en el mismo directorio que este script.
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
# Deshabilita el seguimiento de modificaciones de objetos SQLAlchemy.
# Esto es opcional y se suele hacer para ahorrar memoria si no necesitas esta funcionalidad.
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Inicializa la extensión SQLAlchemy con la aplicación Flask.
db = SQLAlchemy(app)
# Inicializa Flask-HTTPAuth para manejar la autenticación básica.
auth = HTTPBasicAuth()

# --- Modelos de Base de Datos ---
# Un "modelo" es una clase Python que SQLAlchemy mapea a una tabla en la base de datos.

class User(db.Model):
    """
    Modelo de usuario para la base de datos.
    Representa la tabla 'user' en SQLite.
    """
    # Columna 'id': clave primaria entera que se auto-incrementa.
    id = db.Column(db.Integer, primary_key=True)
    # Columna 'username': cadena de hasta 80 caracteres, debe ser única y no puede ser nula.
    username = db.Column(db.String(80), unique=True, nullable=False)
    # Columna 'password_hash': cadena para almacenar el hash de la contraseña, no puede ser nula.
    password_hash = db.Column(db.String(120), nullable=False)

    def __repr__(self):
        """
        Método para una representación de cadena legible del objeto User.
        Útil para depuración.
        """
        return f'<User {self.username}>'

    def set_password(self, password):
        """
        Hashea la contraseña proporcionada y la almacena en 'password_hash'.
        Utiliza 'generate_password_hash' de Werkzeug, que incorpora salting y es computacionalmente costosa.
        """
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """
        Verifica si la contraseña en texto plano proporcionada coincide con el hash almacenado.
        Utiliza 'check_password_hash' de Werkzeug para comparar de forma segura.
        """
        return check_password_hash(self.password_hash, password)

# --- Creación de la Base de Datos y Usuario por Defecto ---
# Este bloque asegura que las tablas se creen al iniciar la aplicación si no existen.
with app.app_context():
    db.create_all()
    # Opcional: Crear un usuario 'admin' por defecto si no existe en la base de datos.
    # Esto facilita las pruebas iniciales.
    if not User.query.filter_by(username='admin').first():
        admin_user = User(username='admin')
        admin_user.set_password('adminpass')
        db.session.add(admin_user)
        db.session.commit()
        print("Usuario 'admin' creado con contraseña 'adminpass'")

# --- Funciones de Autenticación de Flask-HTTPAuth ---

@auth.verify_password
def verify_password(username, password):
    """
    Esta función es un callback para Flask-HTTPAuth.
    Se ejecuta automáticamente cuando un endpoint decorado con @auth.login_required es accedido.
    Verifica las credenciales (nombre de usuario y contraseña) proporcionadas en la solicitud HTTP.
    """
    user = User.query.filter_by(username=username).first()
    # Si el usuario existe y la contraseña es correcta, retorna el nombre de usuario.
    # Flask-HTTPAuth almacena este nombre en g.current_user o auth.current_user().
    if user and user.check_password(password):
        return username
    # Si las credenciales no son válidas, retorna False, lo que resulta en un 401 Unauthorized.
    return False

# --- Endpoints de la API ---

@app.route('/')
def home():
    """
    Ruta raíz que proporciona un mensaje de bienvenida general.
    """
    return "¡Bienvenido a la API de Gestión de Tareas! Usa /registro, /login o /tareas."

@app.route('/registro', methods=['POST'])
def register():
    """
    Endpoint para el registro de nuevos usuarios.
    Espera un JSON con las claves "usuario" y "contraseña".
    """
    data = request.get_json()
    # Valida que la solicitud contenga los datos esperados.
    if not data or not 'usuario' in data or not 'contraseña' in data:
        return jsonify({"mensaje": "Se requiere usuario y contraseña"}), 400

    username = data['usuario']
    password = data['contraseña']

    # Verifica si el nombre de usuario ya está en uso.
    if User.query.filter_by(username=username).first():
        return jsonify({"mensaje": "El usuario ya existe"}), 409 # 409 Conflict

    # Crea un nuevo usuario, hashea la contraseña y lo guarda en la base de datos.
    new_user = User(username=username)
    new_user.set_password(password) # Aquí se hashea la contraseña
    db.session.add(new_user)
    db.session.commit()

    return jsonify({"mensaje": "Usuario registrado exitosamente"}), 201 # 201 Created

@app.route('/login', methods=['POST'])
def login():
    """
    Endpoint para el inicio de sesión.
    Espera un JSON con las claves "usuario" y "contraseña".
    """
    data = request.get_json()
    # Valida que la solicitud contenga los datos esperados.
    if not data or not 'usuario' in data or not 'contraseña' in data:
        return jsonify({"mensaje": "Se requiere usuario y contraseña"}), 400

    username = data['usuario']
    password = data['contraseña']

    # Busca el usuario por nombre de usuario.
    user = User.query.filter_by(username=username).first()
    # Si el usuario existe y la contraseña es correcta, el inicio de sesión es exitoso.
    if user and user.check_password(password):
        return jsonify({"mensaje": "Inicio de sesión exitoso"}), 200 # 200 OK
    else:
        return jsonify({"mensaje": "Credenciales inválidas"}), 401 # 401 Unauthorized

@app.route('/tareas', methods=['GET'])
@auth.login_required # Este decorador protege la ruta, exigiendo autenticación básica.
def get_tareas():
    """
    Endpoint protegido. Muestra una página HTML de bienvenida solo a usuarios autenticados.
    El nombre de usuario autenticado se pasa a la plantilla.
    """
    # auth.current_user() obtiene el nombre de usuario que fue verificado por verify_password.
    return render_template('index.html', username=auth.current_user())

# --- Ejecución del Servidor ---
if __name__ == '__main__':
    # Ejecuta la aplicación Flask en modo depuración.
    # En un entorno de producción, usar un servidor WSGI como Gunicorn o uWSGI.
    app.run(debug=True)