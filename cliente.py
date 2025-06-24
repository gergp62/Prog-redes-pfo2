import requests
import json
import base64

# --- Configuración del cliente ---
BASE_URL = "http://127.0.0.1:5000"

# Almacenaremos las credenciales del usuario autenticado aquí
# para poder usarlas en solicitudes protegidas.

AUTH_USERNAME = None
AUTH_PASSWORD = None

def registrar_usuario(usuario, contrasena):
    """
    Envía una solicitud POST para registrar un nuevo usuario.
    """
    url = f"{BASE_URL}/registro"
    headers = {"Content-Type": "application/json"}
    payload = {"usuario": usuario, "contraseña": contrasena}
    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()  # Lanza una excepción para errores HTTP (4xx o 5xx)
        print(f"Registro: {response.status_code} - {response.json().get('mensaje')}")
        return True
    except requests.exceptions.RequestException as e:
        print(f"Error al registrar usuario: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"  Detalles del error: {e.response.status_code} - {e.response.json().get('mensaje', 'Error desconocido')}")
        return False

def iniciar_sesion(usuario, contrasena):
    """
    Envía una solicitud POST para iniciar sesión y almacena las credenciales para futuras solicitudes.
    """
    global AUTH_USERNAME, AUTH_PASSWORD
    url = f"{BASE_URL}/login"
    headers = {"Content-Type": "application/json"}
    payload = {"usuario": usuario, "contraseña": contrasena}
    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        print(f"Login: {response.status_code} - {response.json().get('mensaje')}")
        if response.status_code == 200:
            AUTH_USERNAME = usuario
            AUTH_PASSWORD = contrasena
            return True
        return False
    except requests.exceptions.RequestException as e:
        print(f"Error al iniciar sesión: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"  Detalles del error: {e.response.status_code} - {e.response.json().get('mensaje', 'Error desconocido')}")
        AUTH_USERNAME = None
        AUTH_PASSWORD = None
        return False

def obtener_tareas():
    """
    Envía una solicitud GET a la ruta protegida /tareas.
    Usa autenticación básica si el usuario ha iniciado sesión.
    """
    url = f"{BASE_URL}/tareas"
    headers = {}
    if AUTH_USERNAME and AUTH_PASSWORD:
        # Codifica las credenciales en Base64 para Basic Auth
        credentials = f"{AUTH_USERNAME}:{AUTH_PASSWORD}"
        encoded_credentials = base64.b64encode(credentials.encode()).decode()
        headers["Authorization"] = f"Basic {encoded_credentials}"
    else:
        print("Advertencia: No hay usuario autenticado. La solicitud a /tareas podría fallar.")

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()

        
        print(f"Obtener Tareas: {response.status_code}")
        print("\n--- Contenido HTML de la página de Tareas ---")
        print(response.text)
        print("---------------------------------------------")
        return True
    except requests.exceptions.RequestException as e:
        print(f"Error al obtener tareas: {e}")
        if hasattr(e, 'response') and e.response is not None:
            if e.response.status_code == 401:
                print("  Acceso no autorizado. Por favor, inicie sesión primero.")
            else:
                print(f"  Detalles del error: {e.response.status_code} - {e.response.text}")
        return False

def menu():
    """
    Muestra un menú interactivo en consola para interactuar con la API.
    """
    print("\n--- Cliente de Gestión de Tareas ---")
    while True:
        print("\nOpciones:")
        print("1. Registrar nuevo usuario")
        print("2. Iniciar sesión")
        print("3. Ver página de tareas (requiere sesión)")
        print("4. Salir")

        choice = input("Seleccione una opción: ")

        if choice == '1':
            user = input("Ingrese nombre de usuario para registrar: ")
            pw = input("Ingrese contraseña para registrar: ")
            registrar_usuario(user, pw)
        elif choice == '2':
            user = input("Ingrese nombre de usuario para iniciar sesión: ")
            pw = input("Ingrese contraseña para iniciar sesión: ")
            iniciar_sesion(user, pw)
        elif choice == '3':
            obtener_tareas()
        elif choice == '4':
            print("Saliendo del cliente.")
            break
        else:
            print("Opción no válida. Intente de nuevo.")

if __name__ == '__main__':
    
    print("Asegúrese de que el servidor (servidor.py) esté en ejecución en http://127.0.0.1:5000")
    menu()