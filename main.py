import sys
from utils import generar_dataset
from algorithms import bubble_sort, quick_sort, merge_sort, insertion_sort, selection_sort
from benchmarker import medir_tiempo
from visualizer import graficar_resultados

from rich.console import Console
from rich.prompt import Prompt
from rich.progress import Progress, SpinnerColumn, TimeElapsedColumn
from rich.table import Table
from rich import box

console = Console()

TODOS_LOS_ALGORITMOS = {
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
    
    # Selección de tamaños
    tamanos_input = Prompt.ask(
        "\nIngresa los tamaños de los arreglos a evaluar separados por coma",
        default="100, 500, 1000, 2000"
    )
    
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
            progress.console.print(f"[dim]Generando dataset de tamaño {tamano}...[/dim]")
            dataset = generar_dataset(tamano)
            
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
    
    console.print("\n[bold cyan]Generando gráfico comparativo...[/bold cyan]")
    graficar_resultados(resultados, tamanos)

if __name__ == "__main__":
    try:
        main()
        Prompt.ask("\n[bold yellow]Presiona Enter para salir y cerrar el gráfico...[/bold yellow]")
    except KeyboardInterrupt:
        console.print("\n[bold red]Ejecución cancelada por el usuario.[/bold red]")
        sys.exit(0)
