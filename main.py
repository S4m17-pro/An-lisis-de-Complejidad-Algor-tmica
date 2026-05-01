import sys
from utils import generar_dataset
import algorithms
from benchmarker import medir_tiempo, ejecutar_codigo_personalizado
from visualizer import graficar_resultados
from complexity_detector import estimar_complejidad

from rich.console import Console
from rich.prompt import Prompt
from rich.progress import Progress, SpinnerColumn, TimeElapsedColumn
from rich.table import Table
from rich import box
from rich.panel import Panel

console = Console()

ALGORITMOS_ORDENAMIENTO = {
    "1": ("Bubble Sort (O(n²))", algorithms.bubble_sort),
    "2": ("Quick Sort (O(n log n))", algorithms.quick_sort),
    "3": ("Merge Sort (O(n log n))", algorithms.merge_sort),
    "4": ("Insertion Sort (O(n²))", algorithms.insertion_sort),
    "5": ("Selection Sort (O(n²))", algorithms.selection_sort),
    "6": ("Timsort (Nativo) (O(n log n))", algorithms.timsort_nativo),
}

ALGORITMOS_BUSQUEDA = {
    "7": ("Búsqueda Lineal (O(n))", algorithms.busqueda_lineal),
    "8": ("Búsqueda Binaria (O(log n))", algorithms.busqueda_binaria),
}

ALGORITMOS_ESPECIALES = {
    "9": ("Fibonacci Recursivo (O(2ⁿ))", algorithms.fibonacci_recursivo),
    "10": ("Fibonacci Iterativo (O(n))", algorithms.fibonacci_iterativo),
}

TODOS_LOS_ALGORITMOS = {**ALGORITMOS_ORDENAMIENTO, **ALGORITMOS_BUSQUEDA, **ALGORITMOS_ESPECIALES}

def mostrar_menu():
    console.print(Panel.fit(
        "[bold cyan] Analizador de Complejidad Algorítmica [/bold cyan]\n"
        "[dim]Detecta el Big O de tu código y compara algoritmos clásicos[/dim]",
        border_style="blue", box=box.DOUBLE
    ))

    table = Table(show_header=False, box=box.SIMPLE)
    table.add_column("Cat", style="yellow")
    table.add_column("Algs", style="green")

    def format_group(group):
        return "\n".join([f"[bold white]{k}[/bold white] - {v[0]}" for k, v in group.items()])

    table.add_row("Ordenamiento", format_group(ALGORITMOS_ORDENAMIENTO))
    table.add_row("Búsqueda", format_group(ALGORITMOS_BUSQUEDA))
    table.add_row("Especiales", format_group(ALGORITMOS_ESPECIALES))
    table.add_row("Personalizado", "[bold white]C[/bold white] - Ingresar mi propio código Python")
    
    console.print(table)

def main():
    mostrar_menu()
    
    seleccion = Prompt.ask(
        "\nSelecciona los números (ej. 1,2,8) o 'C' para código propio",
        default="2,3,6"
    ).upper()
    
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
            return
        algoritmos_a_evaluar = {TODOS_LOS_ALGORITMOS[c][0]: TODOS_LOS_ALGORITMOS[c][1] for c in claves}

    # Configuración de tamaños
    default_sizes = "10, 20, 25" if "9" in seleccion else "100, 500, 1000, 2000"
    tamanos_input = Prompt.ask(f"\nTamaños de entrada (N)", default=default_sizes)
    
    try:
        tamanos = [int(t.strip()) for t in tamanos_input.split(',')]
        tamanos.sort()
    except ValueError:
        console.print("[bold red]Entrada inválida.[/bold red]")
        return

    usar_escala_log = Prompt.ask("\n¿Usar escala logarítmica? (s/n)", default="n").lower() == 's'
    
    # Ejecución
    resultados = {nombre: [] for nombre in algoritmos_a_evaluar}
    console.print("\n[bold magenta]Iniciando Análisis...[/bold magenta]\n")
    
    with Progress(SpinnerColumn(), *Progress.get_default_columns(), TimeElapsedColumn(), console=console) as progress:
        task = progress.add_task("[cyan]Procesando...", total=len(tamanos) * len(algoritmos_a_evaluar))
        
        for tamano in tamanos:
            dataset = generar_dataset(tamano, "aleatorio")
            if any(k in seleccion for k in ["8"]): dataset.sort() # Búsqueda binaria requiere orden

            for nombre, funcion in algoritmos_a_evaluar.items():
                tiempo = medir_tiempo(funcion, dataset)
                resultados[nombre].append(tiempo)
                progress.advance(task)

    # Resultados y Detección de Big O
    tabla = Table(title="Resultados y Estimación de Complejidad", box=box.ROUNDED)
    tabla.add_column("Algoritmo", style="cyan")
    for tamano in tamanos:
        tabla.add_column(f"N={tamano}")
    tabla.add_column("Big O Estimado", style="bold yellow")
        
    for nombre, tiempos in resultados.items():
        big_o = estimar_complejidad(tamanos, tiempos)
        fila = [nombre] + [f"{t:.6f}s" for t in tiempos] + [big_o]
        tabla.add_row(*fila)
        
    console.print(tabla)
    
    # Gráfico
    graficar_resultados(resultados, tamanos, escala_logaritmica=usar_escala_log)

if __name__ == "__main__":
    try:
        main()
        Prompt.ask("\n[bold yellow]Presiona Enter para finalizar...[/bold yellow]")
    except KeyboardInterrupt:
        console.print("\n[bold red]Cancelado.[/bold red]")
        sys.exit(0)
