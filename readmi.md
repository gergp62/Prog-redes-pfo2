# Sistema de Gestión de Tareas con API y Base de Datos

Este proyecto implementa una API RESTful simple utilizando **Flask** para la gestión de usuarios y un endpoint de bienvenida protegido. Utiliza **SQLite** como base de datos para la persistencia de datos y **Werkzeug** para el hasheo seguro de contraseñas, además de **Flask-HTTPAuth** para la autenticación básica HTTP.

## Características

* **Registro de Usuarios:** Permite a los usuarios registrarse con nombre de usuario y contraseña (hasheada).
* **Inicio de Sesión:** Verifica las credenciales de los usuarios para el acceso.
* **Gestión de Tareas (Bienvenida):** Un endpoint protegido por autenticación que muestra una página HTML de bienvenida personalizada.
* **Persistencia de Datos:** Utiliza **SQLite** para almacenar los usuarios de forma persistente en un archivo `database.db`.
* **Seguridad:** Implementa hasheo de contraseñas para protección y autenticación básica HTTP para control de acceso.

## Estructura del Proyecto

├───servidor.py             # Código de la API Flask y lógica de base de datos
├───README.md               # Documentación del proyecto
├───database.db             # Archivo de la base de datos SQLite (se generará automáticamente)
└───templates
└───index.html          # Plantilla HTML para la página de bienvenida

## Requisitos

* Python 3.x
* `pip` (gestor de paquetes de Python)

## Instalación

1.  **Clona este repositorio (o descarga los archivos):**
    ```bash
    git clone [URL_DE_TU_REPOSITORIO]
    cd [nombre_de_tu_repositorio]
    ```
    Si descargaste el ZIP, descomprímelo y navega a la carpeta principal del proyecto.

2.  **Crea un entorno virtual (muy recomendado para aislar dependencias):**
    ```bash
    python -m venv venv
    ```

3.  **Activa el entorno virtual:**
    * **En Windows:**
        ```bash
        .\venv\Scripts\activate
        ```
    * **En macOS/Linux:**
        ```bash
        source venv/bin/activate
        ```

4.  **Instala las dependencias necesarias:**
    ```bash
    pip install Flask Flask-SQLAlchemy Werkzeug Flask-HTTPAuth
    ```

## Ejecución del Servidor

1.  Asegúrate de que tu entorno virtual esté activado.
2.  Desde el directorio raíz del proyecto (donde se encuentra `servidor.py`), ejecuta el archivo:
    ```bash
    python servidor.py
    ```
    El servidor se iniciará y estará disponible en `http://127.0.0.1:5000/`. En tu terminal, deberías ver una salida similar a:
    ```
     * Running on [http://127.0.0.1:5000/](http://127.0.0.1:5000/) (Press CTRL+C to quit)
     * Restarting with stat
     * Debugger is active!
     * Debugger PIN: XXX-XXX-XXX
    ```
    Si es la primera vez que ejecutas el servidor, también verás el mensaje: `Usuario 'admin' creado con contraseña 'adminpass'`, indicando que se ha inicializado la base de datos y un usuario de prueba.

## Pruebas de la API

Puedes utilizar herramientas como **Postman**, **Insomnia**, o `curl` (desde tu terminal) para interactuar con la API.

### 1. Registrar un Usuario (POST /registro)

* **URL:** `http://127.0.0.1:5000/registro`
* **Método:** `POST`
* **Headers:**
    * `Content-Type: application/json`
* **Body (raw JSON):**
    ```json
    {
        "usuario": "nuevo_usuario",
        "contraseña": "mi_clave_segura"
    }
    ```
* **Respuesta esperada (201 Created):**
    ```json
    {
        "mensaje": "Usuario registrado exitosamente"
    }
    ```
    *(Intenta registrar el mismo usuario de nuevo para ver la respuesta 409 Conflict.)*

### 2. Iniciar Sesión (POST /login)

* **URL:** `http://127.0.0.1:5000/login`
* **Método:** `POST`
* **Headers:**
    * `Content-Type: application/json`
* **Body (raw JSON):**
    ```json
    {
        "usuario": "nuevo_usuario",
        "contraseña": "mi_clave_segura"
    }
    ```
* **Respuesta esperada (200 OK):**
    ```json
    {
        "mensaje": "Inicio de sesión exitoso"
    }
    ```
    *(Prueba con credenciales incorrectas para ver la respuesta 401 Unauthorized.)*

### 3. Acceder a Tareas (GET /tareas) - **Protegido con Autenticación Básica**

* **URL:** `http://127.0.0.1:5000/tareas`
* **Método:** `GET`
* **Headers:**
    * **Authorization:** `Basic base64(nombre_de_usuario:contraseña)`
        * **Ejemplo para el usuario 'admin':**
            * Cadena a codificar: `admin:adminpass`
            * En un navegador o Postman/Insomnia, usa la opción "Basic Auth" e ingresa el nombre de usuario y la contraseña. La herramienta se encargará de codificarlo.
            * Si usas `curl` o necesitas la codificación manual (solo para entender):
                * En Linux/macOS: `echo -n "admin:adminpass" | base64` (resultado típico: `YWRtaW46YWRtaW5wYXNz`)
                * En Python: `import base64; base64.b64encode(b"admin:adminpass").decode()`
            * Entonces, el encabezado completo sería similar a: `Authorization: Basic YWRtaW46YWRtaW5wYXNz`
* **Respuesta esperada (200 OK y página HTML):**
    Se cargará una página HTML en tu navegador (o el cliente HTTP mostrará el HTML) con un mensaje de bienvenida personalizado, por ejemplo:
    ```html
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <title>Bienvenido a la Gestión de Tareas</title>
        </head>
    <body>
        <div class="container">
            <h1>¡Bienvenido a la Gestión de Tareas!</h1>
            <p>Hola, <span class="username">admin</span>.</p>
            <p>Esta es tu página principal de gestión de tareas.</p>
            <p>Pronto podrás ver y administrar tus tareas aquí.</p>
        </div>
    </body>
    </html>
    ```
    *(Si intentas acceder a `/tareas` sin el encabezado `Authorization` o con credenciales incorrectas, recibirás un `401 Unauthorized`.)*

---