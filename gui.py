import sys
import traceback
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QListWidget, QListWidgetItem, QTextEdit, QLineEdit,
    QCheckBox, QPushButton, QTableWidget, QTableWidgetItem,
    QHeaderView, QSplitter, QMessageBox, QFrame, QProgressBar
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QSize
from PyQt6.QtGui import QFont, QColor, QPalette, QIcon

import matplotlib
matplotlib.use('QtAgg')
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from matplotlib.backends.backend_qt import NavigationToolbar2QT  # <-- AGREGADO

# Importar lógica del proyecto
from utils import generar_dataset
import algorithms
from benchmarker import medir_tiempo, ejecutar_codigo_personalizado
from complexity_detector import estimar_complejidad
from visualizer import graficar_resultados

# Mapeo de algoritmos
ALGORITMOS_EJEMPLO = {
    "Bubble Sort (O(n²))": algorithms.bubble_sort,
    "Quick Sort (O(n log n))": algorithms.quick_sort,
    "Merge Sort (O(n log n))": algorithms.merge_sort,
    "Insertion Sort (O(n²))": algorithms.insertion_sort,
    "Selection Sort (O(n²))": algorithms.selection_sort,
    "Timsort (Nativo) (O(n log n))": algorithms.timsort_nativo,
    "Búsqueda Lineal (O(n))": algorithms.busqueda_lineal,
    "Búsqueda Binaria (O(log n))": algorithms.busqueda_binaria,
    "Fibonacci Recursivo (O(2ⁿ))": algorithms.fibonacci_recursivo,
    "Fibonacci Iterativo (O(n))": algorithms.fibonacci_iterativo,
}

EJEMPLO_CODIGO_PERSONALIZADO = """# Código Personalizado (data: lista, n: tamaño)
for i in range(n):
    pass
"""


class WorkerThread(QThread):
    progress_signal = pyqtSignal(int, str)  # progreso %, mensaje
    result_signal = pyqtSignal(dict, list)  # resultados dict, tamanos list
    error_signal = pyqtSignal(str)

    def __init__(self, config):
        super().__init__()
        self.config = config

    def run(self):
        try:
            algoritmos_seleccionados = self.config['algoritmos']
            incluir_personalizado = self.config['incluir_personalizado']
            codigo_personalizado = self.config['codigo']
            tamanos = self.config['tamanos']

            resultados = {}

            # Preparar lista de tareas
            tareas = []
            for nombre, func in algoritmos_seleccionados.items():
                tareas.append((nombre, func))
            if incluir_personalizado:
                tareas.append(("Código Personalizado", None))

            total_pasos = len(tamanos) * len(tareas)
            paso_actual = 0

            for tamano in tamanos:
                dataset_base = generar_dataset(tamano, "aleatorio")

                for nombre, funcion in tareas:
                    msg = f"Ejecutando {nombre} (N={tamano})..."
                    self.progress_signal.emit(int((paso_actual / total_pasos) * 100), msg)

                    if nombre not in resultados:
                        resultados[nombre] = []

                    # Preparar dataset específico
                    if "Binaria" in nombre:
                        dataset_actual = sorted(dataset_base)
                    elif any(x in nombre for x in ["Fibonacci", "Recursivo", "Iterativo"]):
                        dataset_actual = tamano
                    else:
                        dataset_actual = dataset_base[:]

                    if funcion is None:  # Código personalizado
                        tiempo = ejecutar_codigo_personalizado(codigo_personalizado, dataset_actual)
                    else:
                        tiempo = medir_tiempo(funcion, dataset_actual)

                    resultados[nombre].append(tiempo)
                    paso_actual += 1

            self.result_signal.emit(resultados, tamanos)

        except Exception as e:
            self.error_signal.emit(str(e) + "\n" + traceback.format_exc())


class AnalizadorGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("🚀 Analizador de Complejidad Algorítmica")
        self.setMinimumSize(1280, 850)
        self.aplicar_estilos()
        self.init_ui()

    def aplicar_estilos(self):
        self.setStyleSheet("""
            QMainWindow { background-color: #0F172A; }
            QWidget { font-family: 'Segoe UI', system-ui, sans-serif; color: #F8FAFC; }

            QFrame#ControlPanel {
                background-color: #1E293B;
                border-radius: 12px;
                border: 1px solid #334155;
            }

            QLabel#Title { font-size: 20px; font-weight: 800; color: #38BDF8; margin-bottom: 10px; }
            QLabel#Sub { color: #94A3B8; font-size: 13px; font-weight: 400; }

            QListWidget {
                background-color: #0F172A;
                border: 1px solid #334155;
                border-radius: 8px;
                padding: 5px;
                outline: none;
            }
            QListWidget::item { padding: 8px; border-radius: 4px; margin: 2px; }
            QListWidget::item:hover { background-color: #1E293B; }
            QListWidget::item:selected { background-color: #38BDF8; color: #0F172A; font-weight: bold; }

            QLineEdit, QTextEdit {
                background-color: #0F172A;
                border: 1px solid #334155;
                border-radius: 8px;
                padding: 10px;
                selection-background-color: #38BDF8;
            }

            QPushButton#ActionBtn {
                background-color: #0EA5E9;
                color: white;
                border-radius: 8px;
                padding: 15px;
                font-size: 14px;
                font-weight: bold;
                text-transform: uppercase;
            }
            QPushButton#ActionBtn:hover { background-color: #0284C7; }
            QPushButton#ActionBtn:pressed { background-color: #075985; }
            QPushButton#ActionBtn:disabled { background-color: #334155; color: #64748B; }

            QTableWidget {
                background-color: #1E293B;
                border: 1px solid #334155;
                border-radius: 8px;
                gridline-color: #334155;
            }
            QHeaderView::section {
                background-color: #334155;
                color: #F8FAFC;
                padding: 10px;
                border: none;
                font-weight: bold;
            }

            QProgressBar {
                border: 1px solid #334155;
                border-radius: 5px;
                text-align: center;
                background-color: #0F172A;
            }
            QProgressBar::chunk { background-color: #38BDF8; border-radius: 4px; }

            /* Estilos para la toolbar de Matplotlib */
            QToolBar {
                background-color: #1E293B;
                border: none;
                border-bottom: 1px solid #334155;
                padding: 4px;
                spacing: 4px;
            }
            QToolBar QToolButton {
                background-color: transparent;
                border: 1px solid transparent;
                border-radius: 6px;
                padding: 4px 6px;
                color: #94A3B8;
            }
            QToolBar QToolButton:hover {
                background-color: #334155;
                border-color: #475569;
                color: #F8FAFC;
            }
            QToolBar QToolButton:pressed {
                background-color: #0EA5E9;
                border-color: #0284C7;
                color: white;
            }
            QToolBar QToolButton:checked {
                background-color: #0EA5E9;
                border-color: #0284C7;
                color: white;
            }
        """)

    def init_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QHBoxLayout(central)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)

        splitter = QSplitter(Qt.Orientation.Horizontal)
        main_layout.addWidget(splitter)

        # --- PANEL IZQUIERDO ---
        left_panel = QFrame()
        left_panel.setObjectName("ControlPanel")
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(20, 20, 20, 20)
        left_layout.setSpacing(15)

        left_layout.addWidget(QLabel("ALGORITMOS", objectName="Title"))
        left_layout.addWidget(QLabel("Selecciona los algoritmos a comparar:", objectName="Sub"))

        self.list_algoritmos = QListWidget()
        for nombre in ALGORITMOS_EJEMPLO.keys():
            item = QListWidgetItem(nombre)
            item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
            item.setCheckState(Qt.CheckState.Unchecked)
            self.list_algoritmos.addItem(item)
        left_layout.addWidget(self.list_algoritmos)

        self.chk_personalizado = QCheckBox(" Incluir Código Personalizado")
        self.chk_personalizado.toggled.connect(self.on_personalizado_toggled)
        left_layout.addWidget(self.chk_personalizado)

        self.editor_codigo = QTextEdit()
        self.editor_codigo.setPlainText(EJEMPLO_CODIGO_PERSONALIZADO)
        self.editor_codigo.setVisible(False)
        left_layout.addWidget(self.editor_codigo)

        left_layout.addWidget(QLabel("CONFIGURACIÓN", objectName="Title"))
        left_layout.addWidget(QLabel("Tamaños de N (ej. 100, 500, 1000):", objectName="Sub"))
        self.input_tamanos = QLineEdit("100, 500, 1000, 2000")
        left_layout.addWidget(self.input_tamanos)

        self.chk_log_scale = QCheckBox(" Usar escala logarítmica")
        left_layout.addWidget(self.chk_log_scale)

        self.btn_analizar = QPushButton("🚀 Ejecutar Análisis")
        self.btn_analizar.setObjectName("ActionBtn")
        self.btn_analizar.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_analizar.clicked.connect(self.ejecutar_analisis)
        left_layout.addWidget(self.btn_analizar)

        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        left_layout.addWidget(self.progress_bar)

        self.lbl_estado = QLabel("Listo para analizar.")
        self.lbl_estado.setObjectName("Sub")
        left_layout.addWidget(self.lbl_estado)

        # --- PANEL DERECHO ---
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(0, 0, 0, 0)

        # Tabla
        self.tabla_resultados = QTableWidget()
        self.tabla_resultados.setAlternatingRowColors(True)
        self.tabla_resultados.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        right_layout.addWidget(self.tabla_resultados, 1)

        # Gráfica
        self.graph_container = QFrame()
        self.graph_container.setObjectName("ControlPanel")
        self.graph_layout = QVBoxLayout(self.graph_container)
        self.graph_layout.setContentsMargins(10, 10, 10, 10)
        self.graph_layout.setSpacing(0)  # toolbar y canvas sin separación
        right_layout.addWidget(self.graph_container, 2)

        splitter.addWidget(left_panel)
        splitter.addWidget(right_panel)
        splitter.setSizes([400, 880])

    def on_personalizado_toggled(self, checked):
        self.editor_codigo.setVisible(checked)

    def ejecutar_analisis(self):
        algos_seleccionados = {}
        for i in range(self.list_algoritmos.count()):
            item = self.list_algoritmos.item(i)
            if item.checkState() == Qt.CheckState.Checked:
                nombre = item.text()
                algos_seleccionados[nombre] = ALGORITMOS_EJEMPLO[nombre]

        if not algos_seleccionados and not self.chk_personalizado.isChecked():
            QMessageBox.warning(self, "Atención", "Selecciona al menos un algoritmo.")
            return

        try:
            tamanos = [int(t.strip()) for t in self.input_tamanos.text().split(',')]
            tamanos.sort()
        except ValueError:
            QMessageBox.critical(self, "Error", "Formato de tamaños inválido.")
            return

        # --- PROTECCIÓN DE SEGURIDAD ---
        if any("Recursivo" in nombre for nombre in algos_seleccionados.keys()):
            if any(t > 35 for t in tamanos):
                msg_box = QMessageBox(self)
                msg_box.setIcon(QMessageBox.Icon.Warning)
                msg_box.setWindowTitle("¡Peligro de Rendimiento!")
                msg_box.setText("Has seleccionado 'Fibonacci Recursivo' con tamaños de N mayores a 35.")
                msg_box.setInformativeText(
                    "Este algoritmo tiene complejidad exponencial O(2ⁿ). Con N=100, tardaría años en terminar.\n\n"
                    "¿Deseas continuar bajo tu propio riesgo o cancelar para ajustar los tamaños a algo menor (ej. 20)?"
                )
                msg_box.setStandardButtons(QMessageBox.StandardButton.Ok | QMessageBox.StandardButton.Cancel)
                msg_box.setDefaultButton(QMessageBox.StandardButton.Cancel)

                if msg_box.exec() == QMessageBox.StandardButton.Cancel:
                    return
        # -------------------------------

        self.btn_analizar.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)

        # Limpiar toolbar y gráfica anterior
        for i in reversed(range(self.graph_layout.count())):
            widget = self.graph_layout.itemAt(i).widget()
            if widget is not None:
                widget.setParent(None)

        config = {
            'algoritmos': algos_seleccionados,
            'incluir_personalizado': self.chk_personalizado.isChecked(),
            'codigo': self.editor_codigo.toPlainText(),
            'tamanos': tamanos
        }

        self.thread = WorkerThread(config)
        self.thread.progress_signal.connect(self.actualizar_progreso)
        self.thread.result_signal.connect(self.mostrar_resultados)
        self.thread.error_signal.connect(self.mostrar_error)
        self.thread.start()

    def actualizar_progreso(self, val, msg):
        self.progress_bar.setValue(val)
        self.lbl_estado.setText(msg)

    def mostrar_resultados(self, resultados, tamanos):
        self.progress_bar.setValue(100)
        self.lbl_estado.setText("Generando visualización...")

        # Configurar Tabla
        columnas = ["Algoritmo"] + [f"N={t}" for t in tamanos] + ["Big O"]
        self.tabla_resultados.setColumnCount(len(columnas))
        self.tabla_resultados.setRowCount(len(resultados))
        self.tabla_resultados.setHorizontalHeaderLabels(columnas)

        for row, (nombre, tiempos) in enumerate(resultados.items()):
            self.tabla_resultados.setItem(row, 0, QTableWidgetItem(nombre))
            for col, t in enumerate(tiempos):
                self.tabla_resultados.setItem(row, col + 1, QTableWidgetItem(f"{t:.6f}s"))

            big_o = estimar_complejidad(tamanos, tiempos)
            item_bo = QTableWidgetItem(big_o)
            item_bo.setForeground(QColor("#38BDF8"))
            item_bo.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
            self.tabla_resultados.setItem(row, len(tamanos) + 1, item_bo)

        # Gráfica con toolbar interactiva
        fig = graficar_resultados(resultados, tamanos, self.chk_log_scale.isChecked(), return_fig=True)

        canvas = FigureCanvasQTAgg(fig)
        canvas.setFocusPolicy(Qt.FocusPolicy.StrongFocus)   # recibe scroll y teclado

        toolbar = NavigationToolbar2QT(canvas, self.graph_container)

        self.graph_layout.addWidget(toolbar)   # toolbar primero (arriba)
        self.graph_layout.addWidget(canvas)    # canvas debajo

        self.btn_analizar.setEnabled(True)
        self.lbl_estado.setText("Análisis finalizado.")

    def mostrar_error(self, err):
        self.btn_analizar.setEnabled(True)
        self.progress_bar.setVisible(False)
        QMessageBox.critical(self, "Error Crítico", err)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    win = AnalizadorGUI()
    win.show()
    sys.exit(app.exec())