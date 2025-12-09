# -----------------------------
# ui/styles.py
# -----------------------------
# Aquí guardamos todos los diseños CSS para mantener el código Python limpio.

# Estilo general para los marcos de fondo (Login, Config, Mensajes)
ESTILO_FRAME_OSCURO = """
    QFrame {
        background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #1a1c20, stop:1 #0f1012);
        border-radius: 12px;
        border: 1px solid rgba(0, 240, 255, 0.3); /* Borde Cian Sutil */
    }
"""

# Estilo común para Diálogos (Login, Tareas, Configuración)
# Incluye inputs, fechas, checkboxes y botones.
ESTILO_DIALOGOS = """
    QDialog {
        background-color: #15171a;
        color: #e0e0e0;
        font-family: 'Segoe UI', sans-serif;
    }

    /* Etiquetas */
    QLabel { 
        color: #e0e0e0; 
        font-size: 13px;
    }

    /* Campos de Texto (Inputs) - Más oscuros y con borde brillante al seleccionar */
    QLineEdit, QComboBox, QDateEdit, QTimeEdit { 
        background-color: #0f1012; 
        border: 1px solid #333; 
        border-radius: 6px; 
        padding: 8px; 
        font-size: 13px; 
        color: #00f0ff; /* Texto Cian */
        selection-background-color: #00f0ff;
        selection-color: #000;
    }
    
    /* Efecto al hacer clic en un input */
    QLineEdit:focus, QComboBox:focus, QDateEdit:focus, QTimeEdit:focus {
        border: 1px solid #00f0ff;
        background-color: #1a1c20;
    }

    /* Ajustes para ComboBox y Fechas */
    QComboBox::drop-down, QDateEdit::drop-down, QTimeEdit::up-button, QTimeEdit::down-button {
        border: none;
        background: transparent;
        width: 25px;
    }
    QComboBox::down-arrow {
        image: none;
        border-top: 5px solid #00f0ff;
        border-left: 5px solid transparent; 
        border-right: 5px solid transparent;
    }

    /* Checkbox Moderno */
    QCheckBox { 
        color: #ccc; 
        font-size: 13px;
        spacing: 8px;
    }
    QCheckBox::indicator {
        width: 16px; height: 16px; 
        border-radius: 4px;
        border: 1px solid #555; 
        background: #0f1012;
    }
    QCheckBox::indicator:checked {
        background: #00f0ff; 
        border: 1px solid #00f0ff;
    }

    /* BOTONES PRIMARIOS (Estilo Neón) */
    QPushButton {
        background-color: rgba(0, 240, 255, 0.1);
        color: #00f0ff;
        border: 1px solid rgba(0, 240, 255, 0.5);
        padding: 8px 16px;
        border-radius: 6px;
        font-weight: 600;
        min-width: 80px;
    }
    QPushButton:hover {
        background-color: rgba(0, 240, 255, 0.2);
        border: 1px solid #00f0ff;
        color: white;
        box-shadow: 0 0 10px #00f0ff; /* Efecto brillo */
    }
    QPushButton:pressed {
        background-color: rgba(0, 240, 255, 0.4);
    }
    
    /* Botón Cancelar/No (Estilo Rojo apagado) */
    QDialogButtonBox QPushButton[text="Cancel"], QPushButton[text="No"] {
        background-color: rgba(255, 100, 100, 0.1);
        color: #ff6b6b;
        border: 1px solid rgba(255, 100, 100, 0.3);
    }
    QDialogButtonBox QPushButton[text="Cancel"]:hover, QPushButton[text="No"]:hover {
        background-color: rgba(255, 100, 100, 0.2);
        border: 1px solid #ff6b6b;
        color: white;
    }
"""
# Estilo específico para el Widget Principal (Reloj y Lista de Tareas)
# ... (El resto del archivo igual, solo cambia ESTILO_MAIN_WINDOW) ...

ESTILO_MAIN_WINDOW = """
    /* --- FONDO PRINCIPAL --- */
    QFrame#main_background {
        background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #1a1c20, stop:1 #0f1012);
        border-radius: 15px;
        border: 1px solid rgba(0, 240, 255, 0.3);
    }

    /* Textos Generales */
    QLabel { color: #e0e0e0; font-family: 'Segoe UI', sans-serif; }
    
    #date_label { 
        font-size: 11px; color: #8fa0b5; font-weight: 600;
        text-transform: uppercase; letter-spacing: 1px; margin-bottom: 2px;
    }
    #time_label { 
        font-size: 42px; font-weight: 700; color: #ffffff;
        margin-top: -5px; margin-bottom: 5px;
    }
    #user_label {
        font-size: 11px; color: #00f0ff; font-weight: bold;
        background-color: rgba(0, 240, 255, 0.1);
        border: 1px solid rgba(0, 240, 255, 0.2);
        border-radius: 10px; padding: 4px 10px; margin-top: 5px;
    }

    /* Botones y Scroll */
    QPushButton { background-color: transparent; color: #666; font-size: 14px; border: none; }
    QPushButton:hover { background-color: rgba(255, 255, 255, 0.1); color: white; }
    
    QScrollArea { border: none; background: transparent; }
    QScrollArea #scroll_widget, QScrollArea #history_scroll_widget {
        background: rgba(0, 0, 0, 0.2); border-radius: 8px;
    }
    /* Botón de ELIMINAR (Papelera) */
    QPushButton#btn_eliminar {
        background-color: rgba(255, 50, 50, 0.1);
        border: 1px solid rgba(255, 50, 50, 0.3);
        border-radius: 4px;
        color: #ff4444;
        font-weight: bold;
    }
    QPushButton#btn_eliminar:hover {
        background-color: rgba(255, 50, 50, 0.3);
        border: 1px solid #ff4444;
        color: white;
    }

    /* --- ESTILOS DE TAREAS (CORREGIDO PARA QUE SE VEAN) --- */
    
    /* Base para todos los checkboxes de tareas */
    QCheckBox { 
        color: #ddd; 
        padding: 6px; 
        border-radius: 6px; 
        margin: 2px 0px; /* Separación entre tareas */
        spacing: 8px;
    }
    QCheckBox::indicator {
        width: 16px; height: 16px; border-radius: 4px;
        border: 1px solid #555; background: #222;
    }
    QCheckBox::indicator:checked {
        background: #00f0ff; border: 1px solid #00f0ff;
    }
    QCheckBox:checked { text-decoration: line-through; color: #777; }

    /* COLORES DE TAREAS (Usamos selectores específicos) */
    /* VERDE */
    QCheckBox[class="task_green"], QLabel[class="alert_green"], QLabel#task_db_green {
        background-color: rgba(0, 255, 0, 0.12);
        border: 1px solid rgba(0, 255, 0, 0.2);
        border-left: 3px solid #00ff00;
    }
    /* ROJO */
    QCheckBox[class="task_red"], QLabel[class="alert_red"], QLabel#task_db_red {
        background-color: rgba(255, 50, 50, 0.12);
        border: 1px solid rgba(255, 50, 50, 0.2);
        border-left: 3px solid #ff4444;
    }
    /* AMARILLO */
    QCheckBox[class="task_yellow"], QLabel[class="alert_yellow"], QLabel#task_db_yellow {
        background-color: rgba(255, 255, 0, 0.12);
        border: 1px solid rgba(255, 255, 0, 0.2);
        border-left: 3px solid #ffff44;
    }
    /* AZUL */
    QCheckBox[class="task_blue"], QLabel[class="alert_blue"], QLabel#task_db_blue {
        background-color: rgba(0, 240, 255, 0.12);
        border: 1px solid rgba(0, 240, 255, 0.2);
        border-left: 3px solid #00f0ff;
    }
    
    /* Estilo extra para Alertas (Labels) */
    QLabel[class^="alert_"] {
        padding: 5px;
        border-radius: 6px;
        margin: 2px 0px;
        font-weight: bold;
    }
"""

ESTILO_CALENDARIO = """
    /* La ventana del calendario */
    QWidget {
        background-color: #0f1012;
        color: white;
        font-family: 'Segoe UI', sans-serif;
    }
    
    /* La barra de navegación (Mes y flechas) */
    QCalendarWidget QWidget#qt_calendar_navigationbar { 
        background-color: #1a1c20; 
        border-bottom: 1px solid #00f0ff;
    }
    
    /* Botones de flechas y mes */
    QToolButton {
        color: #00f0ff;
        background: transparent;
        font-weight: bold;
        icon-size: 24px;
    }
    QToolButton:hover {
        background-color: rgba(0, 240, 255, 0.1);
        border-radius: 4px;
    }
    
    /* La grilla de días */
    QTableView {
        background-color: #0f1012;
        alternate-background-color: #15171a;
        selection-background-color: rgba(0, 240, 255, 0.2); /* Fondo selección */
        selection-color: white;                             /* Texto selección */
        gridline-color: #222;
        outline: 0;
    }
    
    /* Cabecera de días (Lun, Mar...) */
    QCalendarWidget QHeaderView {
        background-color: #1a1c20;
    }
"""

ESTILO_ADMIN = """
    /* Fondo General */
    QWidget {
        background-color: #0f1012;
        color: white;
        font-family: 'Segoe UI', sans-serif;
    }
    
    /* Sidebar (Menú Izquierdo) */
    QFrame#sidebar {
        background-color: #1a1c20;
        border-right: 1px solid #00f0ff;
        min-width: 200px;
    }
    
    /* Botones del Sidebar */
    QPushButton#sidebar_btn {
        background-color: transparent;
        color: #888;
        text-align: left;
        padding: 15px;
        border: none;
        font-size: 14px;
    }
    QPushButton#sidebar_btn:hover {
        background-color: rgba(0, 240, 255, 0.1);
        color: #00f0ff;
        border-left: 4px solid #00f0ff;
    }
    QPushButton#sidebar_btn:checked {
        background-color: rgba(0, 240, 255, 0.2);
        color: white;
        border-left: 4px solid #00f0ff;
        font-weight: bold;
    }

    /* Tablas de Datos (Usuarios/Tareas) */
    QTableWidget {
        background-color: #15171a;
        gridline-color: #333;
        border: 1px solid #333;
        selection-background-color: rgba(0, 240, 255, 0.2);
    }
    QHeaderView::section {
        background-color: #222;
        color: #00f0ff;
        padding: 5px;
        border: 1px solid #333;
    }
    
    /* Tarjetas del Dashboard */
    QFrame#card {
        background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #1a1c20, stop:1 #25282d);
        border-radius: 10px;
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
    QFrame#card:hover {
        border: 1px solid #00f0ff;
    }
"""

# admin/styles.py

# Estilos generales para la ventana de Admin
ESTILO_ADMIN_GLOBAL = """
    QWidget {
        background-color: #0f1012;
        color: white;
        font-family: 'Segoe UI', sans-serif;
    }
    
    /* Sidebar (Menú Izquierdo) */
    QFrame#sidebar {
        background-color: #1a1c20;
        border-right: 1px solid #00f0ff;
    }
    
    /* Títulos */
    QLabel#titulo_grande {
        font-size: 24px; 
        font-weight: bold; 
        color: #00f0ff;
    }
"""

# Estilos para botones del menú lateral
ESTILO_BOTON_SIDEBAR = """
    QPushButton {
        background-color: transparent;
        color: #888;
        text-align: left;
        padding: 15px;
        border: none;
        font-size: 14px;
    }
    QPushButton:hover {
        background-color: rgba(0, 240, 255, 0.1);
        color: #00f0ff;
        border-left: 4px solid #00f0ff;
    }
    QPushButton:checked {
        background-color: rgba(0, 240, 255, 0.2);
        color: white;
        border-left: 4px solid #00f0ff;
        font-weight: bold;
    }
"""

# Estilos para Inputs y Tablas (Compartido internamente en Admin)
ESTILO_WIDGETS_ADMIN = """
    /* Campos de texto */
    QLineEdit, QComboBox { 
        background-color: #15171a; 
        border: 1px solid #333; 
        border-radius: 4px; 
        padding: 5px; 
        color: white;
    }
    
    /* Botones de acción (Agregar, Buscar) */
    QPushButton#btn_accion {
        background-color: rgba(0, 240, 255, 0.15);
        color: #00f0ff;
        border: 1px solid #00f0ff;
        border-radius: 4px;
        padding: 6px 12px;
        font-weight: bold;
    }
    QPushButton#btn_accion:hover {
        background-color: rgba(0, 240, 255, 0.3);
        color: white;
    }

    /* Tablas */
    QTableWidget {
        background-color: #15171a;
        gridline-color: #333;
        border: 1px solid #333;
        selection-background-color: rgba(0, 240, 255, 0.2);
        color: white;
    }
    QHeaderView::section {
        background-color: #222;
        color: #00f0ff;
        padding: 5px;
        border: 1px solid #333;
        font-weight: bold;
    }
"""

ESTILO_TOOLTIP = """
    QToolTip {
        background-color: #0f1012;
        color: #00f0ff;
        border: 1px solid #00f0ff;
        padding: 5px;
        font-family: 'Segoe UI';
        font-size: 12px;
    }
"""