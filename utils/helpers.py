import sys
import os

def resource_path(relative_path):
    """
    Obtiene la ruta absoluta para los recursos.
    Funciona tanto en el entorno de desarrollo como en el ejecutable compilado con PyInstaller.
    """
    try:
        # PyInstaller crea una carpeta temporal y almacena la ruta en _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        # En el entorno de desarrollo normal
        base_path = os.path.abspath(".")
    
    return os.path.join(base_path, relative_path)