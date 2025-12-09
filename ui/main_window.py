import sys
import json
import os
from pathlib import Path
from datetime import datetime

from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QCheckBox,
    QScrollArea, QFrame, QDialog, QSystemTrayIcon, QMenu, QListWidget
)
from PySide6.QtCore import QTimer, QTime, QDate, Qt, QPoint, QDateTime, QUrl
from PySide6.QtGui import QIcon, QAction
from PySide6.QtMultimedia import QSoundEffect

# --- IMPORTACIONES PROPIAS (NUESTRA ESTRUCTURA) ---
from database import mongo_db as db
from utils.helpers import resource_path
from ui.styles import ESTILO_MAIN_WINDOW, ESTILO_TOOLTIP
from ui.notifications import AlarmNotification, ToastNotification
from ui.dialogs import LoginDialog, ConfigDialog, TaskDialog, CustomMessageBox, CalendarDialog 
from database import local_storage  
from datetime import datetime

class ProductivityWidget(QWidget):
    def __init__(self):
        super().__init__()

        # Configuración inicial
        self.usuario_actual = None
        self.tareas_pendientes = []
        self.pending_alarms = []
        self.intervalo_revision = 30
        self.is_expanded = False
        self.drag_pos = QPoint()
        self.setStyleSheet(ESTILO_MAIN_WINDOW + ESTILO_TOOLTIP)
        # Ventana
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setFixedSize(280, 140)
        
        # Aplicar estilo unificado
        self.setStyleSheet(ESTILO_MAIN_WINDOW)

        # Configurar Rutas y Archivos
        self.setup_files_and_folders()
        
        # Configurar UI
        self.setup_ui()
        
        # Configurar Bandeja de Sistema (Tray Icon)
        self.setup_tray_icon()
        
        # Configurar Sonidos
        self.setup_audio()

        # Timers
        self.timer_reloj = QTimer(self)
        self.timer_reloj.timeout.connect(self.update_datetime)
        self.timer_reloj.start(1000)
        self.update_datetime()

        self.alarm_timer = QTimer(self)
        self.alarm_timer.timeout.connect(self.check_alarms)
        self.alarm_timer.start(1000)

        # Cargar datos iniciales
        self.load_history()
        self.load_alarms()

    def setup_files_and_folders(self):
        # Carpetas locales (Documentos)
        documents_dir = Path.home() / "Documents" / "ProductivityApp"
        documents_dir.mkdir(parents=True, exist_ok=True)
        self.history_file = documents_dir / "historial.json"
        self.alarms_file = documents_dir / "alarms.json"
        # El archivo de tareas se define al loguearse el usuario

    def setup_audio(self):
        self.new_task_sound = QSoundEffect()
        # Buscamos en la carpeta assets
        sound_path = resource_path("assets/alerta.wav")
        if not os.path.exists(sound_path):
             sound_path = resource_path("alerta.wav") # Fallback raiz
        
        if os.path.exists(sound_path):
            self.new_task_sound.setSource(QUrl.fromLocalFile(sound_path))
            self.new_task_sound.setVolume(0.8)

    def setup_tray_icon(self):
        icon_path = resource_path("assets/Reloj.ico")
        if not os.path.exists(icon_path): icon_path = resource_path("Reloj.ico")
        
        self.tray_icon = QSystemTrayIcon(QIcon(icon_path), self)
        self.tray_icon.setToolTip("ADTL Productivity App")
        
        tray_menu = QMenu()
        show_action = QAction("Abrir/Mostrar", self)
        show_action.triggered.connect(self.show_normal)
        tray_menu.addAction(show_action)
        tray_menu.addSeparator()
        exit_action = QAction("Salir y Cerrar Sesión", self)
        exit_action.triggered.connect(self.close_application)
        tray_menu.addAction(exit_action)
        
        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.show()
        self.tray_icon.activated.connect(self.on_tray_activated)

    def setup_ui(self):
        
        # Frame Principal
        self.background_frame = QFrame()
        self.background_frame.setObjectName("main_background")
        layout = QVBoxLayout(self.background_frame)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(8)

        # Header (Botones y Usuario)
        header = QHBoxLayout()
        self.config_button = QPushButton("⚙️")
        self.config_button.clicked.connect(self.mostrar_configuracion)
        self.config_button.setVisible(False)
        
        self.user_label = QLabel()
        self.user_label.setObjectName("user_label")
        self.user_label.setVisible(False)
        
        self.logout_button = QPushButton("🚪")
        self.logout_button.clicked.connect(self.cerrar_sesion)
        self.logout_button.setVisible(False)

        header.addWidget(self.config_button)
        header.addStretch()
        header.addWidget(self.user_label)
        header.addStretch()
        header.addWidget(self.logout_button)
        layout.addLayout(header)

        # Reloj
        self.date_label = QLabel()
        self.date_label.setObjectName("date_label")
        self.date_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.date_label)

        self.time_label = QLabel()
        self.time_label.setObjectName("time_label")
        self.time_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.time_label)

        # Lista de Tareas (Container)
        self.checklist_container = QWidget()
        self.checklist_layout = QVBoxLayout(self.checklist_container)
        self.checklist_layout.setContentsMargins(0, 5, 0, 0) # Un poco de margen arriba
        
        # Input Tareas Rápidas
        input_layout = QHBoxLayout()
        self.task_input = QLineEdit()
        self.task_input.setPlaceholderText("Nueva tarea...")
        self.task_input.returnPressed.connect(self.add_quick_task)
        
        btn_add = QPushButton("+")
        btn_add.setObjectName("btn_accion")
        btn_add.clicked.connect(self.add_quick_task)
        
        btn_detail = QPushButton("⋯")
        btn_detail.setObjectName("btn_accion")
        btn_detail.clicked.connect(self.show_task_dialog)
        
        input_layout.addWidget(self.task_input)
        input_layout.addWidget(btn_add)
        input_layout.addWidget(btn_detail)
        self.checklist_layout.addLayout(input_layout)

        # Scroll Area Tareas
        self.scroll_area = QScrollArea()
        self.scroll_widget = QWidget()
        self.scroll_widget.setObjectName("scroll_widget")
        self.task_list_layout = QVBoxLayout(self.scroll_widget)
        self.task_list_layout.setAlignment(Qt.AlignTop)
        self.scroll_area.setWidget(self.scroll_widget)
        self.scroll_area.setWidgetResizable(True)
        self.checklist_layout.addWidget(self.scroll_area)
        
        self.checklist_container.setVisible(False)
        layout.addWidget(self.checklist_container)

        botones_layout = QHBoxLayout()
        
        self.btn_calendar = QPushButton("📅 Calendario")
        self.btn_calendar.setCursor(Qt.PointingHandCursor)
        self.btn_calendar.clicked.connect(self.abrir_calendario)
        botones_layout.addWidget(self.btn_calendar)

        self.history_toggle = QPushButton("📜 Historial")
        self.history_toggle.setObjectName("history_button")
        self.history_toggle.setCheckable(True)
        self.history_toggle.setCursor(Qt.PointingHandCursor)
        self.history_toggle.clicked.connect(self.toggle_history)
        botones_layout.addWidget(self.history_toggle)

        self.checklist_layout.addLayout(botones_layout)
        # -----------------------------------------------------------

        # Agregamos el contenedor completo al layout principal y lo ocultamos de inicio
        self.checklist_container.setVisible(False)
        layout.addWidget(self.checklist_container)

        # --- ZONA HISTORIAL (Se muestra debajo de todo) ---
        self.history_container = QWidget()
        self.history_layout = QVBoxLayout(self.history_container)
        self.hist_scroll = QScrollArea()
        self.hist_widget = QWidget()
        self.hist_widget.setObjectName("history_scroll_widget")
        self.history_list_layout = QVBoxLayout(self.hist_widget)
        self.history_list_layout.setAlignment(Qt.AlignTop)
        self.hist_scroll.setWidget(self.hist_widget)
        self.hist_scroll.setWidgetResizable(True)
        self.history_layout.addWidget(self.hist_scroll)
        
        self.history_container.setVisible(False)
        layout.addWidget(self.history_container)

        # Layout Principal final
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(self.background_frame)

    # --- LOGICA DEL RELOJ Y UI ---
    def update_datetime(self):
        now = QDateTime.currentDateTime()
        self.date_label.setText(now.toString("dddd, d 'de' MMMM").capitalize())
        self.time_label.setText(now.toString("hh:mm:ss"))

    def toggle_history(self, checked):
        self.history_container.setVisible(checked)
        self.history_toggle.setText("Historial )…" if checked else "Historial (...")
        if checked:
            self.setFixedSize(320, 550)
            self.load_history()
        else:
            self.setFixedSize(320, 400) if self.is_expanded else self.setFixedSize(260, 120)
    def abrir_calendario(self):
        # Le pasamos las tareas pendientes y las alarmas para que pinte los puntos
        dlg = CalendarDialog(self, tareas=self.tareas_pendientes, alarmas=self.pending_alarms)
        dlg.exec()            

    # --- LOGICA DE USUARIO ---
    def actualizar_interfaz_usuario(self):
        if self.usuario_actual:
            self.user_label.setText(f"{self.usuario_actual['nom_usuario']} (ID: {self.usuario_actual['id_usuario']})")
            self.user_label.setVisible(True)
            self.config_button.setVisible(True)
            self.logout_button.setVisible(True)
            self.archivo_tareas = Path.home() / "Documents" / "ProductivityApp" / f"tareas_usuario_{self.usuario_actual['id_usuario']}.json"

    def cerrar_sesion(self):
        self.detener_revision_automatica()
        self.guardar_tareas_locales()
        self.save_alarms()
        
        self.hide()
        self.usuario_actual = None
        self.tareas_pendientes = []
        
        # Volver al login
        login = LoginDialog()
        if login.exec() == QDialog.Accepted:
            self.usuario_actual = login.usuario_actual
            self.actualizar_interfaz_usuario()
            self.cargar_tareas_locales()
            self.iniciar_revision_automatica()
            self.show()
        else:
            self.close_application()

    # --- LOGICA DE BASE DE DATOS (TAREAS) ---
    def iniciar_revision_automatica(self):
        self.revision_timer = QTimer(self)
        self.revision_timer.timeout.connect(self.actualizar_tareas_db)
        self.revision_timer.start(self.intervalo_revision * 1000)
        QTimer.singleShot(1000, self.actualizar_tareas_db)

    def detener_revision_automatica(self):
        if hasattr(self, 'revision_timer'):
            self.revision_timer.stop()

    def actualizar_tareas_db(self):
        if not self.usuario_actual: return
        
        tareas_bd = db.obtener_tareas_pendientes(self.usuario_actual["id_usuario"])
        
        nuevas_detectadas = False
        lista_final = []
        ids_actuales = {t['id_tarea'] for t in self.tareas_pendientes if t.get('from_db')}
        
        for tarea in tareas_bd:
            tiene_alarma = False
            fecha_alarma = tarea.get("reminder_time")
            
            if fecha_alarma: tiene_alarma = True
            
            t_data = {
                "id_tarea": tarea["id_tarea"],
                "text": tarea["desc_tareas"],
                "color": self._obtener_color_tarea(tarea["tp_tarea"]),
                "from_db": True,
                "has_reminder": tiene_alarma,
                "reminder_time": fecha_alarma,
                "status": "active" if tiene_alarma else None
            }
            
            lista_final.append(t_data)
            
            # SI ES NUEVA TAREA
            if tarea["id_tarea"] not in ids_actuales:
                # 1. MOSTRAR NOTIFICACIÓN VISUAL (TOAST)
                self.show_toast_notification(t_data)
                nuevas_detectadas = True
                
                # 2. SI ES ALARMA, REGISTRARLA
                if tiene_alarma:
                    ya_existe = any(a.get("text") == t_data["text"] and a.get("reminder_time") == fecha_alarma for a in self.pending_alarms)
                    if not ya_existe:
                        alarm_copy = t_data.copy()
                        alarm_copy["id_local"] = f"global_{tarea['id_tarea']}"
                        self.pending_alarms.append(alarm_copy)
                        self.save_alarms()
        
        # 3. SONIDO
        if nuevas_detectadas and hasattr(self, 'new_task_sound'):
            self.new_task_sound.play()

        locales = [t for t in self.tareas_pendientes if not t.get('from_db')]
        self.tareas_pendientes = locales + lista_final
        self.guardar_tareas_locales()
        self.actualizar_interfaz_tareas() 
    def completar_tarea_db(self, container, task_data):
        # Intentar actualizar en BD
        exito = db.actualizar_estado_tarea(task_data["id_tarea"], "Finalizada")
        
        if exito:
            self.tareas_pendientes = [t for t in self.tareas_pendientes if t.get('id_tarea') != task_data['id_tarea']]
            self.guardar_tareas_locales()
            
            # Borrado seguro visual
            self.task_list_layout.removeWidget(container)
            container.setParent(None)
            container.deleteLater()
            
            CustomMessageBox(self, "Tarea completada y sincronizada", "success").exec()
        else:
            CustomMessageBox(self, "Error al sincronizar con BD", "error").exec()


    def _obtener_color_tarea(self, tipo):
        tipo = str(tipo).lower()
        if any(x in tipo for x in ["rojo", "importante", "alta"]): return "red"
        if any(x in tipo for x in ["amarillo", "medio"]): return "yellow"
        if any(x in tipo for x in ["azul", "info"]): return "blue"
        return "green"

    # --- GESTION VISUAL DE TAREAS ---
    def actualizar_interfaz_tareas(self):
        # Limpiar lista visual
        while self.task_list_layout.count():
            item = self.task_list_layout.takeAt(0)
            if item.widget(): item.widget().deleteLater()

        # Renderizar tareas
        for tarea in self.tareas_pendientes:
            self.crear_widget_tarea(tarea)

    def eliminar_tarea(self, widget_contenedor, data):
        msg = CustomMessageBox(self, "¿Eliminar definitivamente?", "question")
        if msg.exec() != QDialog.Accepted:
            return

        try:
            # 1. Eliminar de la memoria
            if data.get("from_db"):
                # Lógica BD (Opcional: Marcar como cancelada en BD)
                # db.actualizar_estado_tarea(data["id_tarea"], "Cancelada") 
                self.tareas_pendientes = [t for t in self.tareas_pendientes if t.get('id_tarea') != data.get('id_tarea')]
            else:
                # Lógica Local
                self.tareas_pendientes = [t for t in self.tareas_pendientes if t.get('id_local') != data.get('id_local')]
                
                # Borrar alarma asociada si existe
                if data.get("has_reminder"):
                    self.pending_alarms = [a for a in self.pending_alarms if a.get('id_local') != data.get('id_local')]
                    self.save_alarms()

            # 2. Guardar cambios
            self.guardar_tareas_locales()
            
            # 3. BORRADO SEGURO
            self.task_list_layout.removeWidget(widget_contenedor)
            widget_contenedor.setParent(None) # <--- ESTO EVITA EL ERROR C++
            widget_contenedor.deleteLater()
            
            self.tray_icon.showMessage("Reloj", "Tarea eliminada", QSystemTrayIcon.NoIcon, 1000)

        except Exception as e:
            print(f"❌ Error eliminando tarea: {e}")


    def crear_widget_tarea(self, data):
        txt_corto = (data["text"][:22] + "...") if len(data["text"]) > 22 else data["text"]
        color = data.get('color', 'green')
        
        container = QWidget()
        lay = QHBoxLayout(container)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(5)
        
        # --- TAREAS DE MONGO (JEFE) ---
        if data.get("from_db"):
            icono = "⏰ " if data.get("has_reminder") else ""
            
            lbl = QLabel(f"{icono}{txt_corto}")
            lbl.setProperty("class", "task_db")
            lbl.setObjectName(f"task_db_{color}")
            lbl.setToolTip(f"📝 Asignación:\n{data['text']}")
            
            # Botón COMPLETAR (El check verde)
            btn_check = QPushButton("✓")
            btn_check.setFixedSize(24, 24)
            btn_check.setStyleSheet("background:#28a745; border-radius:4px; border:none; color:white; font-weight:bold;")
            btn_check.setCursor(Qt.PointingHandCursor)
            btn_check.clicked.connect(lambda: self.completar_tarea_db(container, data))
            
            lay.addWidget(lbl)
            lay.addWidget(btn_check)
            
            # 🛑 AQUÍ ESTÁ EL CAMBIO: NO AGREGAMOS EL BOTÓN DE BASURA
            # Así el empleado no puede borrarla por error.

        # --- ALARMAS LOCALES (USUARIO) ---
        elif data.get("has_reminder"):
            lbl = QLabel(f"⏰ {txt_corto}")
            lbl.setProperty("class", f"alert_{color}")
            lbl.setToolTip(f"Tu Alarma:\n{data['text']}")
            lay.addWidget(lbl)
            
            # Aquí SÍ permitimos borrar (por si se equivocó de hora)
            self._agregar_boton_borrar(lay, container, data)

        # --- NOTAS LOCALES (USUARIO) ---
        else:
            chk = QCheckBox(txt_corto)
            chk.setProperty("class", f"task_{color}")
            chk.setToolTip(f"Tu Nota:\n{data['text']}")
            chk.toggled.connect(lambda c: self.completar_tarea_local(container, chk, c, data))
            lay.addWidget(chk)
            
            # Aquí SÍ permitimos borrar (por si escribió mal)
            self._agregar_boton_borrar(lay, container, data)

        self.task_list_layout.addWidget(container)

    def _agregar_boton_borrar(self, layout, container, data):
        """Helper para agregar el botón de borrar solo cuando corresponde"""
        btn_del = QPushButton("🗑️")
        btn_del.setFixedSize(24, 24)
        btn_del.setObjectName("btn_eliminar")
        btn_del.setToolTip("Eliminar")
        btn_del.setCursor(Qt.PointingHandCursor)
        btn_del.clicked.connect(lambda: self.eliminar_tarea(container, data))
        layout.addWidget(btn_del)

    def completar_tarea_local(self, container, chk, checked, data):
        if checked:
            if CustomMessageBox(self, "¿Terminaste esta tarea?", "question").exec() == QDialog.Accepted:
                try:
                    # 1. Remover de datos
                    if data in self.tareas_pendientes:
                        self.tareas_pendientes.remove(data)
                    
                    # 2. Guardar
                    self.guardar_tareas_locales()
                    self.save_to_history(data)
                    
                    # 3. BORRADO SEGURO (El truco mágico)
                    # Primero lo sacamos del layout
                    self.task_list_layout.removeWidget(container)
                    # Luego lo desconectamos visualmente
                    container.setParent(None)
                    # Finalmente lo destruimos
                    container.deleteLater()
                    
                except Exception as e:
                    print(f"Error completando tarea: {e}")
            else:
                chk.blockSignals(True)
                chk.setChecked(False)
                chk.blockSignals(False)

    # --- ALARMAS Y NOTIFICACIONES ---
    def show_toast_notification(self, task_data):
        """Muestra una notificación flotante agresiva que asegura visibilidad"""
        try:
            # 1. Guardamos la referencia en self para que no se borre
            self.current_toast = ToastNotification(task_data, None, self)
            
            # 2. Configuración agresiva de ventana (Siempre encima, sin foco, tool)
            self.current_toast.setWindowFlags(
                Qt.FramelessWindowHint | 
                Qt.WindowStaysOnTopHint | 
                Qt.Tool | 
                Qt.X11BypassWindowManagerHint
            )
            
            # 3. Mostrar y levantar
            self.current_toast.show()
            self.current_toast.raise_()
            self.current_toast.activateWindow()
            
            # 4. Refuerzo: Volver a levantarla 100ms después por si Windows la tapó
            QTimer.singleShot(100, self.current_toast.raise_)
            QTimer.singleShot(100, self.current_toast.activateWindow)
            
            print(f"🔔 Notificación visual enviada para: {task_data.get('text', 'tarea')}")
            
        except Exception as e:
            print(f"❌ Error mostrando toast: {e}")

    def check_alarms(self):
        now = QDateTime.currentDateTime()
        for alarm in self.pending_alarms[:]:
            t = QDateTime.fromString(alarm["reminder_time"], Qt.ISODate)
            if t.isValid() and now >= t and alarm.get("status") == "active":
                AlarmNotification(alarm, self).show()
                alarm["status"] = "notified" # Evitar repetir
                self.save_alarms()

    def save_snoozed_alarm(self, data):
        self.pending_alarms.append(data)
        self.save_alarms()
    
    def complete_alarm_task(self, data):
        # Elimina si existe en tareas pendientes locales
        self.tareas_pendientes = [t for t in self.tareas_pendientes if t.get('id_local') != data.get('id_local')]
        self.guardar_tareas_locales()
        self.actualizar_interfaz_tareas()

    # --- EVENTOS VENTANA ---
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.drag_pos = event.globalPosition().toPoint() - self.pos()
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton:
            self.move(event.globalPosition().toPoint() - self.drag_pos)
            event.accept()
    
    def mouseDoubleClickEvent(self, event):
        """
        Al hacer doble clic en CUALQUIER PARTE del fondo, 
        se alterna entre expandir y contraer.
        """
        # Invertir el estado
        self.is_expanded = not self.is_expanded
        
        # Mostrar u ocultar los paneles
        self.checklist_container.setVisible(self.is_expanded)
        self.history_toggle.setVisible(self.is_expanded)
        
        # Calcular nueva altura
        # Si está expandido: 420px, si no: 140px (un poco más alto para el nuevo diseño)
        nueva_altura = 420 if self.is_expanded else 140
        ancho = 320 if self.is_expanded else 280
        
        self.setFixedSize(ancho, nueva_altura)
        
        # Si cerramos, asegurarnos de ocultar el historial también
        if not self.is_expanded:
            self.history_container.setVisible(False)
            self.history_toggle.setChecked(False)
            self.history_toggle.setText("Historial (...")
            
        event.accept()
    def closeEvent(self, event):
        event.ignore()
        self.hide()
        self.tray_icon.showMessage("Reloj Productivo", "La aplicación sigue en segundo plano.", QSystemTrayIcon.Information, 2000)

    def show_normal(self):
        self.show()
        self.activateWindow()

    def close_application(self):
        self.detener_revision_automatica()
        QApplication.quit()
        
    def on_tray_activated(self, reason):
        if reason == QSystemTrayIcon.DoubleClick:
            self.show_normal()
            
    # --- FUNCIONES AUXILIARES DE ALMACENAMIENTO ---
    # (Mantener lógica simple de JSON aquí por ahora)
    def add_quick_task(self):
        txt = self.task_input.text().strip()
        if txt:
            data = {"text": txt, "color": "green", "from_db": False, "id_local": str(datetime.now().timestamp())}
            self.tareas_pendientes.append(data)
            self.guardar_tareas_locales()
            self.crear_widget_tarea(data)
            self.task_input.clear()
            
    def show_task_dialog(self):
        dlg = TaskDialog(self, self.task_input.text())
        if dlg.exec():
            data = dlg.get_task_data()
            data["from_db"] = False
            data["id_local"] = str(datetime.now().timestamp())
            
            if data["has_reminder"] and data["reminder_time"]:
                # 1. Guardamos la fecha como TEXTO en el objeto principal
                fecha_texto = data["reminder_time"].toString(Qt.ISODate)
                data["reminder_time"] = fecha_texto
                
                # 2. Programar alarma (usando el texto ya convertido)
                alarm_data = data.copy()
                alarm_data["reminder_time"] = fecha_texto
                alarm_data["status"] = "active"
                
                self.pending_alarms.append(alarm_data)
                self.save_alarms()
                
            self.tareas_pendientes.append(data)
            self.guardar_tareas_locales()
            self.actualizar_interfaz_tareas()

    def mostrar_configuracion(self):
        dlg = ConfigDialog(self.intervalo_revision, self)
        if dlg.exec():
            self.intervalo_revision = dlg.intervalo
            self.iniciar_revision_automatica()

    def guardar_tareas_locales(self):
        if not self.usuario_actual: return
        with open(self.archivo_tareas, 'w', encoding='utf-8') as f:
            json.dump({"usuario": self.usuario_actual["id_usuario"], "tareas": self.tareas_pendientes}, f)

    def cargar_tareas_locales(self):
        if self.archivo_tareas.exists():
            try:
                with open(self.archivo_tareas, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if data.get("usuario") == self.usuario_actual["id_usuario"]:
                        self.tareas_pendientes = data.get("tareas", [])
                        self.actualizar_interfaz_tareas()
            except: pass

    def load_alarms(self):
        if self.alarms_file.exists():
            try:
                with open(self.alarms_file, 'r') as f: self.pending_alarms = json.load(f)
            except: pass

    def save_alarms(self):
        with open(self.alarms_file, 'w') as f: json.dump(self.pending_alarms, f)

    def load_history(self):
        # Limpiar
        while self.history_list_layout.count():
            item = self.history_list_layout.takeAt(0)
            if item.widget(): item.widget().deleteLater()
            
        if self.history_file.exists():
            try:
                with open(self.history_file, 'r') as f: data = json.load(f)
                for date, tasks in data.items():
                    self.history_list_layout.addWidget(QLabel(f"📅 {date}", styleSheet="color:#66CCFF; font-weight:bold;"))
                    for t in tasks:
                        txt = t if isinstance(t, str) else t.get("text","")
                        self.history_list_layout.addWidget(QLabel(f" • {txt}", styleSheet="color:#888; font-size:12px;"))
            except: pass

    def save_to_history(self, task_data):
        date_str = QDate.currentDate().toString("yyyy-MM-dd")
        data = {}
        if self.history_file.exists():
            try:
                with open(self.history_file, 'r') as f: data = json.load(f)
            except: pass
        
        if date_str not in data: data[date_str] = []
        data[date_str].append(task_data)
        
        with open(self.history_file, 'w') as f: json.dump(data, f)

    # --- FUNCIONES AUXILIARES DE ALMACENAMIENTO (MODULAR) ---
    # Reemplaza las funciones del final por estas:

    def guardar_tareas_locales(self):
        if self.usuario_actual:
            local_storage.guardar_tareas(self.usuario_actual["id_usuario"], self.tareas_pendientes)

    def cargar_tareas_locales(self):
        if self.usuario_actual:
            tareas = local_storage.cargar_tareas(self.usuario_actual["id_usuario"])
            if tareas:
                self.tareas_pendientes = tareas
                self.actualizar_interfaz_tareas()

    def load_alarms(self):
        self.pending_alarms = local_storage.cargar_alarmas()

    def save_alarms(self):
        local_storage.guardar_alarmas(self.pending_alarms)

    def load_history(self):
        # Limpiar widget
        while self.history_list_layout.count():
            item = self.history_list_layout.takeAt(0)
            if item.widget(): item.widget().deleteLater()
            
        data = local_storage.cargar_historial_completo()
        # Ordenar fechas descendente
        for date in sorted(data.keys(), reverse=True):
            tasks = data[date]
            self.history_list_layout.addWidget(QLabel(f"📅 {date}", styleSheet="color:#66CCFF; font-weight:bold;"))
            for t in tasks:
                txt = t if isinstance(t, str) else t.get("text","")
                self.history_list_layout.addWidget(QLabel(f" • {txt}", styleSheet="color:#888; font-size:12px;"))

    def save_to_history(self, task_data):
        local_storage.guardar_historial(task_data)

