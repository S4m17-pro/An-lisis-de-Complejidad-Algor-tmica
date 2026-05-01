import time

def medir_tiempo(algoritmo, dataset, repeticiones=3):
    """
    Mide el tiempo de ejecución de una función (algoritmo) sobre un dataset.
    Promedia 'repeticiones' ejecuciones para mayor estabilidad.
    """
    tiempos = []
    for _ in range(repeticiones):
        # Copiamos el dataset si es una lista para evitar efectos secundarios en algoritmos in-place
        data_copy = dataset[:] if isinstance(dataset, list) else dataset
        
        inicio = time.perf_counter()
        algoritmo(data_copy)
        fin = time.perf_counter()
        tiempos.append(fin - inicio)
        
    return sum(tiempos) / len(tiempos)

def ejecutar_codigo_personalizado(codigo_str, dataset):
    """
    Ejecuta un bloque de código Python proporcionado como string.
    El código debe esperar una variable 'n' o 'data'.
    """
    # Creamos un entorno local para la ejecución
    locales = {"data": dataset, "n": len(dataset) if isinstance(dataset, list) else dataset}
    
    inicio = time.perf_counter()
    exec(codigo_str, {}, locales)
    fin = time.perf_counter()
    
    return fin - inicio
