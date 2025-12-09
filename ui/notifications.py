import os
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QPushButton, QApplication
from PySide6.QtCore import Qt, QTimer, QDateTime, QUrl, QPropertyAnimation, QPoint
from PySide6.QtMultimedia import QSoundEffect
# Importamos la función de utilidades
from utils.helpers import resource_path

# --------------------------
# NOTIFICACIÓN DE ALARMA (La que se queda fija hasta que interactúas)
# --------------------------
class AlarmNotification(QWidget):
    def __init__(self, alarm_data, parent=None):
        super().__init__(parent)
        self.alarm_data = alarm_data
        
        # Configuración: Sin bordes, Siempre visible, Tool (no sale en barra de tareas)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setFixedSize(380, 170)

        # Posicionar abajo a la derecha
        screen_geometry = QApplication.primaryScreen().availableGeometry()
        self.move(screen_geometry.width() - self.width() - 20,
                  screen_geometry.height() - self.height() - 60)

        self.setup_ui()
        self.setup_audio()
        
        # Timer para cerrar solo (2 min)
        self.auto_close_timer = QTimer(self)
        self.auto_close_timer.timeout.connect(self.close_alarm)
        self.auto_close_timer.start(120000)

        # Efecto visual de pulso
        self.pulse_timer = QTimer(self)
        self.pulse_value = 0
        self.pulse_direction = 1
        self.pulse_timer.timeout.connect(self._pulse_step)
        self.pulse_timer.start(120)

    def setup_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)

        self.background_frame = QFrame()
        self.background_frame.setObjectName("alarm_background")
        
        color = self.alarm_data.get("color", "green")
        bg_color = self._get_background_color(color)
        
        self.background_frame.setStyleSheet(f"""
            QFrame#alarm_background {{
                background: {bg_color};
                border-radius: 12px;
                border: 1px solid rgba(255,255,255,0.2);
            }}
        """)
        
        frame_layout = QVBoxLayout(self.background_frame)
        frame_layout.setContentsMargins(14, 12, 14, 12)
        frame_layout.setSpacing(8)

        # Header
        header = QHBoxLayout()
        header.addWidget(QLabel("⏰", styleSheet="font-size: 20px; background:transparent;"))
        header.addWidget(QLabel("Recordatorio", styleSheet="font-size:16px; font-weight:600; color:#FFD966; background:transparent;"))
        header.addStretch()

        close_btn = QPushButton("✕")
        close_btn.setFixedSize(24, 24)
        close_btn.setStyleSheet("background: transparent; color: #ddd; border: none; font-size: 14px;")
        close_btn.clicked.connect(self.close_alarm)
        header.addWidget(close_btn)
        frame_layout.addLayout(header)

        # Texto Tarea
        self.task_label = QLabel(self.alarm_data.get("text", "Tarea"))
        self.task_label.setWordWrap(True)
        self.task_label.setStyleSheet("font-size: 13px; padding: 8px; border-radius: 8px; background: rgba(0,0,0,0.3); color: white;")
        frame_layout.addWidget(self.task_label)

        # Botones
        btn_row = QHBoxLayout()
        
        snooze_btn = QPushButton("Posponer 5m")
        snooze_btn.setStyleSheet("background: rgba(255,255,255,0.1); color: #ddd; border: 1px solid #555; border-radius: 6px; padding: 4px 8px;")
        snooze_btn.clicked.connect(self.snooze_alarm)
        
        complete_btn = QPushButton("Completar")
        complete_btn.setStyleSheet("background: #28a745; color: white; border-radius: 6px; padding: 4px 8px; font-weight: bold; border:none;")
        complete_btn.clicked.connect(self.complete_alarm)

        btn_row.addWidget(snooze_btn)
        btn_row.addStretch()
        btn_row.addWidget(complete_btn)
        
        frame_layout.addLayout(btn_row)
        layout.addWidget(self.background_frame)
        self.setLayout(layout)

    def setup_audio(self):
        self.sound_effect = QSoundEffect()
        path = resource_path("assets/alarm.wav")
        if not os.path.exists(path): path = resource_path("alarm.wav")

        if os.path.exists(path):
            self.sound_effect.setSource(QUrl.fromLocalFile(path))
            self.sound_effect.setVolume(0.8)
            self.sound_timer = QTimer(self)
            self.sound_timer.timeout.connect(self.play_sound)
            self.sound_timer.start(2000)
            self.play_sound()

    def play_sound(self):
        if self.sound_effect:
            self.sound_effect.stop()
            self.sound_effect.play()

    def _get_background_color(self, color):
        colores = {
            "red": "qlineargradient(x1:0,y1:0,x2:0,y2:1, stop:0 #3a2326, stop:1 #2a1518)",
            "yellow": "qlineargradient(x1:0,y1:0,x2:0,y2:1, stop:0 #3a3a26, stop:1 #2a2a18)",
            "blue": "qlineargradient(x1:0,y1:0,x2:0,y2:1, stop:0 #232a3a, stop:1 #151c2a)",
            "green": "qlineargradient(x1:0,y1:0,x2:0,y2:1, stop:0 #2a3a26, stop:1 #1a2a18)",
        }
        return colores.get(color, colores["green"])

    def snooze_alarm(self):
        if self.parent() and hasattr(self.parent(), "save_snoozed_alarm"):
            new_time = QDateTime.currentDateTime().addSecs(300).toString(Qt.ISODate)
            new_data = self.alarm_data.copy()
            new_data["reminder_time"] = new_time
            self.parent().save_snoozed_alarm(new_data)
        self.close_alarm()

    def complete_alarm(self):
        if self.parent() and hasattr(self.parent(), "complete_alarm_task"):
            self.parent().complete_alarm_task(self.alarm_data)
        self.close_alarm()

    def close_alarm(self):
        if hasattr(self, "sound_timer"): self.sound_timer.stop()
        if hasattr(self, "sound_effect"): self.sound_effect.stop()
        if hasattr(self, "pulse_timer"): self.pulse_timer.stop()
        self.close()

    def _pulse_step(self):
        self.pulse_value += 0.08 * self.pulse_direction
        if self.pulse_value > 1.0 or self.pulse_value < 0.0:
            self.pulse_direction *= -1
        
        alpha = 40 + int(40 * self.pulse_value)
        if 0 <= self.pulse_value <= 1:
            bg = self._get_background_color(self.alarm_data.get("color", "green"))
            self.background_frame.setStyleSheet(f"""
                QFrame#alarm_background {{
                    background: {bg};
                    border-radius: 12px;
                    border: 1px solid rgba(255,255,255,{alpha/255:.2f});
                }}
            """)

# --------------------------
# NOTIFICACIÓN TOAST (La que aparece y desaparece sola)
# --------------------------
class ToastNotification(QWidget):
    def __init__(self, task_data, parent=None, main_widget=None):
        super().__init__(parent)
        self.task_data = task_data
        self.main_widget = main_widget
        
        # Flags para asegurar visibilidad (Siempre encima, sin marco, no roba foco)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool | Qt.X11BypassWindowManagerHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAttribute(Qt.WA_ShowWithoutActivating)
        self.setFixedSize(320, 90)
        
        self.position_window()
        self.setup_ui()
        
        # Auto-cerrar en 8 segundos
        self.close_timer = QTimer(self)
        self.close_timer.timeout.connect(self.close)
        self.close_timer.start(8000)

    def position_window(self):
        screen_geo = QApplication.primaryScreen().availableGeometry()
        # Posición: Arriba a la derecha
        self.move(screen_geo.width() - self.width() - 20, 100)

    def setup_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        
        color_name = self.task_data.get("color", "green")
        
        # --- COLORES DIFUMINADOS (TRANSPARENTES) ---
        colors = {
            "red":    ("rgba(255, 50, 50, 0.2)",  "rgba(255, 50, 50, 0.9)"),
            "yellow": ("rgba(255, 255, 50, 0.2)", "rgba(255, 255, 50, 0.9)"),
            "blue":   ("rgba(50, 200, 255, 0.2)", "rgba(50, 200, 255, 0.9)"),
            "green":  ("rgba(50, 255, 50, 0.2)",  "rgba(50, 255, 50, 0.9)")
        }
        bg_color, border_color = colors.get(color_name, colors["green"])
        
        self.background_frame = QFrame()
        self.background_frame.setCursor(Qt.PointingHandCursor)
        self.background_frame.setStyleSheet(f"""
            QFrame {{
                background-color: {bg_color};
                border: 2px solid {border_color};
                border-radius: 10px;
            }}
        """)
        
        # Layout interno
        in_layout = QVBoxLayout(self.background_frame)
        in_layout.setContentsMargins(15, 10, 15, 10)
        
        # Título
        top = QHBoxLayout()
        icon = "⏰" if self.task_data.get("has_reminder") else "📋"
        lbl_title = QLabel(f"{icon} NUEVA ASIGNACIÓN")
        lbl_title.setStyleSheet(f"color: {border_color}; font-weight:bold; font-size:12px; background: transparent;")
        top.addWidget(lbl_title)
        top.addStretch()
        
        btn_close = QPushButton("✕")
        btn_close.setFixedSize(20, 20)
        btn_close.setCursor(Qt.PointingHandCursor)
        btn_close.setStyleSheet("color: white; background: transparent; border: none; font-weight: bold;")
        btn_close.clicked.connect(self.close)
        top.addWidget(btn_close)
        
        in_layout.addLayout(top)
        
        # Texto de la tarea
        txt = self.task_data.get("text", "")
        if len(txt) > 40: txt = txt[:40] + "..."
        lbl_task = QLabel(txt)
        lbl_task.setWordWrap(True)
        lbl_task.setStyleSheet("color: white; font-size: 13px; background: transparent;")
        in_layout.addWidget(lbl_task)
        
        layout.addWidget(self.background_frame)
        self.setLayout(layout)

    def mousePressEvent(self, event):
        # Al hacer clic, abrimos el reloj principal y cerramos la notificación
        if event.button() == Qt.LeftButton:
            if self.main_widget:
                self.main_widget.show_normal()
                self.main_widget.raise_()
                self.main_widget.activateWindow()
            self.close()

    def _get_border_color(self, color):
        colores = {
            "red": "rgba(255, 100, 100, 0.5)",
            "yellow": "rgba(255, 215, 100, 0.5)",
            "blue": "rgba(100, 150, 255, 0.5)", 
            "green": "rgba(100, 255, 100, 0.5)",
        }
        return colores.get(color, colores["green"])