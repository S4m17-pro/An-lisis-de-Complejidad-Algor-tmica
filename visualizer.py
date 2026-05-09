import matplotlib
import matplotlib.pyplot as plt
import seaborn as sns
import sys

# Intentar usar un backend interactivo, pero caer con gracia si falla
try:
    # Preferimos QtAgg para la integración con la GUI, pero permitimos otros
    if not matplotlib.get_backend().startswith('module://'):
        matplotlib.use('QtAgg')
except Exception:
    try:
        matplotlib.use('TkAgg')
    except Exception:
        matplotlib.use('Agg') # Backend no interactivo (solo para guardar archivos)

try:
    from rich.console import Console
    console = Console()
except ImportError:
    console = None

def graficar_resultados(resultados, tamanos, escala_logaritmica=False, archivo_salida="complejidad.png", return_fig=False):
    """
    Genera una gráfica comparativa de los tiempos de ejecución.
    """
    # Configurar estilo Seaborn para un look profesional
    sns.set_theme(style="darkgrid", palette="viridis")
    
    # Crear figura y ejes usando la API orientada a objetos
    fig, ax = plt.subplots(figsize=(12, 7))
    
    # Paleta de colores y estilos de línea
    colores = sns.color_palette("husl", len(resultados))
    estilos = ['o-', 's-', '^-', 'd-', 'x-', 'P-', '*-']
    
    for i, (nombre_algoritmo, tiempos) in enumerate(resultados.items()):
        marcador = estilos[i % len(estilos)]
        color = colores[i]
        ax.plot(tamanos, tiempos, marcador, color=color, label=nombre_algoritmo, 
                linewidth=2.5, markersize=8, alpha=0.85)

    # Configuración de escalas y etiquetas
    if escala_logaritmica:
        ax.set_yscale('log')
        ax.set_ylabel('Tiempo de Ejecución (segundos) [Escala Log]', fontsize=13, fontweight='bold')
    else:
        ax.set_ylabel('Tiempo de Ejecución (segundos)', fontsize=13, fontweight='bold')

    ax.set_title('Análisis Comparativo de Complejidad Algorítmica', fontsize=16, fontweight='bold', pad=20)
    ax.set_xlabel('Tamaño de la Entrada (N elementos)', fontsize=13, fontweight='bold')
    
    ax.tick_params(axis='both', which='major', labelsize=11)
    ax.legend(fontsize=11, loc='upper left', frameon=True, shadow=True, borderpad=1)
    
    fig.tight_layout()
    
    if return_fig:
        return fig
        
    try:
        plt.savefig(archivo_salida, dpi=300, bbox_inches='tight')
        msg = f"[bold green][OK][/bold green] Gráfico guardado exitosamente como [bold cyan]{archivo_salida}[/bold cyan]."
        if console:
            console.print(f"\n{msg}")
        else:
            print(f"\n{msg.replace('[bold green]', '').replace('[/bold green]', '').replace('[bold cyan]', '').replace('[/bold cyan]', '')}")
            
        # Solo intentamos mostrar si no estamos en un backend no interactivo
        if matplotlib.get_backend() != 'Agg':
            plt.show(block=False)
            plt.pause(0.1) # Pequeña pausa para asegurar que se renderice
    except Exception as e:
        error_msg = f"[bold red][X][/bold red] Error al guardar/mostrar el gráfico: {e}"
        if console:
            console.print(f"\n{error_msg}")
        else:
            print(f"\n{error_msg}")
