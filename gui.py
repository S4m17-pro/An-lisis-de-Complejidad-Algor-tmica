import sys
import traceback
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QComboBox, QTextEdit, QLineEdit, QCheckBox, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QSplitter, QMessageBox,
    QFrame
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QFont, QColor, QPalette

import matplotlib
matplotlib.use('QtAgg')
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg

# Importar lógica del proyecto
from utils import generar_dataset
import algorithms
from benchmarker import medir_tiempo, ejecutar_codigo_personalizado
from complexity_detector import estimar_complejidad
from visualizer import graficar_resultados

# Mapeo de algoritmos para el ComboBox
ALGORITMOS_EJEMPLO = {
    "Código Personalizado": None,
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

EJEMPLO_CODIGO_PERSONALIZADO = """# Ingresa tu código aquí
# Usa 'data' para acceder al arreglo generado
# o 'n' para el tamaño del arreglo.

# Ejemplo (Bucle simple):
for i in range(n):
    pass
"""

class WorkerThread(QThread):
    # Señales para comunicar progreso y resultados al hilo principal
    progress_signal = pyqtSignal(str)
    result_signal = pyqtSignal(object, list) # resultados dict, tamanos list
    error_signal = pyqtSignal(str)

    def __init__(self, config):
        super().__init__()
        self.config = config

    def run(self):
        try:
            nombre_algoritmo = self.config['nombre']
            funcion_algoritmo = self.config['funcion']
            codigo_personalizado = self.config['codigo']
            tamanos = self.config['tamanos']

            resultados = {nombre_algoritmo: []}
            
            for tamano in tamanos:
                self.progress_signal.emit(f"Procesando N={tamano}...")
                dataset = generar_dataset(tamano, "aleatorio")
                
                # Para búsqueda binaria necesitamos orden
                if "Binaria" in nombre_algoritmo:
                    dataset.sort()

                if funcion_algoritmo is None:
                    # Código personalizado
                    tiempo = ejecutar_codigo_personalizado(codigo_personalizado, dataset)
                else:
                    # Algoritmo clásico
                    tiempo = medir_tiempo(funcion_algoritmo, dataset)
                
                resultados[nombre_algoritmo].append(tiempo)

            self.result_signal.emit(resultados, tamanos)

        except Exception as e:
            error_trace = traceback.format_exc()
            self.error_signal.emit(f"Error durante la ejecución:\n{str(e)}\n\nTraceback:\n{error_trace}")


class AnalizadorGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Analizador de Complejidad Algorítmica")
        self.resize(1200, 800)
        self.aplicar_estilos()
        self.init_ui()

    def aplicar_estilos(self):
        # Estilo oscuro brutalista/moderno
        self.setStyleSheet("""
            QMainWindow {
                background-color: #121212;
            }
            QWidget {
                font-family: 'Inter', 'Segoe UI', sans-serif;
                color: #E0E0E0;
            }
            QLabel {
                font-size: 14px;
                font-weight: bold;
                color: #FFFFFF;
                margin-bottom: 5px;
            }
            QComboBox, QLineEdit, QTextEdit {
                background-color: #1E1E1E;
                border: 2px solid #333333;
                border-radius: 6px;
                padding: 8px;
                font-size: 14px;
                color: #FFFFFF;
            }
            QComboBox::drop-down {
                border: none;
            }
            QComboBox QAbstractItemView {
                background-color: #1E1E1E;
                color: #FFFFFF;
                selection-background-color: #2D5DA1;
            }
            QTextEdit {
                font-family: 'Consolas', 'Courier New', monospace;
            }
            QLineEdit:focus, QTextEdit:focus, QComboBox:focus {
                border: 2px solid #4A90E2;
            }
            QPushButton {
                background-color: #4A90E2;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 12px 20px;
                font-size: 15px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #357ABD;
            }
            QPushButton:disabled {
                background-color: #555555;
                color: #888888;
            }
            QTableWidget {
                background-color: #1E1E1E;
                alternate-background-color: #252525;
                gridline-color: #333333;
                border: 1px solid #333333;
                border-radius: 6px;
                color: #FFFFFF;
                font-size: 13px;
            }
            QHeaderView::section {
                background-color: #2D2D2D;
                color: white;
                padding: 6px;
                border: 1px solid #333333;
                font-weight: bold;
            }
            QCheckBox {
                font-size: 14px;
            }
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
                border: 2px solid #555;
                border-radius: 4px;
                background-color: #1E1E1E;
            }
            QCheckBox::indicator:checked {
                background-color: #4A90E2;
                border: 2px solid #4A90E2;
            }
        """)

    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)

        # Usar un Splitter para permitir ajustar el ancho de los paneles
        splitter = QSplitter(Qt.Orientation.Horizontal)
        main_layout.addWidget(splitter)

        # ================= PANEL IZQUIERDO (CONTROLES) =================
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(15)

        # Título
        title_lbl = QLabel("CONFIGURACIÓN DE ANÁLISIS")
        title_lbl.setStyleSheet("font-size: 18px; color: #4A90E2; margin-bottom: 10px;")
        left_layout.addWidget(title_lbl)

        # Selección de Algoritmo
        left_layout.addWidget(QLabel("Selecciona un Algoritmo o Código Personalizado:"))
        self.combo_algoritmos = QComboBox()
        self.combo_algoritmos.addItems(list(ALGORITMOS_EJEMPLO.keys()))
        self.combo_algoritmos.currentIndexChanged.connect(self.on_algoritmo_changed)
        left_layout.addWidget(self.combo_algoritmos)

        # Editor de Código
        self.lbl_codigo = QLabel("Código Python:")
        left_layout.addWidget(self.lbl_codigo)
        self.editor_codigo = QTextEdit()
        self.editor_codigo.setPlainText(EJEMPLO_CODIGO_PERSONALIZADO)
        left_layout.addWidget(self.editor_codigo)

        # Tamaños de N
        left_layout.addWidget(QLabel("Tamaños de Entrada N (separados por coma):"))
        self.input_tamanos = QLineEdit()
        self.input_tamanos.setText("100, 500, 1000, 2000")
        left_layout.addWidget(self.input_tamanos)

        # Opciones
        self.chk_log_scale = QCheckBox(" Usar Escala Logarítmica en Gráfica")
        left_layout.addWidget(self.chk_log_scale)

        # Botón Analizar
        self.btn_analizar = QPushButton("🚀 ANALIZAR COMPLEJIDAD")
        self.btn_analizar.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_analizar.clicked.connect(self.ejecutar_analisis)
        left_layout.addWidget(self.btn_analizar)
        
        # Etiqueta de estado
        self.lbl_estado = QLabel("")
        self.lbl_estado.setStyleSheet("color: #AAAAAA; font-weight: normal; font-size: 12px;")
        left_layout.addWidget(self.lbl_estado)

        # ================= PANEL DERECHO (RESULTADOS) =================
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(15)

        # Tabla de resultados
        right_layout.addWidget(QLabel("RESULTADOS DE EJECUCIÓN"))
        self.tabla_resultados = QTableWidget(0, 0)
        self.tabla_resultados.setAlternatingRowColors(True)
        self.tabla_resultados.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        right_layout.addWidget(self.tabla_resultados)

        # Contenedor para la gráfica
        right_layout.addWidget(QLabel("GRÁFICA DE COMPLEJIDAD"))
        self.graph_container = QWidget()
        self.graph_layout = QVBoxLayout(self.graph_container)
        self.graph_layout.setContentsMargins(0, 0, 0, 0)
        self.graph_container.setStyleSheet("background-color: #1E1E1E; border: 1px solid #333333; border-radius: 6px;")
        
        # Le damos un tamaño mínimo para que se vea bien
        self.graph_container.setMinimumHeight(400)
        right_layout.addWidget(self.graph_container)

        # Agregar paneles al splitter
        splitter.addWidget(left_panel)
        splitter.addWidget(right_panel)
        # Establecer proporciones iniciales (30% izq, 70% der)
        splitter.setSizes([350, 850])

    def on_algoritmo_changed(self):
        # Si no es código personalizado, deshabilitar el editor
        seleccion = self.combo_algoritmos.currentText()
        if seleccion == "Código Personalizado":
            self.editor_codigo.setEnabled(True)
            self.editor_codigo.setStyleSheet("background-color: #1E1E1E; color: #FFFFFF;")
            self.input_tamanos.setText("100, 500, 1000, 2000")
        else:
            self.editor_codigo.setEnabled(False)
            self.editor_codigo.setStyleSheet("background-color: #2A2A2A; color: #888888;")
            # Si es fibonacci, bajar los tamaños por defecto
            if "Fibonacci" in seleccion:
                self.input_tamanos.setText("10, 20, 25")
            else:
                self.input_tamanos.setText("100, 500, 1000, 2000")

    def ejecutar_analisis(self):
        # Validar tamaños
        tamanos_txt = self.input_tamanos.text()
        try:
            tamanos = [int(t.strip()) for t in tamanos_txt.split(',')]
            tamanos.sort()
            if not tamanos or any(t <= 0 for t in tamanos):
                raise ValueError()
        except ValueError:
            QMessageBox.warning(self, "Error", "Por favor ingresa tamaños válidos (números enteros positivos separados por comas).")
            return

        nombre_algoritmo = self.combo_algoritmos.currentText()
        funcion_algoritmo = ALGORITMOS_EJEMPLO[nombre_algoritmo]
        codigo_personalizado = self.editor_codigo.toPlainText()

        if funcion_algoritmo is None and not codigo_personalizado.strip():
            QMessageBox.warning(self, "Error", "El código personalizado no puede estar vacío.")
            return

        # Preparar UI para ejecución
        self.btn_analizar.setEnabled(False)
        self.lbl_estado.setText("Ejecutando análisis...")
        self.tabla_resultados.clear()
        self.tabla_resultados.setRowCount(0)
        self.tabla_resultados.setColumnCount(0)
        
        # Limpiar gráfica anterior
        for i in reversed(range(self.graph_layout.count())): 
            widget = self.graph_layout.itemAt(i).widget()
            if widget is not None:
                widget.setParent(None)

        config = {
            'nombre': nombre_algoritmo,
            'funcion': funcion_algoritmo,
            'codigo': codigo_personalizado,
            'tamanos': tamanos
        }

        self.thread = WorkerThread(config)
        self.thread.progress_signal.connect(self.actualizar_progreso)
        self.thread.result_signal.connect(self.mostrar_resultados)
        self.thread.error_signal.connect(self.mostrar_error)
        self.thread.start()

    def actualizar_progreso(self, msg):
        self.lbl_estado.setText(msg)

    def mostrar_resultados(self, resultados, tamanos):
        self.lbl_estado.setText("Análisis completado. Generando gráfica...")
        
        nombre_algoritmo = list(resultados.keys())[0]
        tiempos = resultados[nombre_algoritmo]
        
        # Estimar Big O
        big_o = estimar_complejidad(tamanos, tiempos)

        # Configurar Tabla
        columnas = ["Algoritmo"] + [f"N={t}" for t in tamanos] + ["Big O Estimado"]
        self.tabla_resultados.setColumnCount(len(columnas))
        self.tabla_resultados.setHorizontalHeaderLabels(columnas)
        self.tabla_resultados.setRowCount(1)

        self.tabla_resultados.setItem(0, 0, QTableWidgetItem(nombre_algoritmo))
        for idx, t in enumerate(tiempos):
            self.tabla_resultados.setItem(0, idx + 1, QTableWidgetItem(f"{t:.6f}s"))
        
        item_big_o = QTableWidgetItem(big_o)
        item_big_o.setForeground(QColor("#F5A623")) # Naranja para destacar
        # Hacer la fuente bold
        font = item_big_o.font()
        font.setBold(True)
        item_big_o.setFont(font)
        
        self.tabla_resultados.setItem(0, len(tamanos) + 1, item_big_o)

        # Generar Gráfica
        escala_log = self.chk_log_scale.isChecked()
        
        try:
            fig = graficar_resultados(resultados, tamanos, escala_logaritmica=escala_log, return_fig=True)
            canvas = FigureCanvasQTAgg(fig)
            self.graph_layout.addWidget(canvas)
        except Exception as e:
            self.mostrar_error(f"Error al generar la gráfica: {str(e)}")

        self.lbl_estado.setText("Listo.")
        self.btn_analizar.setEnabled(True)

    def mostrar_error(self, error_msg):
        self.lbl_estado.setText("Error en la ejecución.")
        self.btn_analizar.setEnabled(True)
        QMessageBox.critical(self, "Error de Ejecución", error_msg)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Aplicar un estilo base oscuro
    app.setStyle("Fusion")
    
    window = AnalizadorGUI()
    window.show()
    sys.exit(app.exec())
