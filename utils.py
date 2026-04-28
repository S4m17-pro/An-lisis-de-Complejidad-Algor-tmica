import random

def generar_dataset(tamano):
    """
    Genera una lista de tamaño 'tamano' con números aleatorios.
    """
    return [random.randint(1, tamano * 10) for _ in range(tamano)]
