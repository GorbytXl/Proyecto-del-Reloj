import json
from pathlib import Path
from PySide6.QtCore import QDate, Qt

# -----------------------------
# CONFIGURACIÓN DE RUTAS
# -----------------------------
# Creamos la carpeta automáticamente en Documentos
BASE_DIR = Path.home() / "Documents" / "ProductivityApp"
BASE_DIR.mkdir(parents=True, exist_ok=True)

ARCHIVO_HISTORIAL = BASE_DIR / "historial.json"
ARCHIVO_ALARMAS = BASE_DIR / "alarms.json"

def get_ruta_tareas(id_usuario):
    """Devuelve la ruta del archivo de tareas para un usuario específico."""
    return BASE_DIR / f"tareas_usuario_{id_usuario}.json"

# -----------------------------
# FUNCIONES DE ALMACENAMIENTO
# -----------------------------

def guardar_tareas(id_usuario, lista_tareas):
    ruta = get_ruta_tareas(id_usuario)
    datos = {
        "usuario": id_usuario,
        "tareas": lista_tareas
    }
    try:
        with open(ruta, 'w', encoding='utf-8') as f:
            json.dump(datos, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"⚠️ Error guardando tareas locales: {e}")

def cargar_tareas(id_usuario):
    ruta = get_ruta_tareas(id_usuario)
    if not ruta.exists():
        return []
    
    try:
        with open(ruta, 'r', encoding='utf-8') as f:
            datos = json.load(f)
            # Verificamos que el archivo sea del usuario correcto
            if str(datos.get("usuario")) == str(id_usuario):
                return datos.get("tareas", [])
    except Exception as e:
        print(f"⚠️ Error cargando tareas locales: {e}")
    return []

def guardar_alarmas(lista_alarmas):
    try:
        with open(ARCHIVO_ALARMAS, 'w', encoding='utf-8') as f:
            json.dump(lista_alarmas, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"⚠️ Error guardando alarmas: {e}")

def cargar_alarmas():
    if not ARCHIVO_ALARMAS.exists():
        return []
    try:
        with open(ARCHIVO_ALARMAS, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"⚠️ Error cargando alarmas: {e}")
        return []

def guardar_historial(tarea_data):
    """Agrega una tarea completada al historial de hoy."""
    fecha_hoy = QDate.currentDate().toString("yyyy-MM-dd")
    data_historial = {}

    # 1. Cargar historial existente
    if ARCHIVO_HISTORIAL.exists():
        try:
            with open(ARCHIVO_HISTORIAL, 'r', encoding='utf-8') as f:
                data_historial = json.load(f)
        except:
            data_historial = {}

    # 2. Agregar nueva entrada
    if fecha_hoy not in data_historial:
        data_historial[fecha_hoy] = []
    
    data_historial[fecha_hoy].append(tarea_data)

    # 3. Guardar
    try:
        with open(ARCHIVO_HISTORIAL, 'w', encoding='utf-8') as f:
            json.dump(data_historial, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"⚠️ Error actualizando historial: {e}")

def cargar_historial_completo():
    if not ARCHIVO_HISTORIAL.exists():
        return {}
    try:
        with open(ARCHIVO_HISTORIAL, 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return {}