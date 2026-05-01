def bubble_sort(arr):
    n = len(arr)
    resultado = arr[:]
    for i in range(n):
        intercambiado = False
        for j in range(0, n - i - 1):
            if resultado[j] > resultado[j + 1]:
                resultado[j], resultado[j + 1] = resultado[j + 1], resultado[j]
                intercambiado = True
        if not intercambiado:
            break
    return resultado

def quick_sort(arr):
    resultado = arr[:]
    _quick_sort_recursivo(resultado, 0, len(resultado) - 1)
    return resultado

def _quick_sort_recursivo(arr, bajo, alto):
    if bajo < alto:
        pi = _particion(arr, bajo, alto)
        _quick_sort_recursivo(arr, bajo, pi - 1)
        _quick_sort_recursivo(arr, pi + 1, alto)

def _particion(arr, bajo, alto):
    pivote = arr[alto]
    i = bajo - 1
    for j in range(bajo, alto):
        if arr[j] < pivote:
            i += 1
            arr[i], arr[j] = arr[j], arr[i]
    arr[i + 1], arr[alto] = arr[alto], arr[i + 1]
    return i + 1

def merge_sort(arr):
    resultado = arr[:]
    if len(resultado) > 1:
        medio = len(resultado) // 2
        izq = resultado[:medio]
        der = resultado[medio:]

        izq = merge_sort(izq)
        der = merge_sort(der)

        i = j = k = 0

        while i < len(izq) and j < len(der):
            if izq[i] < der[j]:
                resultado[k] = izq[i]
                i += 1
            else:
                resultado[k] = der[j]
                j += 1
            k += 1

        while i < len(izq):
            resultado[k] = izq[i]
            i += 1
            k += 1

        while j < len(der):
            resultado[k] = der[j]
            j += 1
            k += 1
            
    return resultado

def insertion_sort(arr):
    resultado = arr[:]
    for i in range(1, len(resultado)):
        clave = resultado[i]
        j = i - 1
        while j >= 0 and clave < resultado[j]:
            resultado[j + 1] = resultado[j]
            j -= 1
        resultado[j + 1] = clave
    return resultado

def selection_sort(arr):
    resultado = arr[:]
    for i in range(len(resultado)):
        min_idx = i
        for j in range(i + 1, len(resultado)):
            if resultado[min_idx] > resultado[j]:
                min_idx = j
        resultado[i], resultado[min_idx] = resultado[min_idx], resultado[i]
    return resultado

def timsort_nativo(arr):
    # Usa la función sorted nativa de Python, que internamente usa Timsort
    return sorted(arr)

# --- Algoritmos de Búsqueda ---

def busqueda_lineal(arr, objetivo=None):
    """O(n) - Recorre todo el arreglo."""
    if objetivo is None: objetivo = -1 # Caso de búsqueda fallida para benchmark
    for i in range(len(arr)):
        if arr[i] == objetivo:
            return i
    return -1

def busqueda_binaria(arr_ordenado, objetivo=None):
    """O(log n) - Divide y vencerás. Requiere arreglo ordenado."""
    if objetivo is None: objetivo = -1
    bajo = 0
    alto = len(arr_ordenado) - 1
    while bajo <= alto:
        medio = (bajo + alto) // 2
        if arr_ordenado[medio] < objetivo:
            bajo = medio + 1
        elif arr_ordenado[medio] > objetivo:
            alto = medio - 1
        else:
            return medio
    return -1

# --- Ejemplos de Complejidad Exponencial vs Lineal ---

def fibonacci_recursivo(n):
    """O(2ⁿ) - Muy ineficiente para N grandes."""
    if isinstance(n, list): n = len(n) # Adaptador para el benchmarker
    if n <= 1:
        return n
    return fibonacci_recursivo(n-1) + fibonacci_recursivo(n-2)

def fibonacci_iterativo(n):
    """O(n) - Mucho más eficiente."""
    if isinstance(n, list): n = len(n)
    if n <= 1:
        return n
    a, b = 0, 1
    for _ in range(2, n + 1):
        a, b = b, a + b
    return b
