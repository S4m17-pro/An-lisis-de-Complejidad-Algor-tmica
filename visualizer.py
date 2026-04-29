import matplotlib
matplotlib.use('QtAgg') # Usar PyQt6 para mostrar el panel interactivo directamente
import matplotlib.pyplot as plt
import seaborn as sns

def graficar_resultados(resultados, tamanos, escala_logaritmica=False, archivo_salida="complejidad.png"):
    # Configurar estilo Seaborn
    sns.set_theme(style="darkgrid")
    
    plt.figure(figsize=(12, 7))
    
    # Paleta de colores atractiva
    colores = sns.color_palette("husl", len(resultados))
    estilos = ['o-', 's-', '^-', 'd-', 'x-', 'P-']
    
    i = 0
    for nombre_algoritmo, tiempos in resultados.items():
        marcador = estilos[i % len(estilos)]
        color = colores[i]
        plt.plot(tamanos, tiempos, marcador, color=color, label=nombre_algoritmo, linewidth=2.5, markersize=8)
        i += 1

    # Aplicar escala logarítmica si el usuario lo pide
    if escala_logaritmica:
        plt.yscale('log')
        plt.ylabel('Tiempo de Ejecución (segundos) - Escala Log', fontsize=14, labelpad=10)
    else:
        plt.ylabel('Tiempo de Ejecución (segundos)', fontsize=14, labelpad=10)

    plt.title('Análisis Comparativo de Complejidad Algorítmica', fontsize=18, fontweight='bold', pad=20)
    plt.xlabel('Tamaño de la Entrada (N elementos)', fontsize=14, labelpad=10)
    plt.xticks(fontsize=12)
    plt.yticks(fontsize=12)
    
    plt.legend(fontsize=12, loc='upper left', frameon=True, shadow=True, borderpad=1)

    plt.tight_layout()
    plt.savefig(archivo_salida, dpi=300)
    plt.show(block=False) # Mostrar panel interactivo
    print(f"\n[+] Gráfico guardado exitosamente como '{archivo_salida}'.")
