from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
import os

# -----------------------------
# CONEXIÓN
# -----------------------------
# URI de conexión
uri = "mongodb+srv://adtrivi_db_user:cwFR2yBmZO5Fis11@cluster0.gptz0ij.mongodb.net/?appName=Cluster0"

client = None
db = None
usuarios = None
tareas = None

try:
    # Crear cliente y conectar
    client = MongoClient(uri, server_api=ServerApi('1'))
    # Verificar conexión
    client.admin.command('ping')
    
    # Selecciona base de datos y colecciones
    db = client["RelojAtlasDB"]
    usuarios = db["usuarios"]
    tareas = db["tareas"]
    print("✅ Conectado correctamente a MongoDB Atlas.")
except Exception as e:
    print("❌ Error de conexión a MongoDB:", e)


# -----------------------------
# FUNCIONES DE USUARIOS
# -----------------------------

def generar_id():
    """Genera un ID de usuario numérico secuencial."""
    ultimo = usuarios.find_one(sort=[("id_usuario", -1)])
    if ultimo:
        nuevo_id = ultimo["id_usuario"] + 1
    else:
        nuevo_id = 1000
    return nuevo_id

def insertar_usuario(nombre, tipo):
    """Inserta un nuevo usuario recibiendo los datos como parámetros."""
    nuevo_id = generar_id()
    nuevo_usuario = {
        "id_usuario": nuevo_id,
        "nom_usuario": nombre,
        "tp_usuario": tipo
    }
    usuarios.insert_one(nuevo_usuario)
    return nuevo_id

def buscar_usuario_por_id(id_usuario):
    """Busca un usuario por su ID numérico y lo retorna."""
    try:
        usuario = usuarios.find_one({"id_usuario": int(id_usuario)})
        return usuario
    except ValueError:
        return None

# -----------------------------
# FUNCIONES DE TAREAS
# -----------------------------

def generar_id_tarea():
    """Genera un ID secuencial para tareas."""
    ultimo = tareas.find_one(sort=[("id_tarea", -1)]) 
    if ultimo is None:
        nuevo_id = 1
    else:
        # Aseguramos que sea int
        nuevo_id = int(ultimo["id_tarea"]) + 1
    return nuevo_id

def insertar_tarea(id_usuario, tipo_tarea, descripcion):
    """Inserta una nueva tarea para un usuario."""
    nuevo_id = generar_id_tarea()
    nueva_tarea = {
        "id_tarea": nuevo_id,
        "tp_tarea": tipo_tarea,
        "desc_tareas": descripcion,
        "Us_tarea": id_usuario,
        "Us_estado": "Pendiente"
    }
    tareas.insert_one(nueva_tarea)
    return nuevo_id

def obtener_tareas_pendientes(id_usuario):
    """Obtiene solo las tareas pendientes de un usuario."""
    try:
        # Asegurar que el ID sea int para la búsqueda
        tareas_pendientes = list(tareas.find({
            "Us_tarea": int(id_usuario),
            "Us_estado": "Pendiente"
        }))
        return tareas_pendientes
    except Exception as e:
        print(f"Error obteniendo tareas pendientes: {e}")
        return []

def actualizar_estado_tarea(id_tarea, nuevo_estado):
    """Actualiza el estado de una tarea."""
    try:
        resultado = tareas.update_one(
            {"id_tarea": id_tarea},
            {"$set": {"Us_estado": nuevo_estado}}
        )
        return resultado.modified_count > 0
    except Exception as e:
        print(f"Error actualizando estado de tarea: {e}")
        return False

def obtener_todos_los_empleados():
    """Devuelve una lista con todos los usuarios que son 'empleado'."""
    try:
        return list(usuarios.find({"tp_usuario": "empleado"}))
    except Exception as e:
        print(f"Error obteniendo empleados: {e}")
        return []    