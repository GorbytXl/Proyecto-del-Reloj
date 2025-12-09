import PyInstaller.__main__
import os

# Nombre de tu proyecto
PROJECT_NAME = "RelojProductivo"

# 1. COMPILAR EL RELOJ (EMPLEADO)
print("🚀 Compilando RELOJ DEL EMPLEADO...")
PyInstaller.__main__.run([
    'main.py',
    '--name=RelojEmpleado',
    '--onefile',
    '--noconsole',
    '--clean',                       # <--- AGREGADO: Limpia caché antes de empezar
    '--icon=assets/Reloj.ico',
    
    # Recursos
    '--add-data=assets;assets',      
    '--add-data=ui;ui',
    '--add-data=database;database',
    '--add-data=utils;utils',
    
    # Imports ocultos
    '--hidden-import=pymongo',
    '--hidden-import=dns',
    '--hidden-import=PySide6',
])

# 2. COMPILAR EL ADMIN (JEFE)
print("🚀 Compilando PANEL ADMINISTRADOR...")
PyInstaller.__main__.run([
    'admin_launcher.py',
    '--name=PanelAdmin',
    '--onefile',
    '--noconsole',
    '--clean',                       # <--- AGREGADO: Limpia caché antes de empezar
    '--icon=assets/Reloj.ico',
    
    # Recursos
    '--add-data=assets;assets',
    '--add-data=ui;ui',
    '--add-data=admin;admin',
    '--add-data=database;database',
    '--add-data=utils;utils',
    
    '--hidden-import=pymongo',
    '--hidden-import=dns',
    '--hidden-import=PySide6',
])

print("✅ ¡COMPILACIÓN FINALIZADA!")