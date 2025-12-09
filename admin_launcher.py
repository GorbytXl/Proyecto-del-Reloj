import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QPushButton, QStackedWidget, QLabel, QFrame
from PySide6.QtCore import Qt

# Importamos del paquete admin (ASEGURATE DE IMPORTAR TareasView)
from admin.dialogs import AdminLoginDialog
from admin.views import DashboardView, UsuariosView, TareasView # <--- AGREGADO TareasView
from admin.styles import ESTILO_ADMIN_GLOBAL, ESTILO_BOTON_SIDEBAR

class AdminPanel(QMainWindow):
    def __init__(self, admin_user):
        super().__init__()
        self.setWindowTitle(f"Admin Panel - {admin_user['nom_usuario']}")
        self.resize(1100, 650)
        self.setStyleSheet(ESTILO_ADMIN_GLOBAL)
        
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QHBoxLayout(main_widget)
        layout.setContentsMargins(0,0,0,0)
        layout.setSpacing(0)

        # --- SIDEBAR IZQUIERDA ---
        sidebar = QFrame()
        sidebar.setObjectName("sidebar")
        sidebar.setFixedWidth(220)
        side_lay = QVBoxLayout(sidebar)
        side_lay.setContentsMargins(0, 30, 0, 20)
        
        # Logo
        lbl_logo = QLabel("🚀 ADMIN")
        lbl_logo.setAlignment(Qt.AlignCenter)
        lbl_logo.setStyleSheet("color: white; font-weight: bold; font-size: 20px; margin-bottom: 20px;")
        side_lay.addWidget(lbl_logo)
        
        # Menú
        self.stack = QStackedWidget()
        
        self.btn1 = self.nav_btn("📊 Dashboard", 0)
        self.btn2 = self.nav_btn("👥 Usuarios", 1)
        self.btn3 = self.nav_btn("📝 Tareas", 2) # <--- AHORA SÍ ESTÁ ACTIVO
        
        side_lay.addWidget(self.btn1)
        side_lay.addWidget(self.btn2)
        side_lay.addWidget(self.btn3) # <--- AGREGADO AL LAYOUT
        side_lay.addStretch()
        
        btn_exit = QPushButton("🚪 Salir")
        btn_exit.setStyleSheet("color: #ff4444; background: transparent; padding: 15px; text-align: left; font-weight: bold;")
        btn_exit.setCursor(Qt.PointingHandCursor)
        btn_exit.clicked.connect(self.close)
        side_lay.addWidget(btn_exit)
        
        layout.addWidget(sidebar)
        
        # --- CONTENIDO DERECHA ---
        content_area = QWidget()
        content_lay = QVBoxLayout(content_area)
        content_lay.setContentsMargins(30, 30, 30, 30)
        content_lay.addWidget(self.stack)
        
        layout.addWidget(content_area)

        # Páginas
        self.stack.addWidget(DashboardView()) # Index 0
        self.stack.addWidget(UsuariosView())  # Index 1
        self.stack.addWidget(TareasView())    # Index 2 <--- AGREGADA LA VISTA
        
        self.btn1.setChecked(True)

    def nav_btn(self, text, idx):
        btn = QPushButton(text)
        btn.setStyleSheet(ESTILO_BOTON_SIDEBAR)
        btn.setCheckable(True)
        btn.setAutoExclusive(True)
        btn.setCursor(Qt.PointingHandCursor)
        btn.clicked.connect(lambda: self.stack.setCurrentIndex(idx))
        return btn

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    login = AdminLoginDialog()
    
    if login.exec():
        panel = AdminPanel(login.usuario_actual)
        panel.show()
        sys.exit(app.exec())
    
    sys.exit(0)