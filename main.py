import sys
import csv
from datetime import datetime
from utils import generar_dataset
from algorithms import bubble_sort, quick_sort, merge_sort, insertion_sort, selection_sort, timsort_nativo
from benchmarker import medir_tiempo
from visualizer import graficar_resultados

from rich.console import Console
from rich.prompt import Prompt
from rich.progress import Progress, SpinnerColumn, TimeElapsedColumn
from rich.table import Table
from rich import box

console = Console()

TODOS_LOS_ALGORITMOS = {
    "0": ("Timsort (Nativo Python) (O(n log n))", timsort_nativo),
    "1": ("Bubble Sort (O(n²))", bubble_sort),
    "2": ("Quick Sort (O(n log n))", quick_sort),
    "3": ("Merge Sort (O(n log n))", merge_sort),
    "4": ("Insertion Sort (O(n²))", insertion_sort),
    "5": ("Selection Sort (O(n²))", selection_sort)
}

def main():
    console.print("[bold blue]=================================================[/bold blue]")
    console.print("[bold cyan]Analizador de Complejidad Algorítmica Dinámico[/bold cyan]")
    console.print("[bold blue]=================================================[/bold blue]\n")

    # Selección de algoritmos
    console.print("[bold yellow]Algoritmos Disponibles:[/bold yellow]")
    for clave, (nombre, _) in TODOS_LOS_ALGORITMOS.items():
        console.print(f"  [green]{clave}[/green] - {nombre}")
    
    seleccion = Prompt.ask(
        "\nIngresa los números de los algoritmos a evaluar separados por coma (ej. 1,2,3) o presiona Enter para usar todos",
        default="1,2,3,4,5"
    )
    
    claves_seleccionadas = [s.strip() for s in seleccion.split(',') if s.strip() in TODOS_LOS_ALGORITMOS]
    if not claves_seleccionadas:
        console.print("[bold red]Selección inválida, usando Quick Sort y Bubble Sort por defecto.[/bold red]")
        claves_seleccionadas = ["1", "2"]

    algoritmos = {TODOS_LOS_ALGORITMOS[c][0]: TODOS_LOS_ALGORITMOS[c][1] for c in claves_seleccionadas}
    
    # Selección del tipo de caso
    console.print("\n[bold yellow]Distribución de los Datos (Casos de Prueba):[/bold yellow]")
    console.print("  [green]1[/green] - Aleatorio (Caso Promedio)")
    console.print("  [green]2[/green] - Ordenado (Mejor Caso para algunos)")
    console.print("  [green]3[/green] - Inverso (Peor Caso para algunos)")
    
    seleccion_caso = Prompt.ask("\nSelecciona el tipo de caso (1, 2 o 3)", default="1")
    tipos_caso = {"1": "aleatorio", "2": "ordenado", "3": "inverso"}
    caso_actual = tipos_caso.get(seleccion_caso.strip(), "aleatorio")

    # Selección de tamaños
    tamanos_input = Prompt.ask(
        "\nIngresa los tamaños de los arreglos a evaluar separados por coma",
        default="100, 500, 1000, 2000"
    )
    
    # Preguntar por Escala Logarítmica
    usar_escala_log_str = Prompt.ask(
        "\n¿Deseas usar escala logarítmica en la gráfica para ver mejor los algoritmos rápidos? (s/n)",
        default="n"
    )
    usar_escala_log = usar_escala_log_str.strip().lower() == 's'
    
    try:
        tamanos = [int(t.strip()) for t in tamanos_input.split(',')]
        tamanos.sort()
    except ValueError:
        console.print("[bold red]Entrada inválida. Usando tamaños por defecto.[/bold red]")
        tamanos = [100, 500, 1000, 2000]

    resultados = {nombre: [] for nombre in algoritmos}
    
    console.print("\n[bold magenta]Iniciando Análisis de Rendimiento...[/bold magenta]\n")
    
    total_pasos = len(tamanos) * len(algoritmos)
    
    # Progreso de ejecución
    with Progress(
        SpinnerColumn(),
        *Progress.get_default_columns(),
        TimeElapsedColumn(),
        console=console
    ) as progress:
        task = progress.add_task("[cyan]Ejecutando pruebas...", total=total_pasos)
        
        for tamano in tamanos:
            progress.console.print(f"[dim]Generando dataset ({caso_actual}) de tamaño {tamano}...[/dim]")
            dataset = generar_dataset(tamano, caso_actual)
            
            for nombre, funcion in algoritmos.items():
                tiempo = medir_tiempo(funcion, dataset)
                resultados[nombre].append(tiempo)
                progress.advance(task)

    # Construir tabla de resultados
    console.print("\n[bold green]Pruebas finalizadas con éxito![/bold green]")
    
    tabla = Table(title="Resultados de Tiempos de Ejecución (segundos)", box=box.ROUNDED)
    tabla.add_column("Algoritmo", style="cyan", no_wrap=True)
    for tamano in tamanos:
        tabla.add_column(f"N={tamano}", justify="right")
        
    for nombre, tiempos in resultados.items():
        fila = [nombre] + [f"{t:.6f}" for t in tiempos]
        tabla.add_row(*fila)
        
    console.print(tabla)
    
    # Exportar a CSV
    nombre_archivo_csv = f"resultados_{caso_actual}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    try:
        with open(nombre_archivo_csv, mode='w', newline='') as file:
            writer = csv.writer(file)
            encabezados = ["Algoritmo"] + [f"N={t}" for t in tamanos]
            writer.writerow(encabezados)
            for nombre, tiempos in resultados.items():
                fila = [nombre] + [f"{t:.6f}" for t in tiempos]
                writer.writerow(fila)
        console.print(f"[bold green][+] Resultados exportados a CSV: {nombre_archivo_csv}[/bold green]")
    except Exception as e:
        console.print(f"[bold red]Error al guardar CSV: {e}[/bold red]")

    console.print("\n[bold cyan]Generando gráfico comparativo...[/bold cyan]")
    graficar_resultados(resultados, tamanos, escala_logaritmica=usar_escala_log)

if __name__ == "__main__":
    try:
        main()
        Prompt.ask("\n[bold yellow]Presiona Enter para salir y cerrar el gráfico...[/bold yellow]")
    except KeyboardInterrupt:
        console.print("\n[bold red]Ejecución cancelada por el usuario.[/bold red]")
        sys.exit(0)
