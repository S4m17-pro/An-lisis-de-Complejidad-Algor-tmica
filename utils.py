import random

def generar_dataset(tamano, caso="aleatorio"):
    """
    Genera una lista de tamaño 'tamano' según el caso especificado.
    casos soportados: 'aleatorio', 'ordenado', 'inverso'
    """
    dataset = [random.randint(1, tamano * 10) for _ in range(tamano)]
    if caso == "ordenado":
        dataset.sort()
    elif caso == "inverso":
        dataset.sort(reverse=True)
    return dataset
