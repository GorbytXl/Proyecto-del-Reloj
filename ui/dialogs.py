from datetime import datetime
from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                               QLineEdit, QPushButton, QComboBox, QCheckBox, 
                               QDateEdit, QTimeEdit, QDialogButtonBox, QFrame,
                               QCalendarWidget, QTableView, QToolTip)
# AGREGAMOS QEvent AQUÍ ABAJO 👇
from PySide6.QtCore import Qt, QDate, QTime, QDateTime, QTimer, QPoint, QRect, QEvent
from PySide6.QtGui import QColor, QPainter, QBrush, QPen, QCursor

# Importaciones de nuestros módulos
from database import mongo_db as db
from ui.styles import ESTILO_DIALOGOS, ESTILO_FRAME_OSCURO, ESTILO_CALENDARIO

# --------------------------
# Login Dialog
# --------------------------
class LoginDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Acceso de Usuario")
        self.setModal(True)
        self.setFixedSize(320, 220)
        self.usuario_actual = None
        self.setStyleSheet(ESTILO_DIALOGOS)
        self.setup_ui()
    def setup_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(25, 25, 25, 25)
        lbl_titulo = QLabel("🔐 Acceso de Usuario")
        lbl_titulo.setStyleSheet("font-size: 18px; font-weight: bold; color: #FFD966; margin-bottom: 10px;")
        lbl_titulo.setAlignment(Qt.AlignCenter)
        layout.addWidget(lbl_titulo)
        input_container = QVBoxLayout()
        input_container.setSpacing(8)
        lbl_id = QLabel("ID de Usuario:")
        lbl_id.setStyleSheet("font-weight: 600;")
        input_container.addWidget(lbl_id)
        self.entry_id = QLineEdit()
        self.entry_id.setPlaceholderText("Ingrese su ID numérico...")
        self.entry_id.setFixedHeight(40)
        self.entry_id.returnPressed.connect(self.verificar_usuario)
        input_container.addWidget(self.entry_id)
        layout.addLayout(input_container)
        self.lbl_mensaje = QLabel("")
        self.lbl_mensaje.setAlignment(Qt.AlignCenter)
        self.lbl_mensaje.setWordWrap(True)
        layout.addWidget(self.lbl_mensaje)
        btn_ingresar = QPushButton("Ingresar")
        btn_ingresar.setFixedHeight(40)
        btn_ingresar.clicked.connect(self.verificar_usuario)
        layout.addWidget(btn_ingresar)
        self.setLayout(layout)
    def verificar_usuario(self):
        id_ingresado = self.entry_id.text().strip()
        if not id_ingresado.isdigit():
            self.mostrar_mensaje("❌ El ID debe ser numérico", error=True)
            return
        usuario = db.buscar_usuario_por_id(id_ingresado)
        if usuario:
            tipo = usuario.get("tp_usuario", "").lower()
            if tipo == "empleado":
                self.usuario_actual = usuario
                self.mostrar_mensaje("✅ Acceso concedido", error=False)
                QTimer.singleShot(500, self.accept)
            else:
                self.mostrar_mensaje("❌ Acceso denegado. Solo empleados.", error=True)
        else:
            self.mostrar_mensaje("❌ Usuario no encontrado", error=True)
    def mostrar_mensaje(self, texto, error=True):
        color = "#FF6B6B" if error else "#90EE90"
        bg = "rgba(255,107,107,0.1)" if error else "rgba(144,238,144,0.1)"
        self.lbl_mensaje.setText(texto)
        self.lbl_mensaje.setStyleSheet(f"color: {color}; font-size: 12px; background: {bg}; padding: 8px; border-radius: 4px;")

class CustomMessageBox(QDialog):
    def __init__(self, parent=None, mensaje="", tipo="info"):
        super().__init__(parent)
        self.setWindowFlags(Qt.Dialog | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setModal(True)
        self.setFixedSize(420, 220) # Un poco más ancho
        self.mensaje = mensaje
        self.tipo = tipo
        self.setup_ui()

    def setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        self.background_frame = QFrame()
        self.background_frame.setStyleSheet(ESTILO_FRAME_OSCURO)
        
        # Sombra para dar profundidad
        self.background_frame.setGraphicsEffect(None) # Limpiamos efectos previos si hubiera
        
        frame_layout = QVBoxLayout(self.background_frame)
        frame_layout.setSpacing(20) # Más espacio entre elementos
        frame_layout.setContentsMargins(25, 25, 25, 25)

        # Configuración de Iconos y Títulos
        configs = {
            "success": ("✅", "#28a745", "Éxito"),
            "error": ("❌", "#dc3545", "Error"),
            "warning": ("⚠️", "#ffc107", "Advertencia"),
            "question": ("❓", "#00f0ff", "¿Estás seguro?"), # Título más amigable
            "info": ("ℹ️", "#17a2b8", "Información")
        }
        icono, color_borde, titulo = configs.get(self.tipo, configs["info"])

        # Header
        header = QHBoxLayout()
        header.addWidget(QLabel(icono, styleSheet="font-size: 26px; background: transparent;"))
        header.addWidget(QLabel(titulo, styleSheet="font-size: 18px; font-weight: bold; color: white; background: transparent; font-family: 'Segoe UI';"))
        header.addStretch()
        frame_layout.addLayout(header)

        # Mensaje Central
        lbl_msg = QLabel(self.mensaje)
        lbl_msg.setWordWrap(True)
        lbl_msg.setAlignment(Qt.AlignCenter)
        # Estilo tipo "tarjeta" para el texto
        lbl_msg.setStyleSheet(f"""
            font-size: 14px; 
            color: #ddd; 
            padding: 15px; 
            background: rgba(255,255,255,0.05); 
            border-radius: 8px; 
            border-left: 4px solid {color_borde};
        """)
        frame_layout.addWidget(lbl_msg)

        # Botones
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(15) # Separación entre botones
        
        # Estilos específicos para botones de este diálogo
        style_base = """
            QPushButton { 
                font-size: 13px; font-weight: bold; border-radius: 6px; padding: 10px; min-width: 100px;
            }
        """
        
        if self.tipo == "question":
            # Botón CANCELAR (Rojo tenue)
            btn_no = QPushButton("Cancelar")
            btn_no.setCursor(Qt.PointingHandCursor)
            btn_no.setStyleSheet(style_base + """
                QPushButton { background-color: rgba(255, 50, 50, 0.15); color: #ff8888; border: 1px solid #ff4444; }
                QPushButton:hover { background-color: rgba(255, 50, 50, 0.3); color: white; }
            """)
            btn_no.clicked.connect(self.reject)
            btn_layout.addWidget(btn_no)
            
            # Botón CONFIRMAR (Verde/Cian brillante)
            btn_yes = QPushButton("Confirmar")
            btn_yes.setCursor(Qt.PointingHandCursor)
            btn_yes.setStyleSheet(style_base + """
                QPushButton { background-color: rgba(0, 255, 100, 0.15); color: #44ffaa; border: 1px solid #44ffaa; }
                QPushButton:hover { background-color: rgba(0, 255, 100, 0.3); color: white; box-shadow: 0 0 10px #44ffaa; }
            """)
            btn_yes.clicked.connect(self.accept)
            btn_layout.addWidget(btn_yes)
        else:
            # Botón ACEPTAR (Azul standard)
            btn_ok = QPushButton("Entendido")
            btn_ok.setCursor(Qt.PointingHandCursor)
            btn_ok.setStyleSheet(style_base + """
                QPushButton { background-color: rgba(0, 240, 255, 0.15); color: #00f0ff; border: 1px solid #00f0ff; }
                QPushButton:hover { background-color: rgba(0, 240, 255, 0.3); color: white; }
            """)
            btn_ok.clicked.connect(self.accept)
            btn_layout.addWidget(btn_ok)
        
        frame_layout.addLayout(btn_layout)
        main_layout.addWidget(self.background_frame)
        self.setLayout(main_layout)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.drag_pos = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton:
            self.move(event.globalPosition().toPoint() - self.drag_pos)
            event.accept()

class ConfigDialog(QDialog):
    def __init__(self, intervalo_actual, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.Dialog | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setModal(True)
        self.setFixedSize(350, 220)
        self.intervalo = intervalo_actual
        self.setup_ui()
    def setup_ui(self):
        main = QVBoxLayout(self)
        main.setContentsMargins(0,0,0,0)
        frame = QFrame()
        frame.setStyleSheet(ESTILO_FRAME_OSCURO)
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(20,20,20,20)
        layout.addWidget(QLabel("⚙️ Configuración", styleSheet="font-size: 16px; font-weight: bold; color: #FFD966;", alignment=Qt.AlignCenter))
        layout.addWidget(QLabel("Intervalo de revisión (segundos):", styleSheet="color: #CCCCCC;"))
        self.entry_int = QLineEdit(str(self.intervalo))
        layout.addWidget(self.entry_int)
        layout.addWidget(QLabel("Tiempo entre revisiones de la base de datos", styleSheet="color: #888; font-size: 11px; font-style: italic;"))
        btn = QPushButton("💾 Guardar")
        btn.clicked.connect(self.guardar)
        layout.addWidget(btn)
        main.addWidget(frame)
        self.setLayout(main)
    def guardar(self):
        try:
            val = int(self.entry_int.text())
            if val < 10:
                CustomMessageBox(self, "El intervalo mínimo es 10 segundos", "warning").exec()
                return
            self.intervalo = val
            self.accept()
        except ValueError:
            CustomMessageBox(self, "Ingrese un número válido", "error").exec()

class TaskDialog(QDialog):
    def __init__(self, parent=None, task_text=""):
        super().__init__(parent)
        self.setWindowTitle("Configurar Tarea")
        self.setModal(True)
        self.setFixedSize(420, 420)
        self.setStyleSheet(ESTILO_DIALOGOS)
        self.task_text_init = task_text
        self.setup_ui()
    def setup_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(12)
        layout.setContentsMargins(16, 16, 16, 16)

        # Campo Tarea
        layout.addWidget(QLabel("Tarea:"))
        self.task_input = QLineEdit(self.task_text_init)
        self.task_input.setPlaceholderText("Descripción de la tarea...")
        layout.addWidget(self.task_input)

        # Prioridad
        h_layout = QHBoxLayout()
        h_layout.addWidget(QLabel("Prioridad:"))
        self.combo = QComboBox()
        self.combo.addItem("🟢 Normal", "green")
        self.combo.addItem("🟡 Media", "yellow")
        self.combo.addItem("🔴 Alta", "red")
        self.combo.addItem("🔵 Informativa", "blue")
        self.combo.setFixedWidth(200)
        h_layout.addWidget(self.combo)
        layout.addLayout(h_layout)

        # Checkbox Recordatorio
        self.chk_remind = QCheckBox("Agregar recordatorio")
        self.chk_remind.toggled.connect(self.toggle_reminder)
        layout.addWidget(self.chk_remind)
        # --- PANEL DE FECHA Y HORA ---
        self.rem_panel = QVBoxLayout()

        # 1. Selector de FECHA (¡Esto es lo que faltaba!)
        d_lay = QHBoxLayout()
        d_lay.addWidget(QLabel("Fecha:"))
        self.date_edit = QDateEdit(QDate.currentDate())
        self.date_edit.setCalendarPopup(True) # Despliega un calendario al hacer clic
        self.date_edit.setEnabled(False)      # Desactivado por defecto
        self.date_edit.setDisplayFormat("dd/MM/yyyy")
        d_lay.addWidget(self.date_edit)
        
        self.rem_panel.addLayout(d_lay) # <--- ¡ESTA LÍNEA FALTABA!

        # 2. Selector de HORA
        t_lay = QHBoxLayout()
        t_lay.addWidget(QLabel("Hora:"))
        self.time_edit = QTimeEdit(QTime.currentTime().addSecs(3600))
        self.time_edit.setEnabled(False)
        self.time_edit.setDisplayFormat("hh:mm")
        t_lay.addWidget(self.time_edit)
        
        self.rem_panel.addLayout(t_lay)
        # -----------------------------

        layout.addLayout(self.rem_panel)
        layout.addWidget(QLabel("💡 La alarma sonará en el momento programado", styleSheet="color: #888; font-size: 11px; font-style: italic;"))
        layout.addStretch()
        btns = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        btns.accepted.connect(self.accept)
        btns.rejected.connect(self.reject)
        layout.addWidget(btns)
        self.setLayout(layout)
    def toggle_reminder(self, checked):
        self.date_edit.setEnabled(checked)
        self.time_edit.setEnabled(checked)
    def get_task_data(self):
        rem_time = None
        if self.chk_remind.isChecked():
            t = self.time_edit.time()
            # Combinamos la fecha seleccionada con la hora seleccionada
            rem_time = QDateTime(self.date_edit.date(), QTime(t.hour(), t.minute(), 0))
        return {
            "text": self.task_input.text().strip(),
            "color": self.combo.currentData(),
            "color_name": self.combo.currentText(),
            "has_reminder": self.chk_remind.isChecked(),
            "reminder_time": rem_time
        }



# --------------------------
# Calendario Cyberpunk Interactivo (CORREGIDO - MAPA DE CELDAS)
# --------------------------
class CyberCalendar(QCalendarWidget):
    def __init__(self, parent=None, tareas_map=None):
        super().__init__(parent)
        self.tareas_map = tareas_map if tareas_map else {}
        self.setGridVisible(False)
        self.setVerticalHeaderFormat(QCalendarWidget.NoVerticalHeader)
        self.setStyleSheet(ESTILO_CALENDARIO)
        
        # Mapa para guardar dónde está cada fecha: { "2023-12-01": QRect(x,y,w,h) }
        self.celdas_pintadas = {}
        
        # 1. ACTIVAR RASTREO
        self.setMouseTracking(True)
        
        # 2. RASTREO EN TABLA INTERNA
        tabla_interna = self.findChild(QTableView)
        if tabla_interna:
            tabla_interna.setMouseTracking(True)
            tabla_interna.viewport().installEventFilter(self)

    def paintCell(self, painter, rect, date):
        super().paintCell(painter, rect, date)
        
        # GUARDAMOS LA POSICIÓN DE ESTA FECHA EN EL MAPA
        date_str = date.toString("yyyy-MM-dd")
        self.celdas_pintadas[date_str] = rect
        
        if date_str in self.tareas_map:
            items = self.tareas_map[date_str]
            
            painter.save()
            painter.setRenderHint(QPainter.Antialiasing)
            
            radius = 3
            spacing = 8
            start_x = rect.center().x() - ((len(items) - 1) * spacing) / 2
            y_pos = rect.bottom() - 10
            
            for i, item in enumerate(items[:4]):
                color_name = item["color"]
                c = QColor(color_name)
                if color_name == "green": c = QColor("#00ff00")
                elif color_name == "red": c = QColor("#ff4444")
                elif color_name == "yellow": c = QColor("#ffff44")
                elif color_name == "blue": c = QColor("#00f0ff")
                
                painter.setBrush(QBrush(c))
                painter.setPen(Qt.NoPen)
                painter.drawEllipse(QPoint(int(start_x + (i * spacing)), int(y_pos)), radius, radius)
            painter.restore()

    def obtener_fecha_en_pos(self, pos):
        """Busca en nuestro mapa qué fecha corresponde a la posición del mouse"""
        for date_str, rect in self.celdas_pintadas.items():
            if rect.contains(pos):
                return QDate.fromString(date_str, "yyyy-MM-dd")
        return QDate() # Inválida si no encuentra nada

    def eventFilter(self, source, event):
        # Usamos QEvent.MouseMove para evitar errores de atributos
        if event.type() == QEvent.MouseMove and source == self.findChild(QTableView).viewport():
            pos = event.pos()
            
            # USAMOS NUESTRA PROPIA FUNCIÓN EN LUGAR DE dateAt
            date = self.obtener_fecha_en_pos(pos)
            
            if date.isValid():
                self.mostrar_tooltip(date, QCursor.pos())
            else:
                QToolTip.hideText()
            return False
        return super().eventFilter(source, event)

    def mostrar_tooltip(self, date, global_pos):
        date_str = date.toString("yyyy-MM-dd")
        if date_str in self.tareas_map:
            items = self.tareas_map[date_str]
            
            tooltip_text = f"""
            <div style='background-color:#0f1012; color:white; padding:4px; font-family: Segoe UI;'>
                <b style='color:#00f0ff;'>📅 {date.toString('dd/MM/yyyy')}</b>
                <hr style='background-color:#333; margin: 2px 0;'>
            """
            
            for item in items:
                c_code = item['color']
                hex_c = "#00ff00" if c_code == "green" else ("#ff4444" if c_code == "red" else ("#ffff44" if c_code == "yellow" else "#00f0ff"))
                tooltip_text += f"<div style='margin-bottom:2px;'><span style='color:{hex_c};'>●</span> {item['text']}</div>"
            
            tooltip_text += "</div>"
            QToolTip.showText(global_pos, tooltip_text, self)
        else:
            QToolTip.hideText()


class CalendarDialog(QDialog):
    def __init__(self, parent=None, tareas=None, alarmas=None):
        super().__init__(parent)
        self.setWindowTitle("Calendario de Tareas")
        self.setModal(True)
        self.setFixedSize(400, 350)
        self.setStyleSheet(ESTILO_DIALOGOS)
        
        self.mapa_tareas = self._procesar_datos(tareas, alarmas)
        self.setup_ui()

    def _procesar_datos(self, tareas, alarmas):
        mapa = {}
        
        def agregar(fecha_iso, color, texto):
            if not fecha_iso: return
            try:
                if "T" in str(fecha_iso): f = str(fecha_iso).split("T")[0]
                else: f = str(fecha_iso).split(" ")[0]
                
                if f not in mapa: mapa[f] = []
                
                # Evitar duplicados (ignorando mayúsculas/minúsculas)
                texto_limpio = str(texto).strip()
                ya_existe = any(x['text'].strip().lower() == texto_limpio.lower() for x in mapa[f])
                
                if not ya_existe:
                    mapa[f].append({"color": color, "text": texto_limpio})
            except:
                pass

        # 1. Alarmas (FILTRO: Solo ACTIVAS)
        for al in (alarmas or []):
            if al.get("status") == "active":
                agregar(al.get("reminder_time"), al.get("color", "green"), al.get("text", "Alarma"))
            
        # 2. Tareas / Notas
        for t in (tareas or []):
            fecha_final = None
            if t.get("has_reminder") and t.get("reminder_time"):
                rt = t.get("reminder_time")
                if hasattr(rt, "toString"): rt = rt.toString(Qt.ISODate)
                fecha_final = rt
            elif t.get("id_local"):
                try:
                    id_limpio = str(t["id_local"]).replace("local_", "")
                    timestamp = float(id_limpio)
                    dt = datetime.fromtimestamp(timestamp)
                    fecha_final = dt.isoformat()
                except: pass
            
            # Red de seguridad: Si no tiene fecha, es de HOY
            if not fecha_final: fecha_final = datetime.now().isoformat()
            
            if fecha_final:
                agregar(fecha_final, t.get("color", "green"), t.get("text", "Nota"))
                
        return mapa

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0,0,0,0)
        frame = QFrame()
        frame.setStyleSheet(ESTILO_FRAME_OSCURO)
        lay_frame = QVBoxLayout(frame)
        lay_frame.setContentsMargins(10,10,10,10)
        
        lbl = QLabel("📅 Calendario Activo")
        lbl.setStyleSheet("font-size: 16px; font-weight: bold; color: #00f0ff; margin-bottom: 5px;")
        lbl.setAlignment(Qt.AlignCenter)
        lay_frame.addWidget(lbl)
        
        self.calendar = CyberCalendar(self, self.mapa_tareas)
        lay_frame.addWidget(self.calendar)
        
        legend = QHBoxLayout()
        lbl_info = QLabel("Pasa el mouse sobre los días marcados para ver notas")
        lbl_info.setStyleSheet("color: #888; font-size: 11px;")
        legend.addWidget(lbl_info)
        lay_frame.addLayout(legend)
        
        btn_close = QPushButton("Cerrar")
        btn_close.clicked.connect(self.accept)
        lay_frame.addWidget(btn_close)
        
        layout.addWidget(frame)

class CalendarDialog(QDialog):
    def __init__(self, parent=None, tareas=None, alarmas=None):
        super().__init__(parent)
        self.setWindowTitle("Calendario de Tareas")
        self.setModal(True)
        self.setFixedSize(400, 350)
        self.setStyleSheet(ESTILO_DIALOGOS)
        
        self.mapa_tareas = self._procesar_datos(tareas, alarmas)
        self.setup_ui()

    def _procesar_datos(self, tareas, alarmas):
        mapa = {}
        
        def agregar(fecha_iso, color, texto):
            if not fecha_iso: return
            try:
                if "T" in str(fecha_iso): f = str(fecha_iso).split("T")[0]
                else: f = str(fecha_iso).split(" ")[0]
                
                if f not in mapa: mapa[f] = []
                
                # --- CORRECCIÓN DUPLICADOS ---
                texto_limpio = str(texto).strip()
                
                # Verificamos si ya existe una tarea con el mismo texto (ignorando case)
                ya_existe = any(x['text'].strip().lower() == texto_limpio.lower() for x in mapa[f])
                
                if not ya_existe:
                    mapa[f].append({"color": color, "text": texto_limpio})
            except:
                pass

        # 1. Alarmas (FILTRO: Solo ACTIVAS)
        for al in (alarmas or []):
            if al.get("status") == "active":
                agregar(al.get("reminder_time"), al.get("color", "green"), al.get("text", "Alarma"))
            
        # 2. Tareas
        for t in (tareas or []):
            fecha_final = None
            if t.get("has_reminder") and t.get("reminder_time"):
                rt = t.get("reminder_time")
                if hasattr(rt, "toString"): rt = rt.toString(Qt.ISODate)
                fecha_final = rt
            elif t.get("id_local"):
                try:
                    id_limpio = str(t["id_local"]).replace("local_", "")
                    timestamp = float(id_limpio)
                    dt = datetime.fromtimestamp(timestamp)
                    fecha_final = dt.isoformat()
                except: pass
            
            if not fecha_final: fecha_final = datetime.now().isoformat()
            
            if fecha_final:
                agregar(fecha_final, t.get("color", "green"), t.get("text", "Nota"))
                
        return mapa

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0,0,0,0)
        frame = QFrame()
        frame.setStyleSheet(ESTILO_FRAME_OSCURO)
        lay_frame = QVBoxLayout(frame)
        lay_frame.setContentsMargins(10,10,10,10)
        
        lbl = QLabel("📅 Calendario Activo")
        lbl.setStyleSheet("font-size: 16px; font-weight: bold; color: #00f0ff; margin-bottom: 5px;")
        lbl.setAlignment(Qt.AlignCenter)
        lay_frame.addWidget(lbl)
        
        self.calendar = CyberCalendar(self, self.mapa_tareas)
        lay_frame.addWidget(self.calendar)
        
        legend = QHBoxLayout()
        lbl_info = QLabel("Pasa el mouse sobre los días marcados")
        lbl_info.setStyleSheet("color: #888; font-size: 11px;")
        legend.addWidget(lbl_info)
        lay_frame.addLayout(legend)
        
        btn_close = QPushButton("Cerrar")
        btn_close.clicked.connect(self.accept)
        lay_frame.addWidget(btn_close)
        
        layout.addWidget(frame)