from datetime import datetime
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                               QPushButton, QTableWidget, QTableWidgetItem, 
                               QHeaderView, QFrame, QLineEdit, QComboBox, 
                               QMessageBox, QTabWidget, QDialog, QCalendarWidget, 
                               QTableView, QToolTip, QTextEdit, QCheckBox, QDateTimeEdit)
from PySide6.QtCore import Qt, QTimer, QEvent, QPoint, QDate
from PySide6.QtGui import QColor, QPainter, QBrush, QPen, QCursor

from database import mongo_db as db
from admin.styles import ESTILO_WIDGETS_ADMIN, ESTILO_TABS

# ==========================================
# 1. CALENDARIO DASHBOARD
# ==========================================
class AdminCalendar(QCalendarWidget):
    def __init__(self, parent=None, tareas_map=None):
        super().__init__(parent)
        self.tareas_map = tareas_map if tareas_map else {}
        self.setGridVisible(False)
        self.setVerticalHeaderFormat(QCalendarWidget.NoVerticalHeader)
        self.setStyleSheet("""
            QCalendarWidget QWidget#qt_calendar_navigationbar { background-color: #1a1c20; }
            QToolButton { color: #00f0ff; background: transparent; icon-size: 24px; }
            QTableView { background-color: #0f1012; selection-background-color: rgba(0, 240, 255, 0.2); color: white; }
        """)
        self.celdas_pintadas = {}
        self.setMouseTracking(True)
        tabla = self.findChild(QTableView)
        if tabla:
            tabla.setMouseTracking(True)
            tabla.viewport().installEventFilter(self)

    def paintCell(self, painter, rect, date):
        super().paintCell(painter, rect, date)
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
                c = QColor("#00ff00")
                tipo = item.get("tipo", "")
                if "Rojo" in tipo: c = QColor("#ff4444")
                elif "Amarillo" in tipo: c = QColor("#ffff44")
                elif "Azul" in tipo: c = QColor("#00f0ff")
                painter.setBrush(QBrush(c))
                painter.setPen(Qt.NoPen)
                painter.drawEllipse(QPoint(int(start_x + (i * spacing)), int(y_pos)), radius, radius)
            painter.restore()

    def obtener_fecha_en_pos(self, pos):
        for date_str, rect in self.celdas_pintadas.items():
            if rect.contains(pos):
                return QDate.fromString(date_str, "yyyy-MM-dd")
        return QDate()

    def eventFilter(self, source, event):
        if event.type() == QEvent.MouseMove and source == self.findChild(QTableView).viewport():
            date = self.obtener_fecha_en_pos(event.pos())
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
            html = f"<div style='background-color:#0f1012; color:white; padding:5px; font-family:Segoe UI;'><b style='color:#00f0ff'>{date.toString('dd/MM/yyyy')}</b><hr style='background-color:#444; margin:2px 0;'>"
            for item in items[:6]: 
                html += f"<div style='margin-bottom:2px;'>• <b style='color:#ccc'>{item['empleado']}:</b> {item['desc']}</div>"
            if len(items) > 6: html += f"<i style='color:#888'>...y {len(items)-6} más</i>"
            html += "</div>"
            QToolTip.showText(global_pos, html, self)
        else:
            QToolTip.hideText()

# ==========================================
# 2. VISTAS PRINCIPALES
# ==========================================

class DashboardView(QWidget):
    def __init__(self):
        super().__init__()
        self.setup_ui()
        
        # --- AUTO ACTUALIZACIÓN DASHBOARD (10s) ---
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.cargar_datos)
        self.timer.start(10000) 

    def setup_ui(self):
        layout = QVBoxLayout(self)
        top = QHBoxLayout()
        lbl = QLabel("📊 Resumen General")
        lbl.setStyleSheet("font-size: 24px; font-weight: bold; color: #00f0ff;")
        top.addWidget(lbl)
        top.addStretch()
        btn_refresh = QPushButton("🔄")
        btn_refresh.setObjectName("btn_accion")
        btn_refresh.clicked.connect(self.cargar_datos)
        top.addWidget(btn_refresh)
        layout.addLayout(top)
        self.cards_layout = QHBoxLayout()
        layout.addLayout(self.cards_layout)
        layout.addWidget(QLabel("📅 Calendario de Entregas (Todas las Tareas)", styleSheet="color:#888; margin-top:10px; font-size:14px;"))
        self.calendar_container = QVBoxLayout()
        layout.addLayout(self.calendar_container)
        layout.addStretch()
        self.cargar_datos()

    def cargar_datos(self):
        self.limpiar_layout(self.cards_layout)
        self.limpiar_layout(self.calendar_container)
        n_users = db.usuarios.count_documents({"tp_usuario": "empleado"})
        n_pend = db.tareas.count_documents({"Us_estado": "Pendiente"})
        n_done = db.tareas.count_documents({"Us_estado": "Finalizada"})
        self.cards_layout.addWidget(self.crear_tarjeta("👥 Empleados", str(n_users), "#00f0ff"))
        self.cards_layout.addWidget(self.crear_tarjeta("⏳ Pendientes", str(n_pend), "#ff4444"))
        self.cards_layout.addWidget(self.crear_tarjeta("✅ Finalizadas", str(n_done), "#00ff00"))
        
        tareas_map = {}
        cursor = db.tareas.find({"Us_estado": "Pendiente"})
        users_map = {u['id_usuario']: u['nom_usuario'] for u in db.usuarios.find()}
        for t in cursor:
            fecha_iso = t.get("fecha_creacion")
            if fecha_iso:
                try:
                    if "T" in str(fecha_iso): f_str = str(fecha_iso).split("T")[0]
                    else: f_str = str(fecha_iso).split(" ")[0]
                    if f_str not in tareas_map: tareas_map[f_str] = []
                    uid = t.get("Us_tarea")
                    try: uid = int(uid)
                    except: pass
                    nombre_emp = users_map.get(uid, f"ID {uid}")
                    tareas_map[f_str].append({
                        "tipo": t.get("tp_tarea"),
                        "desc": t.get("desc_tareas", "")[:25] + "...",
                        "empleado": nombre_emp.split(" ")[0]
                    })
                except: pass
        cal = AdminCalendar(self, tareas_map)
        self.calendar_container.addWidget(cal)

    def crear_tarjeta(self, titulo, valor, color):
        f = QFrame()
        f.setStyleSheet(f"background: #1a1c20; border: 1px solid {color}; border-radius: 8px;")
        f.setFixedSize(200, 100)
        l = QVBoxLayout(f)
        l.addWidget(QLabel(titulo, styleSheet="color:#ccc; font-size:12px;"))
        l.addWidget(QLabel(valor, styleSheet=f"color:{color}; font-size:28px; font-weight:bold;"))
        return f

    def limpiar_layout(self, layout):
        while layout.count():
            item = layout.takeAt(0)
            if item.widget(): item.widget().deleteLater()

class UsuariosView(QWidget):
    def __init__(self):
        super().__init__()
        self.setStyleSheet(ESTILO_WIDGETS_ADMIN)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        top_bar = QHBoxLayout()
        top_bar.addWidget(QLabel("👥 Gestión de Usuarios", styleSheet="font-size:18px; font-weight:bold; color:white;"))
        top_bar.addStretch()
        self.combo_filtro = QComboBox()
        self.combo_filtro.addItems(["Todos", "Nombre", "ID", "Tipo"])
        self.combo_filtro.setFixedWidth(120)
        self.input_buscar = QLineEdit()
        self.input_buscar.setPlaceholderText("Buscar...")
        self.input_buscar.returnPressed.connect(self.cargar_tabla)
        btn_buscar = QPushButton("🔍")
        btn_buscar.setObjectName("btn_accion")
        btn_buscar.clicked.connect(self.cargar_tabla)
        top_bar.addWidget(self.combo_filtro)
        top_bar.addWidget(self.input_buscar)
        top_bar.addWidget(btn_buscar)
        layout.addLayout(top_bar)

        form = QHBoxLayout()
        self.new_name = QLineEdit()
        self.new_name.setPlaceholderText("Nombre nuevo empleado...")
        self.new_role = QComboBox()
        self.new_role.addItems(["empleado", "admin"])
        btn_add = QPushButton("➕ Crear")
        btn_add.setObjectName("btn_accion")
        btn_add.clicked.connect(self.crear_usuario)
        form.addWidget(self.new_name)
        form.addWidget(self.new_role)
        form.addWidget(btn_add)
        layout.addLayout(form)

        self.tabla = QTableWidget()
        self.tabla.setColumnCount(5)
        self.tabla.setHorizontalHeaderLabels(["ID", "Nombre", "Rol", "Editar", "Borrar"])
        self.tabla.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.tabla.verticalHeader().setVisible(False)
        layout.addWidget(self.tabla)
        self.cargar_tabla()

    def cargar_tabla(self):
        self.tabla.setRowCount(0)
        filtro = self.combo_filtro.currentText()
        valor = self.input_buscar.text().strip()
        query = {}
        if valor:
            if filtro == "ID" and valor.isdigit(): query = {"id_usuario": int(valor)}
            elif filtro == "Nombre": query = {"nom_usuario": {"$regex": valor, "$options": "i"}}
            elif filtro == "Tipo": query = {"tp_usuario": {"$regex": valor, "$options": "i"}}
        users = db.usuarios.find(query).sort("id_usuario", 1)
        for u in users:
            row = self.tabla.rowCount()
            self.tabla.insertRow(row)
            self.tabla.setItem(row, 0, QTableWidgetItem(str(u["id_usuario"])))
            self.tabla.setItem(row, 1, QTableWidgetItem(u["nom_usuario"]))
            self.tabla.setItem(row, 2, QTableWidgetItem(u["tp_usuario"]))
            btn_edit = QPushButton("✏️")
            btn_edit.setStyleSheet("color:#ffff44; background:transparent; border:none;")
            btn_edit.setCursor(Qt.PointingHandCursor)
            btn_edit.clicked.connect(lambda _, x=u: self.abrir_editor(x))
            self.tabla.setCellWidget(row, 3, btn_edit)
            btn_del = QPushButton("🗑️")
            btn_del.setStyleSheet("color:#ff4444; background:transparent; border:none;")
            btn_del.setCursor(Qt.PointingHandCursor)
            btn_del.clicked.connect(lambda _, id=u["id_usuario"]: self.borrar_usuario(id))
            self.tabla.setCellWidget(row, 4, btn_del)

    def crear_usuario(self):
        nom = self.new_name.text().strip()
        rol = self.new_role.currentText()
        if nom:
            db.insertar_usuario(nom, rol)
            self.new_name.clear()
            self.cargar_tabla()
            QMessageBox.information(self, "Éxito", "Usuario creado")

    def borrar_usuario(self, uid):
        if QMessageBox.question(self, "Confirmar", "¿Eliminar usuario?") == QMessageBox.Yes:
            db.usuarios.delete_one({"id_usuario": uid})
            self.cargar_tabla()

    def abrir_editor(self, user_data):
        dlg = EditarUsuarioDialog(self, user_data)
        if dlg.exec():
            self.cargar_tabla()

class EditarUsuarioDialog(QDialog):
    def __init__(self, parent, data):
        super().__init__(parent)
        self.setWindowTitle(f"Editar ID: {data['id_usuario']}")
        self.data = data
        self.setFixedSize(300, 200)
        self.setStyleSheet("background:#15171a; color:white;")
        l = QVBoxLayout(self)
        l.addWidget(QLabel("Nombre:"))
        self.inp_name = QLineEdit(data['nom_usuario'])
        self.inp_name.setStyleSheet("background:#0f1012; border:1px solid #333; color:white; padding:5px;")
        l.addWidget(self.inp_name)
        l.addWidget(QLabel("Rol:"))
        self.inp_role = QComboBox()
        self.inp_role.addItems(["empleado", "admin"])
        self.inp_role.setCurrentText(data['tp_usuario'])
        self.inp_role.setStyleSheet("background:#0f1012; color:white; padding:5px;")
        l.addWidget(self.inp_role)
        btn_save = QPushButton("Guardar Cambios")
        btn_save.setStyleSheet("background:#00f0ff; color:black; font-weight:bold; padding:8px; border-radius:4px;")
        btn_save.clicked.connect(self.guardar)
        l.addWidget(btn_save)

    def guardar(self):
        new_name = self.inp_name.text().strip()
        new_role = self.inp_role.currentText()
        if new_name:
            db.usuarios.update_one(
                {"id_usuario": self.data["id_usuario"]},
                {"$set": {"nom_usuario": new_name, "tp_usuario": new_role}}
            )
            self.accept()

# ==========================================
# 3. GESTIÓN DE TAREAS (CON ACTUALIZACIÓN AUTOMÁTICA)
# ==========================================
class TareasView(QWidget):
    def __init__(self):
        super().__init__()
        self.setStyleSheet(ESTILO_WIDGETS_ADMIN + ESTILO_TABS)
        self.setup_ui()
        
        # Auto-actualización (10s)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.refrescar_datos)
        self.timer.start(10000)

    def setup_ui(self):
        layout = QVBoxLayout(self)
        lbl = QLabel("📝 Gestión de Tareas")
        lbl.setStyleSheet("font-size:18px; font-weight:bold; color:white; margin-bottom:10px;")
        layout.addWidget(lbl)
        
        self.tabs = QTabWidget()
        self.tab_asignar = QWidget()
        self.tab_global = QWidget()
        self.tab_consultar = QWidget()
        
        self.tabs.addTab(self.tab_asignar, "➕ Asignar Tarea")
        self.tabs.addTab(self.tab_global, "📢 Anuncio Global")
        self.tabs.addTab(self.tab_consultar, "🔍 Consultar Historial")
        
        self.setup_asignar()
        self.setup_global()
        self.setup_consultar()
        
        layout.addWidget(self.tabs)

    def refrescar_datos(self):
        self.cargar_tabla_tareas_global()
        if hasattr(self, 'txt_desc') and not self.txt_desc.hasFocus():
            self.cargar_historial_empleado()

    def setup_asignar(self):
        main_layout = QHBoxLayout(self.tab_asignar)
        frame_form = QFrame()
        frame_form.setFixedWidth(350)
        frame_form.setStyleSheet("background: #1a1c20; border-radius: 8px; border: 1px solid #333;")
        l_form = QVBoxLayout(frame_form)
        l_form.setSpacing(10)
        l_form.setContentsMargins(20, 20, 20, 20)
        
        l_form.addWidget(QLabel("1. Empleado:", styleSheet="color:#00f0ff; font-weight:bold;"))
        self.combo_emp = QComboBox()
        self.combo_emp.setFixedHeight(30)
        self.combo_emp.currentIndexChanged.connect(self.cargar_historial_empleado)
        l_form.addWidget(self.combo_emp)
        
        l_form.addWidget(QLabel("2. Prioridad:", styleSheet="color:#ccc; font-weight:bold;"))
        self.combo_tipo = QComboBox()
        self.combo_tipo.addItems(["Verde - Normal", "Amarillo - Media", "Rojo - Alta", "Azul - Info"])
        self.combo_tipo.setFixedHeight(30)
        l_form.addWidget(self.combo_tipo)
        
        l_form.addWidget(QLabel("3. Descripción:", styleSheet="color:#ccc; font-weight:bold;"))
        self.txt_desc = QTextEdit()
        self.txt_desc.setPlaceholderText("Escribe la tarea...")
        self.txt_desc.setStyleSheet("background:#0f1012; border:1px solid #333; color:white; border-radius:4px;")
        l_form.addWidget(self.txt_desc)
        
        self.chk_alarm = QCheckBox("🔔 Programar Alarma")
        self.chk_alarm.setStyleSheet("color: #ccc; font-weight: bold;")
        l_form.addWidget(self.chk_alarm)
        
        self.dt_alarm = QDateTimeEdit(datetime.now())
        self.dt_alarm.setDisplayFormat("dd/MM/yyyy HH:mm")
        self.dt_alarm.setCalendarPopup(True)
        self.dt_alarm.setEnabled(False)
        self.dt_alarm.setStyleSheet("background:#0f1012; color:#00f0ff; padding:5px; border:1px solid #333;")
        l_form.addWidget(self.dt_alarm)
        
        self.chk_alarm.toggled.connect(lambda: self.dt_alarm.setEnabled(self.chk_alarm.isChecked()))
        
        btn_save = QPushButton("💾 ASIGNAR TAREA")
        btn_save.setCursor(Qt.PointingHandCursor)
        btn_save.setFixedHeight(40)
        btn_save.setStyleSheet("background: rgba(0, 255, 0, 0.2); color: #00ff00; border: 1px solid #00ff00; font-weight: bold; border-radius: 4px; margin-top:10px;")
        btn_save.clicked.connect(self.guardar_tarea_individual)
        l_form.addWidget(btn_save)
        
        frame_table = QFrame()
        l_table = QVBoxLayout(frame_table)
        l_table.setContentsMargins(0, 0, 0, 0)
        
        h_head = QHBoxLayout()
        lbl_hist = QLabel("📋 Historial Reciente")
        lbl_hist.setStyleSheet("color: #ccc; font-size: 14px; font-weight: bold;")
        btn_ref_hist = QPushButton("🔄")
        btn_ref_hist.setFixedSize(30,30)
        btn_ref_hist.clicked.connect(self.cargar_historial_empleado)
        h_head.addWidget(lbl_hist)
        h_head.addStretch()
        h_head.addWidget(btn_ref_hist)
        l_table.addLayout(h_head)

        self.tabla_historial = QTableWidget()
        self.tabla_historial.setColumnCount(5)
        self.tabla_historial.setHorizontalHeaderLabels(["ID", "Tipo", "Prioridad", "Descripción", "Estado"])
        self.tabla_historial.horizontalHeader().setSectionResizeMode(3, QHeaderView.Stretch)
        self.tabla_historial.setColumnWidth(0, 40)
        self.tabla_historial.setColumnWidth(1, 50)
        self.tabla_historial.verticalHeader().setVisible(False)
        self.tabla_historial.setStyleSheet("QTableWidget { background: #0f1012; }")
        l_table.addWidget(self.tabla_historial)
        
        main_layout.addWidget(frame_form)
        main_layout.addWidget(frame_table)
        
        self.cargar_empleados_combo()

    # --- PESTAÑA GLOBAL MODIFICADA ---
    def setup_global(self):
        l = QVBoxLayout(self.tab_global)
        l.setContentsMargins(40, 40, 40, 40)
        center_frame = QFrame()
        center_frame.setStyleSheet("background: #1a1c20; border-radius: 8px; border: 1px solid #333;")
        l_form = QVBoxLayout(center_frame)
        l_form.setSpacing(20)
        l_form.setContentsMargins(30, 30, 30, 30)
        
        lbl_title = QLabel("📢 Anuncio Rápido (Sin Asignación Específica)")
        lbl_title.setStyleSheet("font-size: 18px; font-weight: bold; color: #ff00ff; margin-bottom: 10px;")
        lbl_title.setAlignment(Qt.AlignCenter)
        l_form.addWidget(lbl_title)
        
        l_form.addWidget(QLabel("Mensaje / Nota:", styleSheet="color:#ccc; font-weight:bold;"))
        self.txt_global_desc = QTextEdit()
        self.txt_global_desc.setPlaceholderText("Escribe el anuncio para todos...")
        self.txt_global_desc.setStyleSheet("background:#0f1012; border:1px solid #ff00ff; color:white;")
        self.txt_global_desc.setFixedHeight(80)
        l_form.addWidget(self.txt_global_desc)
        
        # --- CHECKBOX PARA ACTIVAR ALARMA GLOBAL ---
        self.chk_global_alarm = QCheckBox("🔔 Activar como Alarma (Con Fecha)")
        self.chk_global_alarm.setStyleSheet("color: #ff00ff; font-weight: bold;")
        l_form.addWidget(self.chk_global_alarm)
        
        # Selector de Fecha (Desactivado por defecto)
        self.dt_global = QDateTimeEdit(datetime.now())
        self.dt_global.setCalendarPopup(True)
        self.dt_global.setDisplayFormat("dd/MM/yyyy HH:mm")
        self.dt_global.setEnabled(False)
        self.dt_global.setStyleSheet("background:#0f1012; color:#ff00ff; border:1px solid #333; padding:5px;")
        l_form.addWidget(self.dt_global)
        
        # Conectar checkbox con fecha
        self.chk_global_alarm.toggled.connect(lambda: self.dt_global.setEnabled(self.chk_global_alarm.isChecked()))
        
        btn_send_all = QPushButton("🚀 ENVIAR A TODOS")
        btn_send_all.setCursor(Qt.PointingHandCursor)
        btn_send_all.setFixedHeight(50)
        btn_send_all.setStyleSheet("background: rgba(255, 0, 255, 0.2); color: #ff00ff; border: 1px solid #ff00ff; font-weight: bold; border-radius: 4px; font-size: 14px;")
        btn_send_all.clicked.connect(self.enviar_anuncio_global)
        l_form.addWidget(btn_send_all)
        l.addWidget(center_frame)
        l.addStretch()

    def enviar_anuncio_global(self):
        desc = self.txt_global_desc.toPlainText().strip()
        if not desc: return QMessageBox.warning(self, "Error", "Escriba el mensaje")
        
        reminder_time = None
        tipo_msg = "¿Enviar NOTA a TODOS?"
        
        # Verificar si activó la alarma
        if self.chk_global_alarm.isChecked():
            reminder_time = self.dt_global.dateTime().toString(Qt.ISODate)
            tipo_msg = f"¿Enviar ALARMA a TODOS?\nFecha: {reminder_time}"
        
        if QMessageBox.question(self, "Confirmar", tipo_msg) != QMessageBox.Yes: return
        
        try:
            emps = db.obtener_todos_los_empleados()
            count = 0
            for e in emps:
                nid = db.generar_id_tarea()
                ahora = datetime.now().isoformat()
                
                doc = {
                    "id_tarea": nid, 
                    "tp_tarea": "Rojo - Importante", # Anuncios siempre rojos
                    "desc_tareas": f"📢 {desc}",
                    "Us_tarea": e["id_usuario"], 
                    "Us_estado": "Pendiente", 
                    "fecha_creacion": ahora
                }
                
                # Solo agregamos fecha si el checkbox estaba marcado
                if reminder_time:
                    doc["reminder_time"] = reminder_time
                    
                db.tareas.insert_one(doc)
                count += 1
                
            QMessageBox.information(self, "Éxito", f"Enviado a {count} empleados.")
            self.txt_global_desc.clear()
            self.cargar_tabla_tareas_global()
            
        except Exception as e: QMessageBox.critical(self, "Error", str(e))

    def setup_consultar(self):
        l = QVBoxLayout(self.tab_consultar)
        filtros = QHBoxLayout()
        self.combo_filtro_t = QComboBox()
        self.combo_filtro_t.addItems(["Todos", "Empleado (ID)", "Estado"])
        self.input_filtro_t = QLineEdit()
        self.input_filtro_t.setPlaceholderText("Valor filtro...")
        btn_bus = QPushButton("🔍 Buscar")
        btn_bus.setObjectName("btn_accion")
        btn_bus.clicked.connect(self.cargar_tabla_tareas_global)
        filtros.addWidget(self.combo_filtro_t)
        filtros.addWidget(self.input_filtro_t)
        filtros.addWidget(btn_bus)
        l.addLayout(filtros)
        
        self.tabla_global = QTableWidget()
        self.tabla_global.setColumnCount(7) 
        self.tabla_global.setHorizontalHeaderLabels(["ID", "Modo", "Prioridad", "Descripción", "Asignado a", "Estado", "Fecha"])
        self.tabla_global.horizontalHeader().setSectionResizeMode(3, QHeaderView.Stretch)
        self.tabla_global.setColumnWidth(1, 60)
        self.tabla_global.verticalHeader().setVisible(False)
        l.addWidget(self.tabla_global)
        self.cargar_tabla_tareas_global()

    def cargar_empleados_combo(self):
        self.combo_emp.blockSignals(True)
        self.combo_emp.clear()
        self.combo_emp.addItem("👥 TODOS LOS EMPLEADOS", "todos")
        emps = db.usuarios.find({"tp_usuario": "empleado"})
        for e in emps:
            self.combo_emp.addItem(f"{e['id_usuario']} - {e['nom_usuario']}", e['id_usuario'])
        self.combo_emp.blockSignals(False)
        self.cargar_historial_empleado()

    def cargar_historial_empleado(self):
        self.tabla_historial.setRowCount(0)
        idx = self.combo_emp.currentIndex()
        if idx < 0: return
        id_data = self.combo_emp.currentData()
        if id_data == "todos": return 
        
        tareas = db.tareas.find({"Us_tarea": int(id_data)}).sort("id_tarea", -1)
        for t in tareas:
            row = self.tabla_historial.rowCount()
            self.tabla_historial.insertRow(row)
            self.tabla_historial.setItem(row, 0, QTableWidgetItem(str(t.get("id_tarea"))))
            
            tiene_alarma = t.get("reminder_time")
            icono = "⏰" if tiene_alarma else "📝"
            item_icon = QTableWidgetItem(icono)
            item_icon.setTextAlignment(Qt.AlignCenter)
            self.tabla_historial.setItem(row, 1, item_icon)
            
            tipo_item = QTableWidgetItem(t.get("tp_tarea"))
            if "Rojo" in t.get("tp_tarea"): tipo_item.setForeground(QColor("#ff4444"))
            elif "Verde" in t.get("tp_tarea"): tipo_item.setForeground(QColor("#00ff00"))
            self.tabla_historial.setItem(row, 2, tipo_item)
            
            self.tabla_historial.setItem(row, 3, QTableWidgetItem(t.get("desc_tareas")))
            
            estado = t.get("Us_estado")
            it = QTableWidgetItem(estado)
            if estado == "Pendiente": it.setForeground(QColor("#ffaa00"))
            elif estado == "Finalizada": it.setForeground(QColor("#00ff00"))
            self.tabla_historial.setItem(row, 4, it)

    def guardar_tarea_individual(self):
        id_emp_data = self.combo_emp.currentData()
        tipo = self.combo_tipo.currentText()
        desc = self.txt_desc.toPlainText().strip()
        if not desc: return QMessageBox.warning(self, "Error", "Escriba una descripción")
        
        reminder_time = None
        if self.chk_alarm.isChecked():
            reminder_time = self.dt_alarm.dateTime().toString(Qt.ISODate)
        
        try:
            ahora = datetime.now().isoformat()
            lista_ids = []
            if id_emp_data == "todos":
                empleados = db.obtener_todos_los_empleados()
                for e in empleados:
                    lista_ids.append(e["id_usuario"])
            else:
                lista_ids.append(int(id_emp_data))
            
            count = 0
            for uid in lista_ids:
                nuevo_id = db.generar_id_tarea()
                doc = {
                    "id_tarea": nuevo_id,
                    "tp_tarea": tipo,
                    "desc_tareas": desc,
                    "Us_tarea": uid,
                    "Us_estado": "Pendiente",
                    "fecha_creacion": ahora
                }
                if reminder_time: doc["reminder_time"] = reminder_time
                db.tareas.insert_one(doc)
                count += 1
            
            msg = f"Tarea asignada a {count} empleados." if id_emp_data == "todos" else "Tarea asignada correctamente."
            QMessageBox.information(self, "Éxito", msg)
            self.txt_desc.clear()
            if id_emp_data != "todos": self.cargar_historial_empleado()
            self.cargar_tabla_tareas_global()
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def cargar_tabla_tareas_global(self):
        self.tabla_global.setRowCount(0)
        filtro = self.combo_filtro_t.currentText()
        val = self.input_filtro_t.text().strip()
        query = {}
        if val:
            if filtro == "Empleado (ID)" and val.isdigit(): query = {"Us_tarea": int(val)}
            elif filtro == "Estado": query = {"Us_estado": {"$regex": val, "$options": "i"}}
        
        tareas = db.tareas.find(query).sort("id_tarea", -1)
        users_map = {u['id_usuario']: u['nom_usuario'] for u in db.usuarios.find()}
        
        for t in tareas:
            row = self.tabla_global.rowCount()
            self.tabla_global.insertRow(row)
            self.tabla_global.setItem(row, 0, QTableWidgetItem(str(t.get("id_tarea"))))
            
            tiene_alarma = t.get("reminder_time")
            icono = "⏰" if tiene_alarma else "📝"
            item_icon = QTableWidgetItem(icono)
            item_icon.setTextAlignment(Qt.AlignCenter)
            self.tabla_global.setItem(row, 1, item_icon)
            
            it_tipo = QTableWidgetItem(t.get("tp_tarea"))
            if "Rojo" in t.get("tp_tarea"): it_tipo.setForeground(QColor("#ff4444"))
            elif "Verde" in t.get("tp_tarea"): it_tipo.setForeground(QColor("#00ff00"))
            self.tabla_global.setItem(row, 2, it_tipo)
            
            self.tabla_global.setItem(row, 3, QTableWidgetItem(t.get("desc_tareas")))
            
            uid = t.get("Us_tarea")
            nombre = users_map.get(uid, f"ID {uid}")
            self.tabla_global.setItem(row, 4, QTableWidgetItem(nombre))
            
            est = t.get("Us_estado")
            it_e = QTableWidgetItem(est)
            if est == "Pendiente": it_e.setForeground(QColor("#ffaa00"))
            elif est == "Finalizada": it_e.setForeground(QColor("#00ff00"))
            self.tabla_global.setItem(row, 5, it_e)
            
            f_raw = t.get("fecha_creacion", "")
            f_bonita = f_raw.split("T")[0] if "T" in str(f_raw) else str(f_raw)
            self.tabla_global.setItem(row, 6, QTableWidgetItem(f_bonita))
    def __init__(self):
        super().__init__()
        self.setStyleSheet(ESTILO_WIDGETS_ADMIN + ESTILO_TABS)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        lbl = QLabel("📝 Gestión de Tareas")
        lbl.setStyleSheet("font-size:18px; font-weight:bold; color:white; margin-bottom:10px;")
        layout.addWidget(lbl)
        
        self.tabs = QTabWidget()
        self.tab_asignar = QWidget()
        self.tab_global = QWidget()
        self.tab_consultar = QWidget()
        
        self.tabs.addTab(self.tab_asignar, "➕ Asignar Tarea")
        self.tabs.addTab(self.tab_global, "📢 Anuncio Global")
        self.tabs.addTab(self.tab_consultar, "🔍 Consultar Historial")
        
        self.setup_asignar()
        self.setup_global()
        self.setup_consultar()
        
        layout.addWidget(self.tabs)
        
        # Timer de auto-actualización (10s)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.refrescar_datos)
        self.timer.start(10000)

    def refrescar_datos(self):
        self.cargar_tabla_tareas_global()
        if not self.txt_desc.hasFocus():
            self.cargar_historial_empleado()

    def setup_asignar(self):
        main_layout = QHBoxLayout(self.tab_asignar)
        
        # --- IZQUIERDA ---
        frame_form = QFrame()
        frame_form.setFixedWidth(350)
        frame_form.setStyleSheet("background: #1a1c20; border-radius: 8px; border: 1px solid #333;")
        l_form = QVBoxLayout(frame_form)
        l_form.setSpacing(10)
        l_form.setContentsMargins(20, 20, 20, 20)
        
        l_form.addWidget(QLabel("1. Empleado:", styleSheet="color:#00f0ff; font-weight:bold;"))
        self.combo_emp = QComboBox()
        self.combo_emp.setFixedHeight(30)
        self.combo_emp.currentIndexChanged.connect(self.cargar_historial_empleado)
        l_form.addWidget(self.combo_emp)
        
        l_form.addWidget(QLabel("2. Prioridad:", styleSheet="color:#ccc; font-weight:bold;"))
        self.combo_tipo = QComboBox()
        self.combo_tipo.addItems(["Verde - Normal", "Amarillo - Media", "Rojo - Alta", "Azul - Info"])
        self.combo_tipo.setFixedHeight(30)
        l_form.addWidget(self.combo_tipo)
        
        l_form.addWidget(QLabel("3. Descripción:", styleSheet="color:#ccc; font-weight:bold;"))
        self.txt_desc = QTextEdit()
        self.txt_desc.setPlaceholderText("Escribe la tarea...")
        self.txt_desc.setStyleSheet("background:#0f1012; border:1px solid #333; color:white; border-radius:4px;")
        l_form.addWidget(self.txt_desc)
        
        self.chk_alarm = QCheckBox("🔔 Programar Alarma")
        self.chk_alarm.setStyleSheet("color: #ccc; font-weight: bold;")
        l_form.addWidget(self.chk_alarm)
        
        self.dt_alarm = QDateTimeEdit(datetime.now())
        self.dt_alarm.setDisplayFormat("dd/MM/yyyy HH:mm")
        self.dt_alarm.setCalendarPopup(True)
        self.dt_alarm.setEnabled(False)
        self.dt_alarm.setStyleSheet("background:#0f1012; color:#00f0ff; padding:5px; border:1px solid #333;")
        l_form.addWidget(self.dt_alarm)
        
        self.chk_alarm.toggled.connect(lambda: self.dt_alarm.setEnabled(self.chk_alarm.isChecked()))
        
        btn_save = QPushButton("💾 ASIGNAR TAREA")
        btn_save.setCursor(Qt.PointingHandCursor)
        btn_save.setFixedHeight(40)
        btn_save.setStyleSheet("background: rgba(0, 255, 0, 0.2); color: #00ff00; border: 1px solid #00ff00; font-weight: bold; border-radius: 4px; margin-top:10px;")
        btn_save.clicked.connect(self.guardar_tarea_individual)
        l_form.addWidget(btn_save)
        
        # --- DERECHA ---
        frame_table = QFrame()
        l_table = QVBoxLayout(frame_table)
        l_table.setContentsMargins(0, 0, 0, 0)
        
        h_head = QHBoxLayout()
        lbl_hist = QLabel("📋 Historial Reciente")
        lbl_hist.setStyleSheet("color: #ccc; font-size: 14px; font-weight: bold;")
        btn_ref_hist = QPushButton("🔄")
        btn_ref_hist.setFixedSize(30,30)
        btn_ref_hist.clicked.connect(self.cargar_historial_empleado)
        h_head.addWidget(lbl_hist)
        h_head.addStretch()
        h_head.addWidget(btn_ref_hist)
        l_table.addLayout(h_head)

        self.tabla_historial = QTableWidget()
        self.tabla_historial.setColumnCount(5) # ID, TIPO(Icono), Prioridad, Desc, Estado
        self.tabla_historial.setHorizontalHeaderLabels(["ID", "Tipo", "Prioridad", "Descripción", "Estado"])
        self.tabla_historial.horizontalHeader().setSectionResizeMode(3, QHeaderView.Stretch) # Desc estirada
        self.tabla_historial.setColumnWidth(0, 40) # ID pequeño
        self.tabla_historial.setColumnWidth(1, 50) # Tipo pequeño
        self.tabla_historial.verticalHeader().setVisible(False)
        self.tabla_historial.setStyleSheet("QTableWidget { background: #0f1012; }")
        l_table.addWidget(self.tabla_historial)
        
        main_layout.addWidget(frame_form)
        main_layout.addWidget(frame_table)
        
        self.cargar_empleados_combo()

    def setup_global(self):
        l = QVBoxLayout(self.tab_global)
        l.setContentsMargins(40, 40, 40, 40)
        center_frame = QFrame()
        center_frame.setStyleSheet("background: #1a1c20; border-radius: 8px; border: 1px solid #333;")
        l_form = QVBoxLayout(center_frame)
        l_form.setSpacing(20)
        l_form.setContentsMargins(30, 30, 30, 30)
        
        lbl_title = QLabel("📢 Anuncio Rápido (Sin Asignación Específica)")
        lbl_title.setStyleSheet("font-size: 18px; font-weight: bold; color: #ff00ff; margin-bottom: 10px;")
        lbl_title.setAlignment(Qt.AlignCenter)
        l_form.addWidget(lbl_title)
        
        l_form.addWidget(QLabel("Mensaje:", styleSheet="color:#ccc; font-weight:bold;"))
        self.txt_global_desc = QTextEdit()
        self.txt_global_desc.setStyleSheet("background:#0f1012; border:1px solid #ff00ff; color:white;")
        self.txt_global_desc.setFixedHeight(80)
        l_form.addWidget(self.txt_global_desc)
        
        l_form.addWidget(QLabel("Fecha Alarma:", styleSheet="color:#ccc; font-weight:bold;"))
        self.dt_global = QDateTimeEdit(datetime.now())
        self.dt_global.setCalendarPopup(True)
        self.dt_global.setDisplayFormat("dd/MM/yyyy HH:mm")
        self.dt_global.setStyleSheet("background:#0f1012; color:#00f0ff; border:1px solid #333; padding:5px;")
        l_form.addWidget(self.dt_global)
        
        btn_send_all = QPushButton("🚀 ENVIAR A TODOS")
        btn_send_all.setCursor(Qt.PointingHandCursor)
        btn_send_all.setFixedHeight(50)
        btn_send_all.setStyleSheet("background: rgba(255, 0, 255, 0.2); color: #ff00ff; border: 1px solid #ff00ff; font-weight: bold; border-radius: 4px; font-size: 14px;")
        btn_send_all.clicked.connect(self.enviar_anuncio_global)
        l_form.addWidget(btn_send_all)
        l.addWidget(center_frame)
        l.addStretch()

    def setup_consultar(self):
        l = QVBoxLayout(self.tab_consultar)
        filtros = QHBoxLayout()
        self.combo_filtro_t = QComboBox()
        self.combo_filtro_t.addItems(["Todos", "Empleado (ID)", "Estado"])
        self.input_filtro_t = QLineEdit()
        self.input_filtro_t.setPlaceholderText("Valor filtro...")
        btn_bus = QPushButton("🔍 Buscar")
        btn_bus.setObjectName("btn_accion")
        btn_bus.clicked.connect(self.cargar_tabla_tareas_global)
        filtros.addWidget(self.combo_filtro_t)
        filtros.addWidget(self.input_filtro_t)
        filtros.addWidget(btn_bus)
        l.addLayout(filtros)
        
        self.tabla_global = QTableWidget()
        self.tabla_global.setColumnCount(7) # ID, ICONO, TIPO, DESC, ASIGNADO, ESTADO, FECHA
        self.tabla_global.setHorizontalHeaderLabels(["ID", "Modo", "Prioridad", "Descripción", "Asignado a", "Estado", "Fecha"])
        self.tabla_global.horizontalHeader().setSectionResizeMode(3, QHeaderView.Stretch)
        self.tabla_global.setColumnWidth(1, 60) # Ancho columna icono
        self.tabla_global.verticalHeader().setVisible(False)
        l.addWidget(self.tabla_global)
        self.cargar_tabla_tareas_global()

    def cargar_empleados_combo(self):
        self.combo_emp.blockSignals(True)
        self.combo_emp.clear()
        self.combo_emp.addItem("👥 TODOS LOS EMPLEADOS", "todos")
        emps = db.usuarios.find({"tp_usuario": "empleado"})
        for e in emps:
            self.combo_emp.addItem(f"{e['id_usuario']} - {e['nom_usuario']}", e['id_usuario'])
        self.combo_emp.blockSignals(False)
        self.cargar_historial_empleado()

    def cargar_historial_empleado(self):
        self.tabla_historial.setRowCount(0)
        idx = self.combo_emp.currentIndex()
        if idx < 0: return
        
        id_data = self.combo_emp.currentData()
        if id_data == "todos": return 
        
        tareas = db.tareas.find({"Us_tarea": int(id_data)}).sort("id_tarea", -1)
        
        for t in tareas:
            row = self.tabla_historial.rowCount()
            self.tabla_historial.insertRow(row)
            
            # ID
            self.tabla_historial.setItem(row, 0, QTableWidgetItem(str(t.get("id_tarea"))))
            
            # ICONO (El "Visto" que pediste)
            tiene_alarma = t.get("reminder_time")
            icono = "⏰" if tiene_alarma else "📝"
            self.tabla_historial.setItem(row, 1, QTableWidgetItem(icono))
            self.tabla_historial.item(row, 1).setTextAlignment(Qt.AlignCenter)
            
            # PRIORIDAD
            tipo_item = QTableWidgetItem(t.get("tp_tarea"))
            if "Rojo" in t.get("tp_tarea"): tipo_item.setForeground(QColor("#ff4444"))
            elif "Verde" in t.get("tp_tarea"): tipo_item.setForeground(QColor("#00ff00"))
            self.tabla_historial.setItem(row, 2, tipo_item)
            
            # DESC
            self.tabla_historial.setItem(row, 3, QTableWidgetItem(t.get("desc_tareas")))
            
            # ESTADO
            estado = t.get("Us_estado")
            it = QTableWidgetItem(estado)
            if estado == "Pendiente": it.setForeground(QColor("#ffaa00"))
            elif estado == "Finalizada": it.setForeground(QColor("#00ff00"))
            self.tabla_historial.setItem(row, 4, it)

    def guardar_tarea_individual(self):
        id_emp_data = self.combo_emp.currentData()
        tipo = self.combo_tipo.currentText()
        desc = self.txt_desc.toPlainText().strip()
        if not desc: return QMessageBox.warning(self, "Error", "Escriba una descripción")
        
        reminder_time = None
        if self.chk_alarm.isChecked():
            reminder_time = self.dt_alarm.dateTime().toString(Qt.ISODate)
        
        try:
            ahora = datetime.now().isoformat()
            lista_ids = []
            if id_emp_data == "todos":
                empleados = db.obtener_todos_los_empleados()
                for e in empleados:
                    lista_ids.append(e["id_usuario"])
            else:
                lista_ids.append(int(id_emp_data))
            
            count = 0
            for uid in lista_ids:
                nuevo_id = db.generar_id_tarea()
                doc = {
                    "id_tarea": nuevo_id,
                    "tp_tarea": tipo,
                    "desc_tareas": desc,
                    "Us_tarea": uid,
                    "Us_estado": "Pendiente",
                    "fecha_creacion": ahora
                }
                if reminder_time: doc["reminder_time"] = reminder_time
                db.tareas.insert_one(doc)
                count += 1
            
            msg = f"Tarea asignada a {count} empleados." if id_emp_data == "todos" else "Tarea asignada correctamente."
            QMessageBox.information(self, "Éxito", msg)
            self.txt_desc.clear()
            if id_emp_data != "todos": self.cargar_historial_empleado()
            self.cargar_tabla_tareas_global()
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def enviar_anuncio_global(self):
        desc = self.txt_global_desc.toPlainText().strip()
        if not desc: return QMessageBox.warning(self, "Error", "Escriba el mensaje")
        fecha_alarma = self.dt_global.dateTime().toString(Qt.ISODate)
        
        if QMessageBox.question(self, "Confirmar", f"¿Enviar a TODOS?\n{fecha_alarma}") != QMessageBox.Yes: return
        
        try:
            emps = db.obtener_todos_los_empleados()
            for e in emps:
                nid = db.generar_id_tarea()
                ahora = datetime.now().isoformat()
                db.tareas.insert_one({
                    "id_tarea": nid, "tp_tarea": "Rojo - Importante", "desc_tareas": f"📢 {desc}",
                    "Us_tarea": e["id_usuario"], "Us_estado": "Pendiente", "fecha_creacion": ahora, "reminder_time": fecha_alarma
                })
            QMessageBox.information(self, "Éxito", "Enviado")
            self.txt_global_desc.clear()
            self.cargar_tabla_tareas_global()
        except Exception as e: QMessageBox.critical(self, "Error", str(e))

    def cargar_tabla_tareas_global(self):
        self.tabla_global.setRowCount(0)
        filtro = self.combo_filtro_t.currentText()
        val = self.input_filtro_t.text().strip()
        query = {}
        if val:
            if filtro == "Empleado (ID)" and val.isdigit(): query = {"Us_tarea": int(val)}
            elif filtro == "Estado": query = {"Us_estado": {"$regex": val, "$options": "i"}}
        
        tareas = db.tareas.find(query).sort("id_tarea", -1)
        users_map = {u['id_usuario']: u['nom_usuario'] for u in db.usuarios.find()}
        
        for t in tareas:
            row = self.tabla_global.rowCount()
            self.tabla_global.insertRow(row)
            
            self.tabla_global.setItem(row, 0, QTableWidgetItem(str(t.get("id_tarea"))))
            
            # ICONO (Modo)
            tiene_alarma = t.get("reminder_time")
            icono = "⏰" if tiene_alarma else "📝"
            item_icon = QTableWidgetItem(icono)
            item_icon.setTextAlignment(Qt.AlignCenter)
            self.tabla_global.setItem(row, 1, item_icon)
            
            # Prioridad
            it_tipo = QTableWidgetItem(t.get("tp_tarea"))
            if "Rojo" in t.get("tp_tarea"): it_tipo.setForeground(QColor("#ff4444"))
            elif "Verde" in t.get("tp_tarea"): it_tipo.setForeground(QColor("#00ff00"))
            self.tabla_global.setItem(row, 2, it_tipo)
            
            self.tabla_global.setItem(row, 3, QTableWidgetItem(t.get("desc_tareas")))
            
            uid = t.get("Us_tarea")
            nombre = users_map.get(uid, f"ID {uid}")
            self.tabla_global.setItem(row, 4, QTableWidgetItem(nombre))
            
            est = t.get("Us_estado")
            it_e = QTableWidgetItem(est)
            if est == "Pendiente": it_e.setForeground(QColor("#ffaa00"))
            elif est == "Finalizada": it_e.setForeground(QColor("#00ff00"))
            self.tabla_global.setItem(row, 5, it_e)
            
            f_raw = t.get("fecha_creacion", "")
            f_bonita = f_raw.split("T")[0] if "T" in str(f_raw) else str(f_raw)
            self.tabla_global.setItem(row, 6, QTableWidgetItem(f_bonita))
    def __init__(self):
        super().__init__()
        self.setStyleSheet(ESTILO_WIDGETS_ADMIN + ESTILO_TABS)
        self.setup_ui()
        
        # --- AUTO ACTUALIZACIÓN TAREAS (10s) ---
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.refrescar_datos)
        self.timer.start(10000)

    def setup_ui(self):
        layout = QVBoxLayout(self)
        lbl = QLabel("📝 Gestión de Tareas")
        lbl.setStyleSheet("font-size:18px; font-weight:bold; color:white; margin-bottom:10px;")
        layout.addWidget(lbl)
        self.tabs = QTabWidget()
        self.tab_asignar = QWidget()
        self.tab_global = QWidget()
        self.tab_consultar = QWidget()
        self.tabs.addTab(self.tab_asignar, "➕ Asignar Tarea")
        self.tabs.addTab(self.tab_global, "📢 Anuncio Global")
        self.tabs.addTab(self.tab_consultar, "🔍 Consultar Historial")
        self.setup_asignar()
        self.setup_global()
        self.setup_consultar()
        layout.addWidget(self.tabs)

    def refrescar_datos(self):
        # Actualiza las tablas en segundo plano
        self.cargar_tabla_tareas_global()
        # Solo actualizamos el historial individual si no estamos escribiendo (para no molestar)
        if not self.txt_desc.hasFocus():
            self.cargar_historial_empleado()

    def setup_asignar(self):
        main_layout = QHBoxLayout(self.tab_asignar)
        frame_form = QFrame()
        frame_form.setFixedWidth(350)
        frame_form.setStyleSheet("background: #1a1c20; border-radius: 8px; border: 1px solid #333;")
        l_form = QVBoxLayout(frame_form)
        l_form.setSpacing(10)
        l_form.setContentsMargins(20, 20, 20, 20)
        l_form.addWidget(QLabel("1. Empleado:", styleSheet="color:#00f0ff; font-weight:bold;"))
        self.combo_emp = QComboBox()
        self.combo_emp.setFixedHeight(30)
        self.combo_emp.currentIndexChanged.connect(self.cargar_historial_empleado)
        l_form.addWidget(self.combo_emp)
        l_form.addWidget(QLabel("2. Prioridad:", styleSheet="color:#ccc; font-weight:bold;"))
        self.combo_tipo = QComboBox()
        self.combo_tipo.addItems(["Verde - Normal", "Amarillo - Media", "Rojo - Alta", "Azul - Info"])
        self.combo_tipo.setFixedHeight(30)
        l_form.addWidget(self.combo_tipo)
        l_form.addWidget(QLabel("3. Descripción:", styleSheet="color:#ccc; font-weight:bold;"))
        self.txt_desc = QTextEdit()
        self.txt_desc.setPlaceholderText("Escribe la tarea...")
        self.txt_desc.setStyleSheet("background:#0f1012; border:1px solid #333; color:white; border-radius:4px;")
        l_form.addWidget(self.txt_desc)
        self.chk_alarm = QCheckBox("🔔 Programar Alarma")
        self.chk_alarm.setStyleSheet("color: #ccc; font-weight: bold;")
        l_form.addWidget(self.chk_alarm)
        self.dt_alarm = QDateTimeEdit(datetime.now())
        self.dt_alarm.setDisplayFormat("dd/MM/yyyy HH:mm")
        self.dt_alarm.setCalendarPopup(True)
        self.dt_alarm.setEnabled(False)
        self.dt_alarm.setStyleSheet("background:#0f1012; color:#00f0ff; padding:5px; border:1px solid #333;")
        l_form.addWidget(self.dt_alarm)
        self.chk_alarm.toggled.connect(lambda: self.dt_alarm.setEnabled(self.chk_alarm.isChecked()))
        btn_save = QPushButton("💾 ASIGNAR TAREA")
        btn_save.setCursor(Qt.PointingHandCursor)
        btn_save.setFixedHeight(40)
        btn_save.setStyleSheet("background: rgba(0, 255, 0, 0.2); color: #00ff00; border: 1px solid #00ff00; font-weight: bold; border-radius: 4px; margin-top:10px;")
        btn_save.clicked.connect(self.guardar_tarea_individual)
        l_form.addWidget(btn_save)
        frame_table = QFrame()
        l_table = QVBoxLayout(frame_table)
        l_table.setContentsMargins(0, 0, 0, 0)
        h_head = QHBoxLayout()
        lbl_hist = QLabel("📋 Historial Reciente")
        lbl_hist.setStyleSheet("color: #ccc; font-size: 14px; font-weight: bold;")
        btn_ref_hist = QPushButton("🔄")
        btn_ref_hist.setFixedSize(30,30)
        btn_ref_hist.clicked.connect(self.cargar_historial_empleado)
        h_head.addWidget(lbl_hist)
        h_head.addStretch()
        h_head.addWidget(btn_ref_hist)
        l_table.addLayout(h_head)
        self.tabla_historial = QTableWidget()
        self.tabla_historial.setColumnCount(4)
        self.tabla_historial.setHorizontalHeaderLabels(["ID", "Prioridad", "Descripción", "Estado"])
        self.tabla_historial.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        self.tabla_historial.verticalHeader().setVisible(False)
        self.tabla_historial.setStyleSheet("QTableWidget { background: #0f1012; }")
        l_table.addWidget(self.tabla_historial)
        main_layout.addWidget(frame_form)
        main_layout.addWidget(frame_table)
        self.cargar_empleados_combo()

    def setup_global(self):
        l = QVBoxLayout(self.tab_global)
        l.setContentsMargins(40, 40, 40, 40)
        center_frame = QFrame()
        center_frame.setStyleSheet("background: #1a1c20; border-radius: 8px; border: 1px solid #333;")
        l_form = QVBoxLayout(center_frame)
        l_form.setSpacing(20)
        l_form.setContentsMargins(30, 30, 30, 30)
        lbl_title = QLabel("📢 Anuncio Rápido (Sin Asignación Específica)")
        lbl_title.setStyleSheet("font-size: 18px; font-weight: bold; color: #ff00ff; margin-bottom: 10px;")
        lbl_title.setAlignment(Qt.AlignCenter)
        l_form.addWidget(lbl_title)
        l_form.addWidget(QLabel("Mensaje:", styleSheet="color:#ccc; font-weight:bold;"))
        self.txt_global_desc = QTextEdit()
        self.txt_global_desc.setStyleSheet("background:#0f1012; border:1px solid #ff00ff; color:white;")
        self.txt_global_desc.setFixedHeight(80)
        l_form.addWidget(self.txt_global_desc)
        l_form.addWidget(QLabel("Fecha Alarma:", styleSheet="color:#ccc; font-weight:bold;"))
        self.dt_global = QDateTimeEdit(datetime.now())
        self.dt_global.setCalendarPopup(True)
        self.dt_global.setDisplayFormat("dd/MM/yyyy HH:mm")
        self.dt_global.setStyleSheet("background:#0f1012; color:#00f0ff; border:1px solid #333; padding:5px;")
        l_form.addWidget(self.dt_global)
        btn_send_all = QPushButton("🚀 ENVIAR A TODOS")
        btn_send_all.setCursor(Qt.PointingHandCursor)
        btn_send_all.setFixedHeight(50)
        btn_send_all.setStyleSheet("background: rgba(255, 0, 255, 0.2); color: #ff00ff; border: 1px solid #ff00ff; font-weight: bold; border-radius: 4px; font-size: 14px;")
        btn_send_all.clicked.connect(self.enviar_anuncio_global)
        l_form.addWidget(btn_send_all)
        l.addWidget(center_frame)
        l.addStretch()

    def setup_consultar(self):
        l = QVBoxLayout(self.tab_consultar)
        filtros = QHBoxLayout()
        self.combo_filtro_t = QComboBox()
        self.combo_filtro_t.addItems(["Todos", "Empleado (ID)", "Estado"])
        self.input_filtro_t = QLineEdit()
        self.input_filtro_t.setPlaceholderText("Valor filtro...")
        btn_bus = QPushButton("🔍 Actualizar")
        btn_bus.setObjectName("btn_accion")
        btn_bus.clicked.connect(self.cargar_tabla_tareas_global)
        filtros.addWidget(self.combo_filtro_t)
        filtros.addWidget(self.input_filtro_t)
        filtros.addWidget(btn_bus)
        l.addLayout(filtros)
        self.tabla_global = QTableWidget()
        self.tabla_global.setColumnCount(6)
        self.tabla_global.setHorizontalHeaderLabels(["ID", "Tipo", "Descripción", "Asignado a", "Estado", "Fecha"])
        self.tabla_global.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        self.tabla_global.verticalHeader().setVisible(False)
        l.addWidget(self.tabla_global)
        self.cargar_tabla_tareas_global()

    def cargar_empleados_combo(self):
        self.combo_emp.blockSignals(True)
        self.combo_emp.clear()
        # self.combo_emp.addItem("👥 TODOS LOS EMPLEADOS", "todos")
        emps = db.usuarios.find({"tp_usuario": "empleado"})
        for e in emps:
            self.combo_emp.addItem(f"{e['id_usuario']} - {e['nom_usuario']}", e['id_usuario'])
        self.combo_emp.blockSignals(False)
        self.cargar_historial_empleado()

    def cargar_historial_empleado(self):
        self.tabla_historial.setRowCount(0)
        idx = self.combo_emp.currentIndex()
        if idx < 0: return
        id_data = self.combo_emp.currentData()
        if id_data == "todos": return 
        tareas = db.tareas.find({"Us_tarea": int(id_data)}).sort("id_tarea", -1)
        for t in tareas:
            row = self.tabla_historial.rowCount()
            self.tabla_historial.insertRow(row)
            self.tabla_historial.setItem(row, 0, QTableWidgetItem(str(t.get("id_tarea"))))
            tipo_item = QTableWidgetItem(t.get("tp_tarea"))
            if "Rojo" in t.get("tp_tarea"): tipo_item.setForeground(QColor("#ff4444"))
            elif "Verde" in t.get("tp_tarea"): tipo_item.setForeground(QColor("#00ff00"))
            self.tabla_historial.setItem(row, 1, tipo_item)
            self.tabla_historial.setItem(row, 2, QTableWidgetItem(t.get("desc_tareas")))
            estado = t.get("Us_estado")
            it = QTableWidgetItem(estado)
            if estado == "Pendiente": it.setForeground(QColor("#ffaa00"))
            elif estado == "Finalizada": it.setForeground(QColor("#00ff00"))
            self.tabla_historial.setItem(row, 3, it)

    def guardar_tarea_individual(self):
        id_emp_data = self.combo_emp.currentData()
        tipo = self.combo_tipo.currentText()
        desc = self.txt_desc.toPlainText().strip()
        if not desc: return QMessageBox.warning(self, "Error", "Escriba una descripción")
        reminder_time = None
        if self.chk_alarm.isChecked():
            reminder_time = self.dt_alarm.dateTime().toString(Qt.ISODate)
        try:
            ahora = datetime.now().isoformat()
            lista_ids = []
            if id_emp_data == "todos":
                empleados = db.obtener_todos_los_empleados()
                for e in empleados:
                    lista_ids.append(e["id_usuario"])
            else:
                lista_ids.append(int(id_emp_data))
            count = 0
            for uid in lista_ids:
                nuevo_id = db.generar_id_tarea()
                doc = {
                    "id_tarea": nuevo_id,
                    "tp_tarea": tipo,
                    "desc_tareas": desc,
                    "Us_tarea": uid,
                    "Us_estado": "Pendiente",
                    "fecha_creacion": ahora
                }
                if reminder_time: doc["reminder_time"] = reminder_time
                db.tareas.insert_one(doc)
                count += 1
            if id_emp_data == "todos":
                QMessageBox.information(self, "Éxito", f"Tarea asignada a {count} empleados.")
            else:
                QMessageBox.information(self, "Éxito", f"Tarea asignada correctamente.")
            self.txt_desc.clear()
            if id_emp_data != "todos":
                self.cargar_historial_empleado()
            self.cargar_tabla_tareas_global()
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def enviar_anuncio_global(self):
        desc = self.txt_global_desc.toPlainText().strip()
        if not desc: return QMessageBox.warning(self, "Error", "Escriba el mensaje")
        fecha_alarma = self.dt_global.dateTime().toString(Qt.ISODate)
        if QMessageBox.question(self, "Confirmar", f"¿Enviar a TODOS?\n{fecha_alarma}") != QMessageBox.Yes: return
        try:
            emps = db.obtener_todos_los_empleados()
            for e in emps:
                nid = db.generar_id_tarea()
                ahora = datetime.now().isoformat()
                db.tareas.insert_one({
                    "id_tarea": nid, "tp_tarea": "Rojo - Importante", "desc_tareas": f"📢 {desc}",
                    "Us_tarea": e["id_usuario"], "Us_estado": "Pendiente", "fecha_creacion": ahora, "reminder_time": fecha_alarma
                })
            QMessageBox.information(self, "Éxito", "Enviado")
            self.txt_global_desc.clear()
        except Exception as e: QMessageBox.critical(self, "Error", str(e))

    def cargar_tabla_tareas_global(self):
        self.tabla_global.setRowCount(0)
        filtro = self.combo_filtro_t.currentText()
        val = self.input_filtro_t.text().strip()
        query = {}
        if val:
            if filtro == "Empleado (ID)" and val.isdigit(): query = {"Us_tarea": int(val)}
            elif filtro == "Estado": query = {"Us_estado": {"$regex": val, "$options": "i"}}
        tareas = db.tareas.find(query).sort("id_tarea", -1)
        users_map = {u['id_usuario']: u['nom_usuario'] for u in db.usuarios.find()}
        for t in tareas:
            row = self.tabla_global.rowCount()
            self.tabla_global.insertRow(row)
            self.tabla_global.setItem(row, 0, QTableWidgetItem(str(t.get("id_tarea"))))
            it_tipo = QTableWidgetItem(t.get("tp_tarea"))
            if "Rojo" in t.get("tp_tarea"): it_tipo.setForeground(QColor("#ff4444"))
            elif "Verde" in t.get("tp_tarea"): it_tipo.setForeground(QColor("#00ff00"))
            self.tabla_global.setItem(row, 1, it_tipo)
            self.tabla_global.setItem(row, 2, QTableWidgetItem(t.get("desc_tareas")))
            uid = t.get("Us_tarea")
            nombre = users_map.get(uid, f"ID {uid}")
            self.tabla_global.setItem(row, 3, QTableWidgetItem(nombre))
            est = t.get("Us_estado")
            it_e = QTableWidgetItem(est)
            if est == "Pendiente": it_e.setForeground(QColor("#ffaa00"))
            elif est == "Finalizada": it_e.setForeground(QColor("#00ff00"))
            self.tabla_global.setItem(row, 4, it_e)
            f_raw = t.get("fecha_creacion", "")
            f_bonita = f_raw.split("T")[0] if "T" in str(f_raw) else str(f_raw)
            self.tabla_global.setItem(row, 5, QTableWidgetItem(f_bonita))