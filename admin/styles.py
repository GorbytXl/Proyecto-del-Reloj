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

ESTILO_TABS = """
    QTabWidget::pane {
        border: 1px solid #333;
        background: #15171a;
        border-radius: 4px;
    }
    QTabBar::tab {
        background: #1a1c20;
        color: #888;
        padding: 8px 20px;
        margin-right: 2px;
        border-top-left-radius: 4px;
        border-top-right-radius: 4px;
    }
    QTabBar::tab:selected {
        background: rgba(0, 240, 255, 0.1);
        color: #00f0ff;
        border-bottom: 2px solid #00f0ff;
    }
    QTabBar::tab:hover {
        background: #25282d;
        color: white;
    }
"""