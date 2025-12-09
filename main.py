import sys
from PySide6.QtWidgets import QApplication, QDialog
from ui.dialogs import LoginDialog
from ui.main_window import ProductivityWidget
from datetime import datetime

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # 1. Mostrar Login
    login = LoginDialog()
    if login.exec() == QDialog.Accepted:
        
        # 2. Si el login es correcto, iniciar la app principal
        widget = ProductivityWidget()
        widget.usuario_actual = login.usuario_actual
        
        # Inicializar datos del usuario logueado
        widget.actualizar_interfaz_usuario()
        widget.cargar_tareas_locales()
        widget.iniciar_revision_automatica()
        
        widget.show()
        sys.exit(app.exec())
    else:
        # Si cancela el login, cerrar todo
        sys.exit(0)