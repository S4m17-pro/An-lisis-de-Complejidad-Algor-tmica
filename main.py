import sys
import subprocess

def verificar_dependencias():
    try:
        import matplotlib
        import numpy
        import rich
        import PyQt6
    except ImportError as e:
        print(f"\n[!] Error: Faltan dependencias críticas ({e.name}).")
        print("[!] Por favor, instala los requisitos usando: pip install -r requirements.txt")
        sys.exit(1)

verificar_dependencias()

from utils import generar_dataset
import algorithms
from benchmarker import medir_tiempo, ejecutar_codigo_personalizado
from visualizer import graficar_resultados
from complexity_detector import estimar_complejidad

from rich.console import Console
from rich.prompt import Prompt
from rich.progress import Progress, SpinnerColumn, TimeElapsedColumn, TextColumn
from rich.table import Table
from rich import box
from rich.panel import Panel
from rich.align import Align

console = Console()

ALGORITMOS_ORDENAMIENTO = {
    "1": ("Bubble Sort (O(n^2))", algorithms.bubble_sort),
    "2": ("Quick Sort (O(n log n))", algorithms.quick_sort),
    "3": ("Merge Sort (O(n log n))", algorithms.merge_sort),
    "4": ("Insertion Sort (O(n^2))", algorithms.insertion_sort),
    "5": ("Selection Sort (O(n^2))", algorithms.selection_sort),
    "6": ("Timsort (Nativo) (O(n log n))", algorithms.timsort_nativo),
}

ALGORITMOS_BUSQUEDA = {
    "7": ("Busqueda Lineal (O(n))", algorithms.busqueda_lineal),
    "8": ("Busqueda Binaria (O(log n))", algorithms.busqueda_binaria),
}

ALGORITMOS_ESPECIALES = {
    "9": ("Fibonacci Recursivo (O(2^n))", algorithms.fibonacci_recursivo),
    "10": ("Fibonacci Iterativo (O(n))", algorithms.fibonacci_iterativo),
}

TODOS_LOS_ALGORITMOS = {**ALGORITMOS_ORDENAMIENTO, **ALGORITMOS_BUSQUEDA, **ALGORITMOS_ESPECIALES}

def mostrar_cabecera():
    console.print(Panel(
        Align.center(
            "[bold cyan]*** ANALIZADOR DE COMPLEJIDAD ALGORÍTMICA ***[/bold cyan]\n"
            "[dim]Matemáticas Discretas - Proyecto Profesional[/dim]"
        ),
        border_style="bright_blue",
        box=box.DOUBLE_EDGE
    ))

def mostrar_menu():
    mostrar_cabecera()
    
    table = Table(show_header=True, header_style="bold magenta", box=box.ROUNDED, expand=True)
    table.add_column("ID", style="bold white", width=4)
    table.add_column("Categoria / Algoritmo", style="cyan")
    table.add_column("Complejidad Teorica", style="dim yellow")

    def agregar_grupo(titulo, grupo):
        table.add_section()
        table.add_row("", f"[bold yellow]{titulo.upper()}[/bold yellow]", "")
        for k, v in grupo.items():
            nombre = v[0].split(' (')[0]
            complejidad = v[0].split(' (')[1].replace(')', '') if '(' in v[0] else "N/A"
            table.add_row(k, nombre, complejidad)

    agregar_grupo("Ordenamiento", ALGORITMOS_ORDENAMIENTO)
    agregar_grupo("Búsqueda", ALGORITMOS_BUSQUEDA)
    agregar_grupo("Especiales", ALGORITMOS_ESPECIALES)
    
    table.add_section()
    table.add_row("C", "[bold green]Código Personalizado[/bold green]", "Variable")
    table.add_row("G", "[bold magenta]Lanzar Interfaz Gráfica (GUI)[/bold magenta]", "N/A")
    
    console.print(table)

def lanzar_gui():
    console.print("\n[bold cyan][GUI] Iniciando Interfaz Gráfica...[/bold cyan]")
    try:
        subprocess.Popen([sys.executable, "gui.py"])
    except Exception as e:
        console.print(f"[bold red]Error al lanzar la GUI: {e}[/bold red]")

def main():
    while True:
        console.clear()
        mostrar_menu()
        
        seleccion = Prompt.ask(
            "\nSelecciona los números (ej. 1,2,8), 'C' para código propio, 'G' para GUI o 'S' para salir",
            default="2,3,6"
        ).upper()
        
        if seleccion == 'S':
            break
        if seleccion == 'G':
            lanzar_gui()
            continue

        es_personalizado = 'C' in seleccion
        algoritmos_a_evaluar = {}
        codigo_usuario = ""

        if es_personalizado:
            console.print("\n[bold yellow]📝 Ingresa tu código Python (usa 'n' para el tamaño o 'data' para la lista):[/bold yellow]")
            console.print("[dim]Ejemplo: for i in range(n): pass[/dim]")
            codigo_usuario = Prompt.ask("Código")
            algoritmos_a_evaluar["Código Usuario"] = lambda d: ejecutar_codigo_personalizado(codigo_usuario, d)
        else:
            claves = [s.strip() for s in seleccion.split(',') if s.strip() in TODOS_LOS_ALGORITMOS]
            if not claves:
                console.print("[bold red]Selección inválida.[/bold red]")
                Prompt.ask("Presiona Enter para continuar...")
                continue
            algoritmos_a_evaluar = {TODOS_LOS_ALGORITMOS[c][0]: TODOS_LOS_ALGORITMOS[c][1] for c in claves}

        # Configuración de tamaños
        default_sizes = "10, 20, 25" if any(k in seleccion for k in ["9"]) else "100, 500, 1000, 2000"
        tamanos_input = Prompt.ask(f"\nTamaños de entrada (N)", default=default_sizes)
        
        try:
            tamanos = [int(t.strip()) for t in tamanos_input.split(',')]
            tamanos.sort()
        except ValueError:
            console.print("[bold red]Entrada de tamaños inválida.[/bold red]")
            Prompt.ask("Presiona Enter para continuar...")
            continue

        usar_escala_log = Prompt.ask("\n¿Usar escala logarítmica en la gráfica? (s/n)", default="n").lower() == 's'
        
        # Ejecución
        resultados = {nombre: [] for nombre in algoritmos_a_evaluar}
        console.print("\n[bold magenta][PROCESS] Iniciando Benchmarking...[/bold magenta]\n")
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            *Progress.get_default_columns(),
            TimeElapsedColumn(),
            console=console
        ) as progress:
            total_work = len(tamanos) * len(algoritmos_a_evaluar)
            task = progress.add_task("[cyan]Analizando algoritmos...", total=total_work)
            
            for tamano in tamanos:
                # Generamos un dataset base para este tamaño
                dataset_base = generar_dataset(tamano, "aleatorio")

                for nombre, funcion in algoritmos_a_evaluar.items():
                    # Preparar el dataset específico para el algoritmo
                    # IMPORTANTE: No ordenar el dataset base para no afectar a otros algoritmos
                    if "Binaria" in nombre:
                        dataset_actual = sorted(dataset_base)
                    elif any(x in nombre for x in ["Fibonacci", "Recursivo", "Iterativo"]):
                        dataset_actual = tamano # Estos algoritmos esperan N, no una lista
                    else:
                        dataset_actual = dataset_base[:] # Copia superficial para seguridad
                    
                    tiempo = medir_tiempo(funcion, dataset_actual)
                    resultados[nombre].append(tiempo)
                    progress.advance(task)

        # Resultados y Detección de Big O
        tabla = Table(title="[bold cyan]Resultados de Rendimiento y Estimación Big O[/bold cyan]", 
                      box=box.DOUBLE_EDGE, header_style="bold magenta")
        tabla.add_column("Algoritmo", style="cyan", no_wrap=True)
        for tamano in tamanos:
            tabla.add_column(f"N={tamano}", justify="right")
        tabla.add_column("Big O Estimado", style="bold yellow", justify="center")
            
        for nombre, tiempos in resultados.items():
            big_o = estimar_complejidad(tamanos, tiempos)
            fila = [nombre] + [f"{t:.6f}s" for t in tiempos] + [f"[bold yellow]{big_o}[/bold yellow]"]
            tabla.add_row(*fila)
            
        console.print(tabla)
        
        # Gráfico
        graficar_resultados(resultados, tamanos, escala_logaritmica=usar_escala_log)
        
        Prompt.ask("\n[bold green]Análisis finalizado.[/bold green] Presiona Enter para volver al menú...")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        console.print("\n[bold red]Programa finalizado por el usuario.[/bold red]")
        sys.exit(0)
