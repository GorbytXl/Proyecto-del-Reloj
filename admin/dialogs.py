# admin/dialogs.py
from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton
from PySide6.QtCore import Qt, QTimer
from database import mongo_db as db

# Login exclusivo para Admin
class AdminLoginDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Acceso Administrativo")
        self.setFixedSize(350, 250)
        
        # Estilo oscuro integrado
        self.setStyleSheet("""
            QDialog { background-color: #0f1012; color: white; }
            QLineEdit { background: #1a1c20; border: 1px solid #333; color: white; padding: 8px; border-radius: 4px; }
            QPushButton { background: #00f0ff; color: black; font-weight: bold; padding: 10px; border-radius: 4px; border: none; }
            QPushButton:hover { background: #80f8ff; }
        """)
        
        self.usuario_actual = None
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(30, 30, 30, 30)

        title = QLabel("🛡️ PANEL DE CONTROL")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: #00f0ff; letter-spacing: 2px;")
        layout.addWidget(title)

        layout.addWidget(QLabel("ID de Administrador:", styleSheet="color: #888;"))
        
        self.entry_id = QLineEdit()
        self.entry_id.setPlaceholderText("Ej: 9999")
        self.entry_id.setAlignment(Qt.AlignCenter)
        self.entry_id.returnPressed.connect(self.verificar)
        layout.addWidget(self.entry_id)

        self.lbl_msg = QLabel("")
        self.lbl_msg.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.lbl_msg)

        btn = QPushButton("ENTRAR AL SISTEMA")
        btn.setCursor(Qt.PointingHandCursor)
        btn.clicked.connect(self.verificar)
        layout.addWidget(btn)

    def verificar(self):
        uid = self.entry_id.text().strip()
        if not uid.isdigit():
            self.msg("❌ ID debe ser numérico", "red")
            return

        user = db.buscar_usuario_por_id(uid)
        
        if user:
            # LÓGICA PURA DE ADMIN: No nos importa si es empleado
            if "admin" in user.get("tp_usuario", "").lower():
                self.usuario_actual = user
                self.msg("✅ Acceso Autorizado", "#00ff00")
                QTimer.singleShot(800, self.accept)
            else:
                self.msg("⛔ Permisos insuficientes", "red")
        else:
            self.msg("❌ Usuario no encontrado", "red")

    def msg(self, text, color):
        self.lbl_msg.setText(text)
        self.lbl_msg.setStyleSheet(f"color: {color}; font-weight: bold;")