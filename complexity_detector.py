import numpy as np

def estimar_complejidad(tamanos, tiempos):
    """
    Estima la complejidad Big O ajustando los tiempos a curvas conocidas.
    Retorna el nombre de la complejidad estimada.
    """
    n = np.array(tamanos)
    y = np.array(tiempos)
    
    # Evitar divisiones por cero o logs de cero
    n = np.where(n == 0, 1e-9, n)
    
    modelos = {
        "O(1)": lambda x: np.ones_like(x),
        "O(log n)": lambda x: np.log2(x),
        "O(n)": lambda x: x,
        "O(n log n)": lambda x: x * np.log2(x),
        "O(n²)": lambda x: x**2,
        "O(n³)": lambda x: x**3,
        "O(2ⁿ)": lambda x: np.clip(2.0**np.clip(x, None, 100), 0, 1e308) # Evitar overflow
    }
    
    mejor_r2 = -float('inf')
    mejor_complejidad = "Indeterminada"
    
    for nombre, func in modelos.items():
        try:
            # Transformamos la función para hacer una regresión lineal y = c * f(n)
            # f_n es el valor de la complejidad teórica
            f_n = func(n)
            
            # Ajuste lineal simple: y = c * f_n
            # Usamos mínimos cuadrados para encontrar la constante 'c'
            # y = c * f_n  => c = sum(y * f_n) / sum(f_n^2)
            c = np.sum(y * f_n) / np.sum(f_n**2)
            prediccion = c * f_n
            
            # Calcular R^2
            ss_res = np.sum((y - prediccion)**2)
            ss_tot = np.sum((y - np.mean(y))**2)
            
            if ss_tot == 0: # Si todos los tiempos son iguales, es O(1)
                r2 = 1.0 if nombre == "O(1)" else 0.0
            else:
                r2 = 1 - (ss_res / ss_tot)
                
            if r2 > mejor_r2:
                mejor_r2 = r2
                mejor_complejidad = nombre
        except:
            continue
            
    return mejor_complejidad
