import time

def medir_tiempo(algoritmo, dataset):
    """
    Mide el tiempo de ejecución de una función (algoritmo) sobre un dataset.
    Retorna el tiempo en segundos.
    """
    inicio = time.perf_counter()
    algoritmo(dataset)
    fin = time.perf_counter()
    return fin - inicio
